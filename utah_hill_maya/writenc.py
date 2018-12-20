#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Write to NetCDF4 file with CF convention
"""

import numpy
import netCDF4
import time as pytime
from osgeo import osr
from readdata import Solution

# some simulation parameters
source_x = -12443619.
source_y = 4977641.
out_Lx = 400
out_Ly = 400
out_dx = 1.
out_dy = 1.
data_dir = "/home/pychuang/Sync/repos/clawpack-git/geoclaw/examples/landspill/utah_mount/_output"

x_raw = numpy.arange(source_x-out_Lx+out_dx/2., source_x+out_Lx, out_dx)
y_raw = numpy.arange(source_y-out_Ly+out_dy/2., source_y+out_Ly, out_dy)

# create a NC file and root group
rootgrp = netCDF4.Dataset("test.nc", mode="w", format="NETCDF4")

# set up dimension
ntime = rootgrp.createDimension("time", None)
nx = rootgrp.createDimension("x", x_raw.size)
ny = rootgrp.createDimension("y", y_raw.size)

# create variables
times = rootgrp.createVariable("time", numpy.float64, ("time",))
x = rootgrp.createVariable("x", numpy.float64, ("x",))
y = rootgrp.createVariable("y", numpy.float64, ("y",))
depth = rootgrp.createVariable(
    "depth", numpy.float64, ("time", "y", "x"),
    fill_value=-9999., zlib=True, complevel=9)
mercator = rootgrp.createVariable("mercator", 'S1')

# global attributes
rootgrp.title = "Utah-Dem-3"
rootgrp.institution = "The George Washington University"
rootgrp.source = "netCDF4 python module tutorial"
rootgrp.history = "Created " + pytime.ctime(pytime.time())
rootgrp.reference = ""
rootgrp.comment = ""
rootgrp.Conventions = "CF-1.7"

# variable attributes: time
times.units = "sec"
times.axis = "T"
times.long_name = "Simulation times"

# variable attributes: x
x.units = "m"
x.long_name = "X-coordinate in EPSG:3857 WGS 84"
x.standard_name = "projection_x_coordinate"

# variable attributes: y
y.units = "m"
y.long_name = "Y-coordinate in EPSG:3857 WGS 84"
y.standard_name = "projection_y_coordinate"

# variable attributes: topo
depth.units = "m"
depth.long_name = "Oil Depth"
depth.grid_mapping = "mercator"

# variable attributes: mercator
srs = osr.SpatialReference()
srs.ImportFromEPSG(3857)
mercator.grid_mapping_name = "mercator"
mercator.long_name = "CRS definition"
# mercator.longitude_of_prime_meridian = 0.
# mercator.semi_major_axis = 6378137.
# mercator.inverse_flattening = 298.257223563
mercator.spatial_ref = srs.ExportToWkt()
mercator.GeoTransform = "{} {} 0 {} 0 {}".format(
    source_x-out_Lx, out_dx, source_y+out_Ly, -out_dy)

# variable values
x[:] = x_raw
y[:] = y_raw

for frameno in range(0, 241):
    print("Frame No.", frameno)
    soln = Solution(data_dir, frameno)
    times[frameno] = soln.time
    depth[frameno, :, :] = soln.interpolate(x_raw, y_raw)

rootgrp.close()
