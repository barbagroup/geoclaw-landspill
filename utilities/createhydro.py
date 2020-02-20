#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
########################################################################################################################
# Copyright © 2019-2020 Pi-Yueh Chuang and Lorena A. Barba.
# All Rights Reserved.
#
# Contributors: Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Licensed under the BSD-3-Clause License (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at: https://opensource.org/licenses/BSD-3-Clause
#
# BSD-3-Clause License:
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#    following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
#    promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
########################################################################################################################

"""
Download and create hydrological files.
"""
import os
import sys


def obtain_NHD_geojson(extent):
    """Obtain features from NHD high resolution dataset MapServer

    Retrun:
        A list: [<flowline>, <area>, <water body>]. The data types are GeoJson.
    """
    import requests

    server = []

    # flowline
    server.append(
        "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/6/query")

    # area
    server.append(
        "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/8/query")

    # waterbody
    server.append(
        "https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer/10/query")

    query = []

    # flowline
    query.append({
        "where": "1=1", # in the future, use this to filter FCode(s)
        "f": "geojson",
        "geometry": "{},{},{},{}".format(extent[0], extent[1], extent[2], extent[3]),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "3857",
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "true",
        "outSR": "3857"
    })

    # area
    query.append({
        "where": "1=1", # in the future, use this to filter FCode(s)
        "f": "geojson",
        "geometry": "{},{},{},{}".format(extent[0], extent[1], extent[2], extent[3]),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "3857",
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "true",
        "outSR": "3857"
    })

    # waterbody
    query.append({
        "where": "1=1", # in the future, use this to filter FCode(s)
        "f": "geojson",
        "geometry": "{},{},{},{}".format(extent[0], extent[1], extent[2], extent[3]),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "3857",
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "true",
        "outSR": "3857"
    })

    geoms = []

    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(
        max_retries=requests.packages.urllib3.util.retry.Retry(
            total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])))

    for i, s in enumerate(server):
        response = session.get(s, stream=True, params=query[i])
        response.raise_for_status()
        geoms.append(response.json())

    session.close()

    return geoms

def convert_geojson_2_raster(feat_layers, filename, extent, res, crs=3857):
    """Convert a list of GeoTiff dict to raster (ESRI ASCII files)."""
    import numpy
    import rasterio
    import rasterio.features
    import rasterio.transform

    if crs != 3857:
        raise NotImplementedError("crs other than 3857 are not implemented yet")

    width = int((extent[2]-extent[0])/res+0.5)
    height = int((extent[3]-extent[1])/res+0.5)
    transform = rasterio.transform.from_origin(extent[0], extent[3], res, res)

    shapes = []
    for feat_layer in feat_layers:
        for g in feat_layer["features"]:
            if not rasterio.features.is_valid_geom(g["geometry"]):
                raise ValueError("Not a valid GeoJson gemoetry data")
            shapes.append((g["geometry"], 10))

    # if no geometry exists in the list
    if not shapes:
        image = numpy.ones((height, width), dtype=rasterio.float32) * -9999.
    # else if there's any geometry
    else:
        image = rasterio.features.rasterize(
            shapes=shapes, out_shape=(width, height), fill=-9999.,
            transform=transform, all_touched=True, dtype=rasterio.float32)

    # a workaround to ignore ERROR 4 message
    rasterio.open(
        os.path.abspath(filename), mode="w", driver="GTiff",
        width=1, height=1, count=1, crs=rasterio.crs.CRS.from_epsg(3857),
        transform=transform, dtype=rasterio.int8, nodata=0
    ).close()

    dst = rasterio.open(
        os.path.abspath(filename), mode="w", driver="AAIGrid",
        width=width, height=height, count=1,
        crs=rasterio.crs.CRS.from_epsg(crs), transform=transform,
        dtype=rasterio.float32, nodata=-9999.)

    dst.write(image, indexes=1)

    dst.close()

def check_download_hydro(casepath, rundata):
    """Check hydro file and download it if it does not exist."""

    if not rundata.landspill_data.hydro_features.files:
        return

    hydro_file = os.path.join(
        os.path.abspath(casepath), rundata.landspill_data.hydro_features.files[0])
    hydro_file = os.path.normpath(hydro_file)

    if not os.path.isfile(hydro_file):
        print("Hydro file {} not found. ".format(hydro_file) +
              "Download it now.", file=sys.stdout)

        ext = [rundata.clawdata.lower[0], rundata.clawdata.lower[1],
               rundata.clawdata.upper[0], rundata.clawdata.upper[1]]

        Nx = rundata.clawdata.num_cells[0]
        for i in range(rundata.amrdata.amr_levels_max-1):
            Nx *= rundata.amrdata.refinement_ratios_x[i]

        Ny = rundata.clawdata.num_cells[1]
        for i in range(rundata.amrdata.amr_levels_max-1):
            Ny *= rundata.amrdata.refinement_ratios_y[i]

        res = min((ext[2]-ext[0])/Nx, (ext[3]-ext[1])/Ny)

        # make the extent of the hydro file a little bit larger than comp. domain
        ext[0] -= res
        ext[1] -= res
        ext[2] += res
        ext[3] += res

        if not os.path.isdir(os.path.dirname(hydro_file)):
            os.makedirs(os.path.dirname(hydro_file))

        print("Obtaining GeoJson from NHD high resolution dataset server.", file=sys.stdout)
        feats = obtain_NHD_geojson(ext)

        print("Write GeoJson data to raster file {}".format(hydro_file), file=sys.stdout)
        convert_geojson_2_raster(feats, hydro_file, ext, res)

        print("Done writing to {}".format(hydro_file), file=sys.stdout)

# if running this script, then it's a test
if __name__ == "__main__":

    center = [-11483354.366326567, 3727793.1138695683]
    geoms = obtain_NHD_geojson([
        center[0]-1000., center[1]-1000., center[0]+1000., center[1]+1000.])

    import pprint
    pprint.pprint(geoms)
