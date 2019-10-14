#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
########################################################################################################################
# Copyright © 2019 The George Washington University.
# All Rights Reserved.
#
# Contributors: Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Licensed under the BSD-3-Clause License (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at: https://opensource.org/licenses/BSD-3-Clause
#
# BSD-3-Clause License:
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#    following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
#    promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
########################################################################################################################

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
