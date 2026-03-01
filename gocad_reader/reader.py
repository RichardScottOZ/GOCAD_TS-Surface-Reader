"""Core functions for reading and inspecting GOCAD TS surface files."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Tuple

import numpy as np


def read_gocad_ts(tsfile: str) -> Tuple[np.ndarray, np.ndarray]:
    """Read vertices and triangles from a GOCAD TS file.

    Parameters
    ----------
    tsfile : str
        Path to the GOCAD ``.ts`` file.

    Returns
    -------
    vrtx : np.ndarray
        Array of shape ``(N, 3)`` with vertex X, Y, Z coordinates (float64).
    trgl : np.ndarray
        Array of shape ``(M, 3)`` with triangle vertex indices (int64).

    Raises
    ------
    FileNotFoundError
        If *tsfile* does not exist.
    ValueError
        If the file contains no vertices or no triangles.
    """
    if not os.path.isfile(tsfile):
        raise FileNotFoundError(f"GOCAD TS file not found: {tsfile}")

    vrtx: List[np.ndarray] = []
    trgl: List[np.ndarray] = []

    with open(tsfile, "r") as fid:
        for line in fid:
            line_stripped = line.strip()

            if line_stripped.startswith("PVRTX") or line_stripped.startswith("VRTX"):
                parts = line_stripped.split()
                temp = np.array(parts[2:5], dtype=np.float64)
                vrtx.append(temp)

            elif line_stripped.startswith("ATOM"):
                parts = line_stripped.split()
                vertex_id_atom = int(parts[2])
                vrtx.append(vrtx[vertex_id_atom - 1])

            elif line_stripped.startswith("TRGL"):
                parts = line_stripped.split()
                temp = np.array(parts[1:4], dtype=np.int64)
                trgl.append(temp)

    if not vrtx:
        raise ValueError(f"No vertices found in {tsfile}")
    if not trgl:
        raise ValueError(f"No triangles found in {tsfile}")

    return np.asarray(vrtx, dtype=np.float64), np.asarray(trgl, dtype=np.int64)


def check_gocad_ts(tsfile: str) -> Dict[str, Any]:
    """Extract metadata and element counts from a GOCAD TS file.

    Parameters
    ----------
    tsfile : str
        Path to the GOCAD ``.ts`` file.

    Returns
    -------
    dict
        Dictionary with keys such as ``SURFACE``, ``NAME``, ``COORD``,
        ``TFACE``, ``PVRTX``, ``VRTX``, ``TRGL``, ``ATOM``, ``CRS``,
        and ``COLOR``.

    Raises
    ------
    FileNotFoundError
        If *tsfile* does not exist.
    """
    if not os.path.isfile(tsfile):
        raise FileNotFoundError(f"GOCAD TS file not found: {tsfile}")

    surface_name = os.path.basename(tsfile)

    crs_dict: Dict[str, Any] = {
        "NAME": None,
        "AXIS_NAME": None,
        "AXIS_UNIT": None,
        "ZPOSITIVE": None,
    }
    check_dist: Dict[str, Any] = {
        "SURFACE": surface_name,
        "NAME": None,
        "COORD": 0,
        "TFACE": 0,
        "PVRTX": 0,
        "VRTX": 0,
        "TRGL": 0,
        "ATOM": 0,
        "CRS": crs_dict,
        "COLOR": None,
    }

    # Temporary holders – may remain ``None`` if not present in the file.
    crs: str | None = None
    axis_name: List[str] | None = None
    axis_unit: List[str] | None = None
    zpositive: str | None = None

    with open(tsfile, "r") as fid:
        for line in fid:
            # --- Header metadata ---
            if "color:" in line:
                strcolor = line.split(":")
                tricolor = strcolor[1].split()
                if len(tricolor) >= 3:
                    check_dist["COLOR"] = [
                        float(tricolor[0]),
                        float(tricolor[1]),
                        float(tricolor[2]),
                    ]

            if "name:" in line:
                strname = line.split(":")
                check_dist["NAME"] = strname[1].strip()

            if "NAME " in line and "AXIS" not in line:
                parts = line.split()
                if len(parts) >= 2:
                    crs = parts[1].strip()

            if "AXIS_NAME" in line:
                axis_name = line.split()
                # Remove trailing empty elements
                axis_name = [a for a in axis_name if a]

            if "AXIS_UNIT" in line:
                axis_unit = line.split()
                axis_unit = [a for a in axis_unit if a]

            if "ZPOSITIVE" in line:
                parts = line.split()
                if len(parts) >= 2:
                    zpositive = parts[1].strip()

            if "END_ORIGINAL_COORDINATE" in line:
                crs_dict["NAME"] = crs
                crs_dict["AXIS_NAME"] = axis_name
                crs_dict["AXIS_UNIT"] = axis_unit
                crs_dict["ZPOSITIVE"] = zpositive

            # --- Element counters ---
            if "TFACE" in line:
                check_dist["TFACE"] += 1
            if "COORDINATE_SYSTEM" in line:
                check_dist["COORD"] += 1
            if line.strip().startswith("ATOM"):
                check_dist["ATOM"] += 1
            if line.strip().startswith("PVRTX"):
                check_dist["PVRTX"] += 1
            if line.strip().startswith("VRTX"):
                check_dist["VRTX"] += 1
            if line.strip().startswith("TRGL"):
                check_dist["TRGL"] += 1

    return check_dist
