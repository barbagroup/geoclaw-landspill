#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""Functions related to plotting with matplotlib."""
import os
import copy
import pathlib
import argparse
import multiprocessing
from typing import Sequence, Tuple

import numpy
import rasterio
import rasterio.plot
import matplotlib.pyplot
import matplotlib.axes
import matplotlib.colors
import matplotlib.cm
from gclandspill import pyclaw
from gclandspill import clawutil
from gclandspill import _misc
from gclandspill import _postprocessing


def plot_depth(args: argparse.Namespace):
    """Plot depth with Matplotlib.

    This function is called by the main function.

    Argumenst
    ---------
    args : argparse.Namespace
        CMD argument parsed by `argparse`.

    Returns
    -------
    Execution code. 0 for success.
    """

    # process nprocs
    args.nprocs = len(os.sched_getaffinity(0)) if args.nprocs is None else args.nprocs

    # process case path
    args.case = pathlib.Path(args.case).expanduser().resolve()
    _misc.check_folder(args.case)

    # case's setrun data
    rundata = _misc.import_setrun(args.case).setrun()

    # process target AMR level
    args.level = rundata.amrdata.amr_levels_max if args.level is None else args.level

    # process args.frame_ed
    if args.frame_ed is not None:
        args.frame_ed += 1  # plus 1 so can be used as the `end` in the `range` function
    elif rundata.clawdata.output_style == 1:  # if it's None, and the style is 1
        args.frame_ed = rundata.clawdata.num_output_times
        if rundata.clawdata.output_t0:
            args.frame_ed += 1
    elif rundata.clawdata.output_style == 2:  # if it's None, and the style is 2
        args.frame_ed = len(rundata.clawdata.output_times)
    elif rundata.clawdata.output_style == 3:  # if it's None, and the style is 3
        args.frame_ed = int(rundata.clawdata.total_steps / rundata.clawdata.output_step_interval)
        if rundata.clawdata.output_t0:
            args.frame_ed += 1

    # process args.soln_dir
    args.soln_dir = _misc.process_path(args.soln_dir, args.case, "_output")
    _misc.check_folder(args.soln_dir)

    # process args.dest_dir
    args.dest_dir = _misc.process_path(
        args.dest_dir, args.case, "_plots/level{:02d}".format(args.level))
    os.makedirs(args.dest_dir, exist_ok=True)  # make sure the folder exists

    # process args.extent
    if args.extent is None:  # get the minimum extent convering the solutions at all frames
        args.extent = _postprocessing.calc.get_soln_extent(
            args.soln_dir, args.frame_bg, args.frame_ed, args.level)

    # process args.dry_rol
    if args.dry_tol is None:  # get the dry tolerance from setrun.py
        args.dry_tol = rundata.geo_data.dry_tolerance

    # process the max of solution
    if args.cmax is None:
        args.cmax = _postprocessing.calc.get_soln_max(
            args.soln_dir, args.frame_bg, args.frame_ed, args.level)

    # prepare args for child processes (also initialize for the first proc)
    per_proc = (args.frame_ed - args.frame_bg) // args.nprocs  # number of frames per porcess
    child_args = [[copy.deepcopy(args), copy.deepcopy(rundata)]]
    child_args[0][0].frame_bg = args.frame_bg
    child_args[0][0].frame_ed = args.frame_bg + per_proc

    # the first process has to do more jobs ...
    child_args[0][0].frame_ed += (args.frame_ed - args.frame_bg) % args.nprocs

    # remaining processes
    for _ in range(args.nprocs-1):
        child_args.append([copy.deepcopy(args), copy.deepcopy(rundata)])
        child_args[-1][0].frame_bg = child_args[-2][0].frame_ed
        child_args[-1][0].frame_ed = child_args[-1][0].frame_bg + per_proc

    # plot
    print("Spawning plotting tasks to {} processes: ".format(args.nprocs))
    with multiprocessing.Pool(args.nprocs, lambda: print("PID {}".format(os.getpid()))) as pool:
        pool.starmap(plot_soln_frames, child_args)

    return 0


