#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""Post-processing functions calculating something with simulation solutions."""
import os
import pathlib
from typing import Optional, Tuple, Sequence

import rasterio
from gclandspill import pyclaw
from gclandspill import _misc


def get_soln_extent(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, level: int):
    """Get the bounding box of the results of all time frames at a specific AMR level.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    level : int
        The level of AMR to provess.

    Returns
    -------
    extent : tuple/list
        [xmin, ymin, xmax, ymax] (i.e., [west, south, east, north])
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()
    extent = [float("inf"), float("inf"), -float("inf"), -float("inf")]

    for fno in range(frame_bg, frame_ed):

        # aux and solution file of this time frame
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4))
        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=aux.is_file())

        # search through AMR grid patches in this solution
        for state in soln.states:
            if state.patch.level != level:
                continue

            extent[0] = min(extent[0], state.patch.lower_global[0])
            extent[1] = min(extent[1], state.patch.lower_global[1])
            extent[2] = max(extent[2], state.patch.upper_global[0])
            extent[3] = max(extent[3], state.patch.upper_global[1])

    return extent


def get_soln_res(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, level: int):
    """Get the resolution of the grid at a specific AMR level.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    level : int
        The level of AMR to provess.

    Returns
    -------
    dx, dy : float
        Cell size at x and y direction.
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()

    for fno in range(frame_bg, frame_ed):

        # aux and solution file of this time frame
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4))
        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=aux.is_file())

        # search through AMR grid patches, if found desired dx & dy at the level, quit
        for state in soln.states:
            if state.patch.level == level:
                return state.patch.delta

    raise _misc.AMRLevelError("No solutions has AMR level {}".format(level))


def get_soln_min(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, level: int):
    """Get the minimum depth of the results of all time frames at a specific AMR level.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    level : int
        The level of AMR to provess.

    Returns
    -------
    vmin : float
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()
    vmin = float("inf")

    for fno in range(frame_bg, frame_ed):

        # aux and solution file of this time frame
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4))
        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=aux.is_file())

        # search through AMR grid patches in this solution
        for state in soln.states:
            if state.patch.level != level:
                continue

            vmin = min(vmin, state.q[0].min())

    return vmin


def get_soln_max(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, level: int):
    """Get the maximum depth of the results of all time frames at a specific AMR level.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    level : int
        The level of AMR to provess.

    Returns
    -------
    vmax : float
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()
    vmax = - float("inf")

    for fno in range(frame_bg, frame_ed):

        # aux and solution file of this time frame
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4))
        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=aux.is_file())

        # search through AMR grid patches in this solution
        for state in soln.states:
            if state.patch.level != level:
                continue

            vmax = max(vmax, state.q[0].max())

    return vmax


def get_topo_min(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, level: int):
    """Get the minimum elevation during runtime among the time frames at a specific AMR level.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    level : int
        The level of AMR to provess.

    Returns
    -------
    vmin : float
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()
    vmin = float("inf")

    for fno in range(frame_bg, frame_ed):

        # aux and solution file of this time frame
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4)).is_file()

        if not aux:  # this time frame does not contain runtime topo data
            continue

        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=True)

        # search through AMR grid patches in this solution
        for state in soln.states:
            if state.patch.level != level:
                continue

            vmin = min(vmin, state.aux[0].min())

    if vmin == float("inf"):
        raise _misc.NoFrameDataError("No AUX found in frames {} to {}.".format(frame_bg, frame_ed))

    return vmin


def get_topo_max(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, level: int):
    """Get the maximum elevation during runtime among the time frames at a specific AMR level.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    level : int
        The level of AMR to provess.

    Returns
    -------
    vmax : float
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()
    vmax = - float("inf")

    for fno in range(frame_bg, frame_ed):

        # aux and solution file of this time frame
        aux = soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4)).is_file()

        if not aux:  # this time frame does not contain runtime topo data
            continue

        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=True)

        # search through AMR grid patches in this solution
        for state in soln.states:
            if state.patch.level != level:
                continue

            vmax = max(vmax, state.aux[0].max())

    if vmax == - float("inf"):
        raise _misc.NoFrameDataError("No AUX found in frames {} to {}.".format(frame_bg, frame_ed))

    return vmax


