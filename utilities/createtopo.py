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
Create topography file for a case based on point coordinate and domain extent.
"""
import os
import sys
import time


def request_arcgis_token(
        username, password,
        token_server="https://www.arcgis.com/sharing/rest/generateToken",
        exp=5):
    """Request a token from ArcGIS token server

    Request a user token from ArcGIS. Only required when the source of elevation
    is chosen to be ESRI World Elevation.

    Return: a str, the token.
    """
    import requests

    # information that will post to token server to obtain a token
    token_applicant = {
        "f": "json",
        "username": username,
        "password": password,
        "client": "referer",
        "expiration": str(exp),
        "referer": "https://www.arcgis.com"
    }

    # request a token
    token_response = requests.post(token_server, token_applicant)

    # try to raise an error if the server does not return success signal
    token_response.raise_for_status()

    # if execution comes to this point, we've got the token from the server
    token = token_response.json()["token"]

    return token

def obtain_geotiff(extent, filename, res=1, source="3DEP", token=None):
    """Grab the GeoTiff file for the elevation of a region.

    The region is defined by the argument extent. extent is a list with 4
    floating point numbers. Its format is extent = [Xmin, Ymin, Xmax, Ymax].

    Available elevation sources are 3DEP and ESRI. If using ESRI data, then
    token must present. Token can be obtained from the function
    request_arcgis_token. If using 3DEP, then remember that 3DEP only has data
    for North America.

    Args:
        extent [in]: a list with format [Xmin, Ymin, Xmax, Ymax]
        filename [in]: output GeoTiff filename.
        res [in]: output resolution. Default: 1 meter.
        source [in]: either 3DEP or ESRI.
        token [in]: if using ESRI source, the token must be provided.
    """
    import requests

    # the REST endpoint of exportImage of the elevation server
    if source == "ESRI":
        dem_server = \
            "https://elevation.arcgis.com/arcgis/rest/services/" + \
            "WorldElevation/Terrain/ImageServer/exportImage"

        assert token is not None, \
            "Token cannot be None when using ESRI data source"

    elif source == "3DEP":
        dem_server = \
            "https://elevation.nationalmap.gov/arcgis/rest/services/" + \
            "3DEPElevation/ImageServer/exportImage"
    else:
        raise ValueError("Invalid elevation source: {}".format(source))

    # calculate number of cells
    Xsize = int((extent[2]-extent[0])/res+0.5)
    Ysize = int((extent[3]-extent[1])/res+0.5)

    # adjust North and East boundary to match Xsize and Ysize
    extent[2] = extent[0] + Xsize * res
    extent[3] = extent[1] + Ysize * res

    # parameters used to get response from the REST endpoint
    dem_query = {
        "f": "json",
        "bbox": "{},{},{},{}".format(extent[0], extent[1], extent[2], extent[3]),
        "size": "{},{}".format(Xsize, Ysize),
        "imageSR": "3857",
        "bboxSr": "3857",
        "format": "tiff",
        "pixelType": "F32",
        "noData": "-9999",
        "interpolation": "RSP_BilinearInterpolation",
    }

    # add token to parameters if using ESRI
    if source == "ESRI":
        dem_query["token"] = token
    else:
        dem_query["mosaicRule"] = \
            "{\"mosaicMethod\":\"esriMosaicAttribute\",\"sortField\":\"AcquisitionDate\"}"

    # create a HTTP session that can retry 5 times if 500, 502, 503, 504 happens
    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(
        max_retries=requests.packages.urllib3.util.retry.Retry(
            total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])))

    # use GET to get response
    dem_response = session.get(dem_server, stream=True, params=dem_query)

    # try to raise an error if the server does not return success signal
    dem_response.raise_for_status()

    # close the session
    session.close()

    # if execution comes to this point, we've got the GeoTiff from the server
    tif_url = dem_response.json()["href"]

    # download the GeoTiff file, retry unitl success or timeout
    count = 0
    while True:

        r = requests.get(tif_url, stream=True, allow_redirects=True)

        if r.status_code == requests.codes.ok:
            break

        time.sleep(3)
        count += 3
        if count > 300:
            r.raise_for_status()

    with open(os.path.abspath(filename), "wb") as f:
        f.write(r.content)

def geotiff_2_esri_ascii(in_file, out_file):
    """Convert a GeoTiff to an ESRI ASCII file."""
    import rasterio

    geotiff = rasterio.open(in_file, "r")

    # a workaround to ignore ERROR 4 message; we create a new Tiff and close it
    rasterio.open(
        os.path.abspath(out_file), mode="w", driver="GTiff",
        width=1, height=1, count=1, crs=rasterio.crs.CRS.from_epsg(3857),
        transform=geotiff.transform, dtype=rasterio.int8, nodata=0
    ).close()

    dst = rasterio.open(
        os.path.abspath(out_file), mode="w", driver="AAIGrid",
        width=geotiff.width, height=geotiff.height, count=geotiff.count,
        crs=rasterio.crs.CRS.from_epsg(3857),
        transform=geotiff.transform, dtype=rasterio.float32,
        nodata=geotiff.nodata)

    dst.write_band(1, geotiff.read(1))
    dst.close()

    geotiff.close()

def check_download_topo(casepath, rundata):
    """Check topo file and download it if it does not exist."""

    topo_file = os.path.join(
        os.path.abspath(casepath), rundata.topo_data.topofiles[0][-1])
    topo_file = os.path.normpath(topo_file)

    if not os.path.isfile(topo_file):
        print("Topo file {} not found. ".format(topo_file) +
              "Download it now.")

        ext = [rundata.clawdata.lower[0], rundata.clawdata.lower[1],
               rundata.clawdata.upper[0], rundata.clawdata.upper[1]]

        Nx = rundata.clawdata.num_cells[0]
        for i in range(rundata.amrdata.amr_levels_max-1):
            Nx *= rundata.amrdata.refinement_ratios_x[i]

        Ny = rundata.clawdata.num_cells[1]
        for i in range(rundata.amrdata.amr_levels_max-1):
            Ny *= rundata.amrdata.refinement_ratios_y[i]

        res = min((ext[2]-ext[0])/Nx, (ext[3]-ext[1])/Ny)

        # make the extent of the topo file a little bit larger than comp. domain
        ext[0] -= res
        ext[1] -= res
        ext[2] += res
        ext[3] += res

        if not os.path.isdir(os.path.dirname(topo_file)):
            os.makedirs(os.path.dirname(topo_file))

        print("Downloading {}".format(topo_file+".tif"), file=sys.stdout)
        obtain_geotiff(ext, topo_file+".tif", res)
        print("Done downloading {}".format(topo_file+".tif"), file=sys.stdout)
        print("Converting to ESRI ASCII file", file=sys.stdout)
        geotiff_2_esri_ascii(topo_file+".tif", topo_file)
        print("Done converting to {}".format(topo_file), file=sys.stdout)
        os.remove(topo_file+".tif")