def plot_soln_frames(args: argparse.Namespace, rundata: clawutil.data.ClawRunData):
    """Plot solution frames.

    Currently, this function is supposed to be called by `plot_depth` with multiprocessing.

    Argumenst
    ---------
    args : argparse.Namespace
        CMD argument parsed by `argparse`.
    rundata : clawutil.data.ClawRunData
        The `ClawRunData` object holding simulation configuration.

    Returns
    -------
    Execution code. 0 for success.
    """

    # plot
    fig, axes = matplotlib.pyplot.subplots(1, 3, gridspec_kw={"width_ratios": [10, 1, 1]})

    axes[0], _, cmap_t, cmscale_t = plot_topo_on_ax(
        axes[0], rundata.topo_data.topofiles, args.colorize, extent=args.extent,
        degs=[args.topo_azdeg, args.topo_altdeg], clims=[args.topo_cmin, args.topo_cmax]
    )

    for fno in range(args.frame_bg, args.frame_ed):

        print("Processing frame {} by PID {}".format(fno, os.getpid()))

        # read in solution data
        soln = pyclaw.Solution()
        soln.read(
            fno, str(args.soln_dir), file_format="binary",
            read_aux=args.soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4)).is_file()
        )

        axes[0], imgs, cmap_s, cmscale_s = plot_soln_frame_on_ax(
            axes[0], soln, args.level, [args.cmin, args.cmax], args.dry_tol,
            cmap=args.cmap, border=args.border)

        axes[0].set_xlim(args.extent[0], args.extent[2])
        axes[0].set_ylim(args.extent[1], args.extent[3])

        # topography colorbar
        fig.colorbar(matplotlib.cm.ScalarMappable(cmscale_t, cmap_t), cax=axes[1])

        # solution depth colorbar
        fig.colorbar(matplotlib.cm.ScalarMappable(cmscale_s, cmap_s), cax=axes[2])

        fig.suptitle("T = {} sec".format(soln.state.t))  # title
        fig.savefig(args.dest_dir.joinpath("frame{:05d}.png".format(fno)))  # save

        # clear artists
        while True:
            try:
                img = imgs.pop()
                img.remove()
                del img
            except IndexError:
                break

    print("PID {} done processing frames {} - {}".format(os.getpid(), args.frame_bg, args.frame_ed))
    return 0


def plot_topo_on_ax(
    axes: matplotlib.axes.Axes,
    topo_files: Sequence[Tuple[int, os.PathLike]],
    colorize: bool = False,
    **kwargs: str
):
    """Add a topography elevation plot to an existing Axes object.

    Arguments
    ---------
    axes : matplotlib.axes.Axes
        The target Axes object.
    topo_files : tuple/lsit of sub-tuples/lists of [int, pathlike]
        A list of list following the topography files specification in GeoClaw's settings.
    colorize : bool
        Whether to use colorized colormap for the elevation. (default: False).
    **kwargs :
        Other possible keyword arguments:
        extent : [xmin, ymin, xmax, ymax]
            The extent of the topography. If not porvided, use the union of all provided topography
            files.
        degs : [azdeg, altdeg]
            The `azdeg` and `altdeg` for shading. See matplotlib's documentation regarding light
            sources. If not provided, use the default value of [45, 25].
        clims : [colormap min, colormap max]
            Customize the limits of the colormap. If not provided, use the full range.
        nodata : int
            Indicates the `nodata` values in the topography files. Default value is -9999.

    Returns
    -------
    axes : matplotlib.axes.Axes
        The updated Axes object.
    img : matplotlib.image.AxesImage
        The image object of the topography plot returned by matplotlib's `imshow`.
    cmap : matplotlib.colors.Colormap
        The colormap object used by the topography plot.
    cmscale : matplotlib.colors.Normalize
        The normalization object that maps elevation data to the the colormap valess.
    """

    # process optional keyword arguments
    extent = None if "extent" not in kwargs else kwargs["extent"]
    degs = [45, 25] if "degs" not in kwargs else kwargs["degs"]
    clims = None if "clims" not in kwargs else kwargs["clims"]
    nodata = -9999 if "nodata" not in kwargs else kwargs["nodata"]

    # use mosaic raster to obtain interpolated terrain
    rasters = []
    for topo in topo_files:
        if topo[0] != 3:
            raise _misc.WrongTopoFileError("Only accept type 3 topography file: {}".format(topo[0]))
        rasters.append(rasterio.open(topo[-1], "r"))

    # merge and interplate
    dst, affine = rasterio.merge.merge(rasters, extent)

    # close raster datasets
    for topo in rasters:
        topo.close()

    # convert to masked array
    dst = numpy.ma.array(dst[0], mask=(dst[0] == nodata))

    # update the limits based on elevation
    clims = [dst.min(), dst.max()] if clims is None else clims

    if colorize:  # use colorized colormap
        if numpy.all(dst >= 0.):  # colorbar: land-only
            cmap = matplotlib.colors.ListedColormap(
                matplotlib.cm.get_cmap("terrain")(numpy.linspace(0.25, 1, 256)))
            cmscale = matplotlib.colors.Normalize(*clims, False)
        else:  # mixture of land and ocean
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
                'cmap',
                numpy.concatenate(
                    (matplotlib.cm.get_cmap("terrain")(numpy.linspace(0, 0.17, 256)),
                     matplotlib.cm.get_cmap("terrain")(numpy.linspace(0.25, 1, 256))),
                    0
                )
            )
            cmscale = matplotlib.colors.TwoSlopeNorm(0., *clims)
    else:  # use gray scale
        cmap = matplotlib.cm.get_cmap("gray")
        cmscale = matplotlib.colors.Normalize(*clims, False)

    # shade has required rgb values, no need to provide cmap again
    img = axes.imshow(
        matplotlib.colors.LightSource(*degs).shade(
            dst, cmap, cmscale, vert_exag=5, fraction=1,
            dx=affine._scaling[0], dy=affine._scaling[1]  # pylint: disable=protected-access
        ),
        extent=rasterio.plot.plotting_extent(dst, affine), alpha=0.7
    )

    return axes, img, cmap, cmscale


