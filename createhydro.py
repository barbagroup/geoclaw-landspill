#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Download and create hydrological files.
"""
import os
import requests


def obtain_NHD_geojson(extent):
    """Obtain features from NHD high resolution dataset MapServer

    Retrun:
        A list: [<flowline>, <area>, <water body>]. The data types are GeoJson.
    """

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
    for i, s in enumerate(server):
        response = requests.get(s, stream=True, params=query[i])
        response.raise_for_status()
        geoms.append(response.json())

    return geoms

def convert_geojson_2_raster(feat_layers, filename, extent, res, crs=3857):
    """Convert a list of GeoTiff dict to raster (ESRI ASCII files)."""
    import rasterio
    import rasterio.features
    import rasterio.transform

    if crs != 3857:
        raise NotImplementedError("crs other than 3857 are not implemented yet")

    width = int((extent[2]-extent[0])/res+0.5)
    height = int((extent[3]-extent[1])/res+0.5)
    transform = rasterio.transform.from_origin(extent[0], extent[3], res, res)

    dst = rasterio.open(
        os.path.abspath(filename), mode="w", driver="AAIGrid",
        width=width, height=height, count=1,
        crs=rasterio.crs.CRS.from_epsg(crs),
        transform=transform, dtype=rasterio.float32,
        nodata=-9999.)

    shapes = []
    for feat_layer in feat_layers:
        for g in feat_layer["features"]:
            if not rasterio.features.is_valid_geom(g["geometry"]):
                raise ValueError("Not a valid GeoJson gemoetry data")
            shapes.append((g["geometry"], 10))

    image = rasterio.features.rasterize(
        shapes=shapes, out_shape=(width, height), fill=-9999.,
        transform=transform, all_touched=True, dtype=rasterio.float32)

    dst.write(image, indexes=1)

    try:
        dst.close()
    except:
        pass

def check_download_hydro(casepath, rundata):
    """Check hydro file and download it if it does not exist."""

    if len(rundata.landspill_data.hydro_features.files) == 0:
        return

    hydro_file = os.path.join(
        os.path.abspath(casepath), rundata.landspill_data.hydro_features.files[0])
    hydro_file = os.path.normpath(hydro_file)

    if not os.path.isfile(hydro_file):
        print("Hydro file {} not found. ".format(hydro_file) +
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

        # make the extent of the hydro file a little bit larger than comp. domain
        ext[0] -= res
        ext[1] -= res
        ext[2] += res
        ext[3] += res

        if not os.path.isdir(os.path.dirname(hydro_file)):
            os.makedirs(os.path.dirname(hydro_file))

        print("Obtaining GeoJson from NHD high resolution dataset server.")
        feats = obtain_NHD_geojson(ext)

        print("Write GeoJson data to raster file {}".format(hydro_file))
        convert_geojson_2_raster(feats, hydro_file, ext, res)

        print("Done writing to {}".format(hydro_file))
