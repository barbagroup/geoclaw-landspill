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


def create_data(casepath):
    """Create *.data files in case folder.

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

        print("Downloading {}".format(topo_file+".tif"))
        createtopo.obtain_geotiff(ext, topo_file+".tif", res)
        print("Done downloading {}".format(topo_file+".tif"))
        print("Converting to ESRI ASCII file")
        createtopo.geotiff_2_esri_ascii(topo_file+".tif", topo_file)
        print("Done converting to {}".format(topo_file))
        os.remove(topo_file+".tif")

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