def plot_soln_frame_on_ax(
    axes: matplotlib.axes.Axes,
    soln: pyclaw.Solution,
    level: int,
    clims: Tuple[float, float],
    dry_tol: float,
    **kwargs: str
):
    """Plot solution patch-by-patch to an existing Axes object.

    Arguments
    ---------
    axes : matplotlib.axes.Axes
        The target Axes target.
    soln : pyclaw.Solution
        Solution object from simulation.
    level : int
        Target AMR level.
    clims : [float, float]
        Min and max colormap limits.
    dry_tol : float
        Depth below this value will be cutoff and masked.
    **kwargs : keyword arguments
        Valid keyword arguments include:
        cmap : matplotlib.cm.Colormap
            Colormap to use. (Default: viridis)
        border : bool
            To draw border line for each patch.

    Returns
    -------
    axes : matplotlib.axes.Axes
        The updated Axes object.
    imgs : matplotlib.image.AxesImage
        Thes artist objects created by this function.
    cmap : matplotlib.colors.Colormap
        The colormap object used by the solutions.
    cmscale : matplotlib.colors.Normalize
        The normalization object that maps solution data to the the colormap values.
    """

    # process optional keyword arguments
    cmap = "viridis" if "cmap" not in kwargs else kwargs["cmap"]

    # normalization object
    cmscale = matplotlib.colors.Normalize(*clims, False)

    imgs = []
    for state in soln.states:
        if state.patch.level != level:
            continue  # skip patches not on target level

        p = state.patch  # pylint: disable=invalid-name

        affine = rasterio.transform.from_origin(
            p.lower_global[0], p.upper_global[1], p.delta[0], p.delta[1])

        dst = state.q[0].T[::-1, :]
        dst = numpy.ma.array(dst, mask=(dst < dry_tol))
        imgs.append(axes.imshow(
            dst, cmap=cmap, extent=rasterio.plot.plotting_extent(dst, affine), norm=cmscale,
        ))

        # boarder line
        stl = {"color": "k", "lw": 1, "alpha": 0.7}
        if "border" in kwargs and kwargs["border"]:
            imgs.append(axes.hlines(p.lower_global[1], p.lower_global[0], p.upper_global[0], **stl))
            imgs.append(axes.hlines(p.upper_global[1], p.lower_global[0], p.upper_global[0], **stl))
            imgs.append(axes.vlines(p.lower_global[0], p.lower_global[1], p.upper_global[1], **stl))
            imgs.append(axes.vlines(p.upper_global[0], p.lower_global[1], p.upper_global[1], **stl))

    return axes, imgs, cmap, cmscale
