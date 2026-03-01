"""Tests for gocad_reader package."""

from __future__ import annotations

import os
import tempfile
import textwrap

import numpy as np
import pytest

from gocad_reader import read_gocad_ts, check_gocad_ts


# ---------------------------------------------------------------------------
# Helpers – sample GOCAD TS content
# ---------------------------------------------------------------------------

MINIMAL_TS = textwrap.dedent("""\
    GOCAD TSurf 1
    HEADER {
    name:TestSurface
    }
    TFACE
    VRTX 1 0.0 0.0 0.0
    VRTX 2 1.0 0.0 0.0
    VRTX 3 0.0 1.0 0.0
    TRGL 1 2 3
    END
""")

TS_WITH_ATOMS = textwrap.dedent("""\
    GOCAD TSurf 1
    HEADER {
    name:AtomSurface
    }
    TFACE
    VRTX 1 10.0 20.0 30.0
    VRTX 2 11.0 21.0 31.0
    VRTX 3 12.0 22.0 32.0
    ATOM 4 1
    TRGL 1 2 3
    TRGL 2 3 4
    END
""")

TS_WITH_PVRTX = textwrap.dedent("""\
    GOCAD TSurf 1
    HEADER {
    name:PvrtxSurface
    }
    TFACE
    PVRTX 1 0.0 0.0 0.0 1.0
    PVRTX 2 1.0 0.0 0.0 2.0
    PVRTX 3 0.0 1.0 0.0 3.0
    TRGL 1 2 3
    END
""")

TS_WITH_METADATA = textwrap.dedent("""\
    GOCAD TSurf 1
    HEADER {
    name:MetaSurface
    *solid*color:0.5 0.6 0.7 1
    }
    COORDINATE_SYSTEM
    ORIGINAL_COORDINATE_SYSTEM
    NAME GDA94
    AXIS_NAME X Y Z
    AXIS_UNIT m m m
    ZPOSITIVE Elevation
    END_ORIGINAL_COORDINATE_SYSTEM
    TFACE
    VRTX 1 0.0 0.0 0.0
    VRTX 2 1.0 0.0 0.0
    VRTX 3 0.0 1.0 0.0
    TRGL 1 2 3
    END
""")


def _write_tmp(content: str) -> str:
    """Write *content* to a temporary ``.ts`` file and return the path."""
    fd, path = tempfile.mkstemp(suffix=".ts")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# Tests for read_gocad_ts
# ---------------------------------------------------------------------------

class TestReadGocadTs:
    def test_minimal_vertices(self):
        path = _write_tmp(MINIMAL_TS)
        try:
            vrtx, trgl = read_gocad_ts(path)
            assert vrtx.shape == (3, 3)
            np.testing.assert_array_almost_equal(
                vrtx, [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
            )
        finally:
            os.unlink(path)

    def test_minimal_triangles(self):
        path = _write_tmp(MINIMAL_TS)
        try:
            vrtx, trgl = read_gocad_ts(path)
            assert trgl.shape == (1, 3)
            np.testing.assert_array_equal(trgl, [[1, 2, 3]])
        finally:
            os.unlink(path)

    def test_dtypes(self):
        path = _write_tmp(MINIMAL_TS)
        try:
            vrtx, trgl = read_gocad_ts(path)
            assert vrtx.dtype == np.float64
            assert trgl.dtype == np.int64
        finally:
            os.unlink(path)

    def test_atoms_duplicate_vertex(self):
        path = _write_tmp(TS_WITH_ATOMS)
        try:
            vrtx, trgl = read_gocad_ts(path)
            assert vrtx.shape == (4, 3)
            # ATOM 4 references VRTX 1 → same coordinates
            np.testing.assert_array_equal(vrtx[3], vrtx[0])
            assert trgl.shape == (2, 3)
        finally:
            os.unlink(path)

    def test_pvrtx_support(self):
        path = _write_tmp(TS_WITH_PVRTX)
        try:
            vrtx, trgl = read_gocad_ts(path)
            assert vrtx.shape == (3, 3)
            np.testing.assert_array_almost_equal(
                vrtx, [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
            )
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            read_gocad_ts("/nonexistent/path/to/file.ts")

    def test_no_vertices_raises(self):
        content = "GOCAD TSurf 1\nTRGL 1 2 3\nEND\n"
        path = _write_tmp(content)
        try:
            with pytest.raises(ValueError, match="No vertices"):
                read_gocad_ts(path)
        finally:
            os.unlink(path)

    def test_no_triangles_raises(self):
        content = "GOCAD TSurf 1\nVRTX 1 0 0 0\nEND\n"
        path = _write_tmp(content)
        try:
            with pytest.raises(ValueError, match="No triangles"):
                read_gocad_ts(path)
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Tests for check_gocad_ts
# ---------------------------------------------------------------------------

class TestCheckGocadTs:
    def test_element_counts_minimal(self):
        path = _write_tmp(MINIMAL_TS)
        try:
            result = check_gocad_ts(path)
            assert result["VRTX"] == 3
            assert result["TRGL"] == 1
            assert result["ATOM"] == 0
            assert result["TFACE"] == 1
        finally:
            os.unlink(path)

    def test_name_extracted(self):
        path = _write_tmp(MINIMAL_TS)
        try:
            result = check_gocad_ts(path)
            assert result["NAME"] == "TestSurface"
        finally:
            os.unlink(path)

    def test_surface_uses_basename(self):
        path = _write_tmp(MINIMAL_TS)
        try:
            result = check_gocad_ts(path)
            assert result["SURFACE"] == os.path.basename(path)
        finally:
            os.unlink(path)

    def test_color_extracted(self):
        path = _write_tmp(TS_WITH_METADATA)
        try:
            result = check_gocad_ts(path)
            assert result["COLOR"] is not None
            assert len(result["COLOR"]) == 3
            assert result["COLOR"][0] == pytest.approx(0.5)
            assert result["COLOR"][1] == pytest.approx(0.6)
            assert result["COLOR"][2] == pytest.approx(0.7)
        finally:
            os.unlink(path)

    def test_crs_extracted(self):
        path = _write_tmp(TS_WITH_METADATA)
        try:
            result = check_gocad_ts(path)
            crs = result["CRS"]
            assert crs["NAME"] == "GDA94"
            assert crs["ZPOSITIVE"] == "Elevation"
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            check_gocad_ts("/nonexistent/path/to/file.ts")

    def test_atom_count(self):
        path = _write_tmp(TS_WITH_ATOMS)
        try:
            result = check_gocad_ts(path)
            assert result["ATOM"] == 1
        finally:
            os.unlink(path)

    def test_pvrtx_count(self):
        path = _write_tmp(TS_WITH_PVRTX)
        try:
            result = check_gocad_ts(path)
            assert result["PVRTX"] == 3
        finally:
            os.unlink(path)

    def test_coord_count(self):
        path = _write_tmp(TS_WITH_METADATA)
        try:
            result = check_gocad_ts(path)
            assert result["COORD"] >= 1
        finally:
            os.unlink(path)
