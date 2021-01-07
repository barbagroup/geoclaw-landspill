#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""Functions related to plotting runtime topography with matplotlib."""
import os
import copy
import pathlib
import argparse
import multiprocessing
from typing import Tuple

import rasterio
import rasterio.plot
import matplotlib.pyplot
import matplotlib.axes
import matplotlib.colors
import matplotlib.cm
from gclandspill import pyclaw
from gclandspill import _misc
from gclandspill import _postprocessing


def plot_topo(args: argparse.Namespace):
    """Plot runtime topography on AMR grids with Matplotlib.

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

    # process level, frame_ed, dry_tol, and topofiles
    args = _misc.extract_info_from_setrun(args)

    # process args.soln_dir
    args.soln_dir = _misc.process_path(args.soln_dir, args.case, "_output")
    _misc.check_folder(args.soln_dir)

    # process args.dest_dir
    args.dest_dir = _misc.process_path(args.dest_dir, args.case, "_plots/topo")
    os.makedirs(args.dest_dir, exist_ok=True)  # make sure the folder exists

    # process args.extent
    if args.extent is None:  # get the minimum extent convering the solutions at all frames
        args.extent = _postprocessing.calc.get_soln_extent(
            args.soln_dir, args.frame_bg, args.frame_ed, args.level)

    lims = _postprocessing.calc.get_topo_lims(args.topofiles, extent=args.extent)

    # process cmax and cmin
    args.cmin = lims[0] if args.cmin is None else args.cmin
    args.cmax = lims[1] if args.cmax is None else args.cmax

    # prepare args for child processes (also initialize for the first proc)
    per_proc = (args.frame_ed - args.frame_bg) // args.nprocs  # number of frames per porcess
    child_args = [copy.deepcopy(args)]
    child_args[0].frame_bg = args.frame_bg
    child_args[0].frame_ed = args.frame_bg + per_proc

    # the first process has to do more jobs ...
    child_args[0].frame_ed += (args.frame_ed - args.frame_bg) % args.nprocs

    # remaining processes
    for _ in range(args.nprocs-1):
        child_args.append(copy.deepcopy(args))
        child_args[-1].frame_bg = child_args[-2].frame_ed
        child_args[-1].frame_ed = child_args[-1].frame_bg + per_proc

    # plot
    print("Spawning plotting tasks to {} processes: ".format(args.nprocs))
    with multiprocessing.Pool(args.nprocs, lambda: print("PID {}".format(os.getpid()))) as pool:
        pool.map(plot_aux_frames, child_args)

    return 0


def plot_aux_frames(args: argparse.Namespace):
    """Plot aux frames.

    Currently, this function is supposed to be called by `plot_depth` with multiprocessing.

    Argumenst
    ---------
    args : argparse.Namespace
        CMD argument parsed by `argparse`.

    Returns
    -------
    Execution code. 0 for success.
    """

    # plot
    fig, axes = matplotlib.pyplot.subplots(1, 2, gridspec_kw={"width_ratios": [10, 1]})

    for fno in range(args.frame_bg, args.frame_ed):

        print("Processing frame {} by PID {}".format(fno, os.getpid()))

        aux = args.soln_dir.joinpath("fort.a"+"{}".format(fno).zfill(4)).is_file()

        # no aux data for this frame
        if not aux:
            continue

        # read in solution data
        soln = pyclaw.Solution()
        soln.read(fno, str(args.soln_dir), file_format="binary", read_aux=True)

        axes[0], imgs, cmap, cmscale = plot_aux_frame_on_ax(
            axes[0], soln, [args.cmin, args.cmax], args.level, cmap=args.cmap, border=args.border)

        axes[0].set_xlim(args.extent[0], args.extent[2])
        axes[0].set_ylim(args.extent[1], args.extent[3])

        # topography colorbar
        fig.colorbar(matplotlib.cm.ScalarMappable(cmscale, cmap), cax=axes[1])

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


def plot_aux_frame_on_ax(
    axes: matplotlib.axes.Axes,
    soln: pyclaw.Solution,
    clims: Tuple[float, float],
    max_lv: int,
    **kwargs: str
):
    """Plot solution patch-by-patch to an existing Axes object.

    Arguments
    ---------
    axes : matplotlib.axes.Axes
        The target Axes target.
    soln : pyclaw.Solution
        Solution object from simulation.
    clims : [float, float]
        Min and max colormap limits.
    max_lv: int
        Maximum level of AMR grid.
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

        p = state.patch  # pylint: disable=invalid-name

        if p.level > max_lv:  # skip AMR level greater than sprcified level
            continue

        affine = rasterio.transform.from_origin(
            p.lower_global[0], p.upper_global[1], p.delta[0], p.delta[1])

        dst = state.aux[0].T[::-1, :]
        imgs.append(axes.imshow(
            dst, cmap=cmap, extent=rasterio.plot.plotting_extent(dst, affine), norm=cmscale,
        ))

        # boarder line
        stl = {"color": matplotlib.cm.get_cmap("Greys")(p.level/max_lv), "lw": 1, "alpha": 0.7}
        if "border" in kwargs and kwargs["border"]:
            imgs.append(axes.hlines(p.lower_global[1], p.lower_global[0], p.upper_global[0], **stl))
            imgs.append(axes.hlines(p.upper_global[1], p.lower_global[0], p.upper_global[0], **stl))
            imgs.append(axes.vlines(p.lower_global[0], p.lower_global[1], p.upper_global[1], **stl))
            imgs.append(axes.vlines(p.upper_global[0], p.lower_global[1], p.upper_global[1], **stl))

    return axes, imgs, cmap, cmscale
