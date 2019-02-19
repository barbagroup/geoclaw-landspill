#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""Compile and build GeoClaw solver binary."""
import os
import sys
import subprocess
import textwrap


def test_env_variables(var):
    """Test environment variables"""

    varpath = os.getenv(var)
    if varpath is None:
        print("\nError: environment variable " +
              "{} not set.\n".format(var), file=sys.stderr)
        sys.exit(1)
    else:
        print("* Environment variable {} is set to {}.".format(var, varpath))

if __name__ == "__main__":

    # check environment variables
    print()
    test_env_variables("CLAW")
    test_env_variables("FC")
    test_env_variables("PYTHONPATH")
    print()

    # absolute path to this repository
    repo_path = os.path.dirname(os.path.abspath(__file__))

    # path to the folder that will hold topo and hydro files
    file_dir = os.path.join(repo_path, "common-files")

    # create a folder for topo and hydro files
    print("* Creating folder \"common-files\"", end="")
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)
        print(" -- done.")
    else:
        print(" -- already exists. Skip.")

    # create a folder for binary
    bin_dir = os.path.join(repo_path, "bin")
    print()
    print("* Creating folder \"bin\"", end="")
    if not os.path.isdir(bin_dir):
        os.mkdir(bin_dir)
        print(" -- done.")
    else:
        print(" -- already exists. Skip.")

    # generate binary
    print("* Generating binary executable of the solver", end="")
    sys.stdout.flush()
    job = subprocess.run(["make", "new"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        job.check_returncode()
    except subprocess.CalledProcessError:
        print(" -- FAILED!\n")
        print('\u250F' + '\u2501'*70 + '\u2513')
        print("\u2503" + " "*70 + "\u2503")
        print("\u2503 THE COMPILATION AND BUILDING JOB " +
              "FAILED DUE TO THE FOLLOWING REASON  \u2503")
        print("\u2503" + " "*70 + "\u2503")
        print('\u2523' + '\u2501'*70 + '\u252B')
        print("\u2503" + " "*70 + "\u2503")

        err = job.stderr.decode('UTF-8')
        err = textwrap.wrap(err, width=68)
        for e in err:
            if len(e) < 68:
                e = e + " " * (68-len(e))
            print("\u2503 " + e + " \u2503")
        print("\u2503" + " "*70 + "\u2503")
        print('\u2517' + '\u2501'*70 + '\u251B' + "\n")

        print("Setup failed and is exiting.", file=sys.stderr)
        sys.exit(1)
    except:
        raise
    else:
        print(" -- done.")

    # setup finished
    print("\nSetup done.\n")
