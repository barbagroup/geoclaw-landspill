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

    # manually add a key `level` with value None, so we can get max AMR level from the next function
    args.level = None

    # process level, frame_ed, topofilee, and dry_tol
    args = _misc.extract_info_from_setrun(args)

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
    data = _postprocessing.calc.get_total_volume(args.soln_dir, args.frame_bg, args.frame_ed, args.level)

    with open(args.filename, "w") as fileobj:
        line = "frame" + ",level {}" * args.level + "\n"
        fileobj.write(line.format(*list(range(1, args.level+1))))

        for ifno, fno in enumerate(range(args.frame_bg, args.frame_ed)):
            line = "{}" + ",{}" * args.level + "\n"
            fileobj.write(line.format(fno, *data[ifno]))

    return 0
