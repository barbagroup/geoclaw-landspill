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
from clawpack.clawutil import runclaw
import createtopo
import createhydro


def create_data(casepath):
    """Create *.data files (and topography & hydrological files) in case folder.

    Args:
        casepath [in]: a string indicating the abs path of case folder.
    """

    if not os.path.isdir(casepath):
        print("Error: case folder {} does not exist.".format(casepath),
              file=sys.stderr)
        sys.exit(1)

    setrunpath = os.path.join(casepath, "setrun.py")
    if not os.path.isfile(setrunpath):
        print("Error: case folder {} does not have setrun.py.".format(casepath),
              file=sys.stderr)
        sys.exit(1)


    pwd = os.getcwd() # get current working directory

    sys.path.insert(0, casepath) # add case folder to module search path
    import setrun # import the setrun.py

    os.chdir(casepath) # go to case folder

    rundata = setrun.setrun() # get ClawRunData object

    # check if topo file exists. Download it if not exist
    createtopo.check_download_topo(casepath, rundata)

    # check if hudro file exists. Download it if not exist
    createhydro.check_download_hydro(casepath, rundata)

    rundata.write() # write *.data to the case folder

    os.chdir(pwd) # go back to pwd


if __name__ == "__main__":

    # help message
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("Usage:")
        print("\tpython run.py case_folder_name")
        sys.exit(0)

    # get case path
    casepath = os.path.abspath(sys.argv[1])

    # get the abs path of the repo
    repopath = os.path.dirname(os.path.abspath(__file__))

    # create *.data files
    create_data(casepath)

    # run simulation
    runclaw.runclaw(
        xclawcmd=os.path.join(repopath, "bin/xgeoclaw"),
        outdir=os.path.join(casepath, "_output"),
        overwrite=False, restart=None, rundir=casepath, print_git_status=True,
        nohup=False, nice=None)
