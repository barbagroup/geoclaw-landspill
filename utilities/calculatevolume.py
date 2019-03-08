#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Calculate total volume at each AMR level and at each output time.
"""
import os
import sys
import argparse
import numpy


def get_level_ncells_volumes(solution):
    """
    Get level-wise numbers of cells and fluid volumes.
    """
    from pphelper import get_max_AMR_level

    max_level = get_max_AMR_level(solution)

    ncells = numpy.zeros(max_level, dtype=numpy.int)
    volumes = numpy.zeros(max_level, dtype=numpy.float64)

    for state in solution.states:
        p = state.patch
        level = p.level

        ncells[level-1] += p.num_cells_global[0] * p.num_cells_global[1]
        volumes[level-1] += (numpy.sum(state.q[0, :, :]) * p.delta[0] * p.delta[1])

    return ncells, volumes

if __name__ == "__main__":

    # CMD argument parser
    parser = argparse.ArgumentParser(description="Calculate total volume.")

    parser.add_argument('case', metavar='case', type=str,
                        help='the name of the case')

    parser.add_argument(
        '--frame-bg', dest="frame_bg", action="store", type=int,
        help='customized start farme no. (default: 0)')

    parser.add_argument(
        '--frame-ed', dest="frame_ed", action="store", type=int,
        help='customized end farme no. (default: get from setrun.py)')

    # process arguments
    args = parser.parse_args()

    # get case path
    casepath = os.path.abspath(args.case)

    # get the abs path of the repo
    repopath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # check case dir
    if not os.path.isdir(casepath):
        print("Error: case folder {} does not exist.".format(casepath),
              file=sys.stderr)
        sys.exit(1)

    # check setup.py
    setrunpath = os.path.join(casepath, "setrun.py")
    if not os.path.isfile(setrunpath):
        print("Error: case folder {} does not have setrun.py.".format(casepath),
              file=sys.stderr)
        sys.exit(1)

    # check soln dir
    outputpath = os.path.join(casepath, "_output")
    if not os.path.isdir(outputpath):
        print("Error: output folder {} does not exist.".format(outputpath),
              file=sys.stderr)
        sys.exit(1)

    # path to clawpack
    claw_dir = os.path.join(repopath, "solver", "clawpack")

    # set CLAW environment variable to satisfy some Clawpack functions' need
    os.environ["CLAW"] = claw_dir

    # make clawpack searchable
    sys.path.insert(0, claw_dir)

    # import utilities
    from clawpack import pyclaw

    # load setup.py
    sys.path.insert(0, casepath) # add case folder to module search path
    import setrun # import the setrun.py

    rundata = setrun.setrun() # get ClawRunData object

    # number of frames
    if args.frame_ed is not None:
        frame_ed = args.frame_ed + 1
    elif rundata.clawdata.output_style == 1:
        frame_ed = rundata.clawdata.num_output_times
        if rundata.clawdata.output_t0:
            frame_ed += 1
    elif rundata.clawdata.output_style == 2:
        frame_ed = len(rundata.clawdata.output_times)
    elif rundata.clawdata.output_style == 3:
        frame_ed = int(rundata.clawdata.total_steps /
                       rundata.clawdata.output_step_interval)
        if rundata.clawdata.output_t0:
            frame_ed += 1

    # starting frame no.
    if args.frame_ed is not None:
        frame_bg = args.frame_bg
    else:
        frame_bg = 0

    data = numpy.zeros(
        (frame_ed-frame_bg, 1+rundata.amrdata.amr_levels_max), dtype=numpy.float64)

    for fno in range(frame_bg, frame_ed):
        # empty solution object
        soln = pyclaw.Solution()

        # path
        auxpath = os.path.join(outputpath, "fort.a"+"{}".format(fno).zfill(4))

        # read
        soln.read(
            fno, outputpath, file_format="binary",
            read_aux=os.path.isfile(auxpath))

        # calculate total volume at each grid level
        ncells, volumes = get_level_ncells_volumes(soln)

        data[fno-frame_bg, 0] = soln.state.t
        data[fno-frame_bg, 1:] = volumes[:]

        print("\tFrame No.{}, T={} secs: N Cells: {}; Fluid volume: {}".format(
            fno, soln.state.t, ncells, volumes))

    numpy.savetxt(os.path.join(casepath, "total_volume.csv"), data, delimiter=",")
