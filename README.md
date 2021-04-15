# GOCAD_TS-Surface-Reader
Script to retrieve the vertices and faces from a GOCAD TS file for use in python processing

## Overview

A GOCAD TS file contains 3-D information - what we are interested in is the vertices and faces.  The vertices contain the X, Y, Z locations and the faces how these triangles relate to each other.

## Data Format

There is a header that the check metadata function takes some information from.  Information (perhaps) on the Coordinate Reference System, the RGB colors in 0-1 RGB, the Z reference direction and others.

The data part of the files contains VRTX or PRTX lines that have the point information and TRGL lines that have the face information.  These have ascending integer IDs.

Also there can be ATOM lines which reference a previous point's VRTX - apparently to have a topologically distinct reference that shares the same location data - which doesn't matter if all you want is X, Y, Z, but needs handling.

## Information

http://paulbourke.net/dataformats/gocad/gocad.pdf

## Basics

Pass the TS file path to the read function.

## Notes

There may be other formatting varieties for TS files I am unfamiliar with, it was just written to handle this particular case.  Logic should be easily extensible.

## Others

Just found this: - https://www.opengeosys.org/docs/tools/fileio/gocadtsurfacereader/

## Thanks

This is all basically because of the idea from https://github.com/fourndo

https://programtalk.com/vs2/python/12012/simpeg/SimPEG/Utils/io_utils.py/

The GemGIS package uses the above: https://github.com/cgre-aachen/gemgis

Sample data source thanks to SARIG  https://sarigbasis.pir.sa.gov.au/WebtopEw/ws/samref/sarig1/cat0/Record?w=catno%3D2036881+OR+catno%3D2036883+OR+catno%3D2036887&sid=c2ca73f5685c43249e6c1ab5ec7dc2e5&set=1&m=3


