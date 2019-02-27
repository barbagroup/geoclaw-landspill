#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""
Run xgeoclaw solver with a given case.
"""
import os
import sys


def create_data(casepath):
    """Create *.data files (and topography & hydrological files) in case folder.

    Args:
        casepath [in]: a string indicating the abs path of case folder.
    """
    import createtopo
    import createhydro

    if not os.path.isdir(casepath):
        print("Error: case folder {} does not exist.".format(casepath),
              file=sys.stderr)
        sys.exit(1)

    setrunpath = os.path.join(casepath, "setrun.py")
    if not os.path.isfile(setrunpath):
        print("Error: case folder {} does not have setrun.py.".format(casepath),
              file=sys.stderr)
        sys.exit(1)

    sys.path.insert(0, casepath) # add case folder to module search path
    import setrun # import the setrun.py

    pwd = os.getcwd() # get current working directory
    os.chdir(casepath) # go to case folder
    rundata = setrun.setrun() # get ClawRunData object
    rundata.write() # write *.data to the case folder
    os.chdir(pwd) # go back to pwd

    # check if topo file exists. Download it if not exist
    createtopo.check_download_topo(casepath, rundata)

    # check if hudro file exists. Download it if not exist
    createhydro.check_download_hydro(casepath, rundata)

if __name__ == "__main__":

    # help message
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("Usage:")
        print("\tpython run.py case_folder_name")
        sys.exit(0)

    # paths
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    claw_dir = os.path.join(repo_dir, "solver", "clawpack")
    case_dir = os.path.abspath(sys.argv[1])
    solver = os.path.join(repo_dir, "solver", "bin", "xgeoclaw")

    # set CLAW environment variable to satisfy some Clawpack functions' need
    os.environ["CLAW"] = claw_dir

    # make clawpack searchable
    sys.path.insert(0, claw_dir)
    from clawpack.clawutil import runclaw

    # create *.data files
    create_data(case_dir)

    # run simulation
    runclaw.runclaw(
        xclawcmd=solver, outdir=os.path.join(case_dir, "_output"),
        overwrite=False, restart=None, rundir=case_dir, print_git_status=True,
        nohup=False, nice=None)
