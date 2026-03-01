"""Backward-compatible wrapper.

The functions have moved into the ``gocad_reader`` package.
Import them from there for new code::

    from gocad_reader import read_gocad_ts, check_gocad_ts
"""

from gocad_reader import read_gocad_ts, check_gocad_ts  # noqa: F401

# Legacy aliases so existing code using the old names keeps working.
read_GOCAD_ts_test = read_gocad_ts
check_GOCAD_ts = check_gocad_ts
    