def get_topo_lims(topo_files: Sequence[os.PathLike], **kwargs):
    """Get the min and max elevation from a set of topography files.

    Arguments
    ---------
    topo_files : tuple/lsit of pathlike.PathLike
        A list of list following the topography files specification in GeoClaw's settings.
    **kwargs :
        Available keyword arguments are:
        extent : [float, float, float, float]
            The customize extent. The format is [west, south, east, north].

    Returns
    -------
    [min, max]
    """

    # process optional keyword arguments
    extent = None if "extent" not in kwargs else kwargs["extent"]

    # use mosaic raster to obtain interpolated terrain
    rasters = [rasterio.open(topo, "r") for topo in topo_files]

    # merge and interplate
    dst, _ = rasterio.merge.merge(rasters, extent)

    # close raster datasets
    for topo in rasters:
        topo.close()

    return dst[0].min(), dst[0].max()


def interpolate(
    soln: pyclaw.Solution,
    level: int,
    dry_tol: float,
    extent: Optional[Tuple[float, float, float, float]] = None,
    res: Optional[float] = None, nodata: int = -9999
):
    """Merge grid patches at a level and interpolate to a given extent with a given resolution.

    This interpolation relies on the concept of mosaic raster, so it has to read all patches at
    that level into memory and hence is memory intense.

    Arguments
    ---------
    soln : pyclaw.Solution
        The solution object from Clawpack.
    level : int
        The target level of AMR grid to be used.
    dry_tol : float
        A cutoff values so that all pixels having values smaller than it will have `nodata` value.
    extent : tuple/list of (xmin, ymin, xmas, ymax)
        The bounds of the outpur/interpolated domain.
    res : float
        The grid/raster resolution of the output domain. X and Y direction will have the same
        resolution.
    nodata : int
        The value indicating that a cell/pixel is masked.

    Returns
    -------
    dst : numpy.ndarray
        The interpolated data. The shape is (n_rows, n_cols). Also, the order of rows is that used
        by `pyplot.imshow`, not the one used by `pyplot.contour`.
    affine : rasterio.transform.Affine
        An affine object that can be passed to raster file writer. An affine object describes how to
        convert from images' row-col indices into real coordinates.
    """
    # pylint: disable=too-many-arguments

    # kwargs to be passed to in-memory rasters
    child_raster_props = {
        "driver": "GTiff", "count": 1, "dtype": float, "nodata": nodata,
        "crs": rasterio.crs.CRS.from_epsg(3857),
        "height": None, "width": None, "transform": None,
    }

    memfiles = []  # backend memory files
    child_rasters = []  # container to hold opened in-memory rasters

    for state in soln.states:
        if state.patch.level != level:
            continue  # skip patches not on target level

        child_raster_props["transform"] = rasterio.transform.from_origin(
            state.patch.lower_global[0], state.patch.upper_global[1],
            state.patch.delta[0], state.patch.delta[1]
        )
        child_raster_props["height"] = state.patch.num_cells_global[1]
        child_raster_props["width"] = state.patch.num_cells_global[0]

        memfiles.append(rasterio.io.MemoryFile())
        child_rasters.append(memfiles[-1].open(**child_raster_props))
        child_rasters[-1].write(state.q[0].T[::-1, :], 1)

    try:
        # make a mosaic raster and interpolate to output domain
        dst, affine = rasterio.merge.merge(
            datasets=child_rasters, bounds=extent, res=res, nodata=nodata, precision=15,
            resampling=rasterio.enums.Resampling.cubic_spline)
    except IndexError as err:
        if str(err) == "list index out of range":  # not wer cells
            raise _misc.NoWetCellError("All grid patches have only dry cells.") from err
        raise  # other unknown errors

    # filter out dry cells
    dst[dst < dry_tol] = nodata

    # close dataset/clear memory
    for memfile, raster in zip(memfiles, child_rasters):
        raster.close()
        memfile.close()

    return dst[0], affine


def get_total_volume(soln_dir: os.PathLike, frame_bg: int, frame_ed: int, n_levels: int):
    """Get total volumes at AMR levels.

    Arguments
    ---------
    soln_dir : pathlike
        Path to where the solution files are.
    frame_bg, frame_ed : int
        Begining and end frame numbers.
    n_levels : int
        Total number of AMR levels.

    Returns
    -------
    A list of of shape (n_frames, n_levels).
    """

    soln_dir = pathlib.Path(soln_dir).expanduser().resolve()

    ans = [[0. for _ in range(n_levels)] for _ in range(frame_bg, frame_ed)]

    for ifno, fno in enumerate(range(frame_bg, frame_ed)):

        # solution file of this time frame
        soln = pyclaw.Solution()
        soln.read(fno, str(soln_dir), file_format="binary", read_aux=False)

        # search through AMR grid patches, if found desired dx & dy at the level, quit
        for state in soln.states:
            p = state.patch  # pylint: disable=invalid-name
            ans[ifno][p.level-1] += (state.q[0].sum() * p.delta[0] * p.delta[1])

    return ans
