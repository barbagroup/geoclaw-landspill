#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""Calculate total volumes to check mass conservation."""
import os
import argparse
import pathlib

from gclandspill import _misc
from gclandspill import _postprocessing


def create_volume_csv(args: argparse.Namespace):
    """Calculate total volumes to check mass conservation."""

    # process case path
    args.case = pathlib.Path(args.case).expanduser().resolve()
    _misc.check_folder(args.case)

    # case's setrun data
    rundata = _misc.import_setrun(args.case).setrun()

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
    args.dest_dir = _misc.process_path(args.dest_dir, args.case, args.soln_dir)
    os.makedirs(args.dest_dir, exist_ok=True)  # make sure the folder exists

    # process the NetCDF filename
    args.filename = _misc.process_path(args.filename, args.dest_dir, "volumes.csv")
    os.makedirs(args.filename.parent, exist_ok=True)  # make sure the parent folder exists

    # get volume data with shape (n_levels, n_frames)
    data = _postprocessing.calc.get_total_volume(
        args.soln_dir, args.frame_bg, args.frame_ed, rundata.amrdata.amr_levels_max)

    with open(args.filename, "w") as fileobj:
        line = "frame" + ",level {}" * rundata.amrdata.amr_levels_max + "\n"
        fileobj.write(line.format(*list(range(1, rundata.amrdata.amr_levels_max+1))))

        for ifno, fno in enumerate(range(args.frame_bg, args.frame_ed)):
            line = "{}" + ",{}" * rundata.amrdata.amr_levels_max + "\n"
            fileobj.write(line.format(fno, *data[ifno]))

    return 0
