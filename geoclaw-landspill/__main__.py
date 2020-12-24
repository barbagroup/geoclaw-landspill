#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""Main function of geoclaw-landspill.
"""
import pathlib
import argparse
import subprocess
import gclandspill
from gclandspill._create_data import create_data


def main():
    """Main function of geoclaw-landspill."""

    # CMD parser
    parser = argparse.ArgumentParser(
        description="Hydrocarbon overland spill solver based on GeoClaw.",
        epilog="GitHub page: https://github.com/barbagroup/geoclaw-landspill"
    )

    # path to the case directory
    parser.add_argument(
        "case", action="store", type=pathlib.Path, metavar="CASE_PATH",
        help="The path to the target case directory."
    )

    # parse the cmd
    args = parser.parse_args()

    # process path
    args.case = args.case.expanduser().resolve()
    assert args.case.is_dir()

    # the output folder of simulation results of this run
    args.output = args.case.joinpath("_output")

    # create *.data files, topology files, and hydrological file
    create_data(args.case, args.output)

    # get the Fortran solver binary
    solver = pathlib.Path(gclandspill.__file__).parents[1].joinpath("bin", "geoclaw-landspill-bin")

    if not solver.is_file():
        raise FileNotFoundError("Couldn't find solver at {}".format(solver))

    # execute the solver
    result = subprocess.run(solver, capture_output=False, cwd=str(args.output), check=True)

    return result.returncode


if __name__ == "__main__":
    import sys
    sys.exit(main())
