#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018-2019 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

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

def untar_and_rename(src, dst, rename=None):
    """Extract a tarball and rename it."""
    import tarfile

    src = os.path.abspath(os.path.normpath(src))
    dst = os.path.abspath(os.path.normpath(dst))

    if rename is not None:
        rename = os.path.join(dst, rename)

        if os.path.exists(rename):
            raise FileExistsError("Folder {} already exists. ".format(rename))

    with tarfile.open(src, "r") as f:
        # get the top-level deirctory name in the tarball
        top_level = os.path.commonpath(f.getnames())
        top_level = os.path.join(dst, top_level)

        # check if the folder already exists, and whether to overwrite that
        if os.path.exists(top_level):
            raise FileExistsError("Folder {} already exists. ".format(rename))

        # extract to dst/top_level
        f.extractall(dst)

    # rename the folder
    if rename is not None:
        os.rename(top_level, rename)

def download_submodules():
    """Download submodules' tarballs.

    This function is called when this repository is downloaded as an archive and
    so no git information available. If this repository is downloaded by git
    clone, then this function should not be used.
    """
    import requests

    print("\n* Not a Git repository, will download arhcives.")

    repo_dir = os.path.dirname(os.path.abspath(__file__))
    solver_path = os.path.join(repo_dir, "solver")

    # delete the empty clawpack directory
    try:
        os.rmdir(os.path.join(solver_path, "clawpack"))
    except FileNotFoundError:
        pass

    # delete the empty geoclaw directory
    try:
        os.rmdir(os.path.join(solver_path, "geoclaw-landspill"))
    except FileNotFoundError:
        pass

    # download clawpack v5.5.0 tarball
    print("* Downloading Clawpack", end="")
    response = requests.get(
        "https://github.com/clawpack/clawpack/files/2330639/clawpack-v5.5.0.tar.gz",
        headers={"Accept": "application/vnd.github.v3+json"})
    response.raise_for_status()

    # write the clawpack tarball to local drive
    claw_tarball = os.path.join(solver_path, "clawpack.tar.gz")
    with open(claw_tarball, "wb") as f:
        f.write(response.content)
    print(" -- done.")

    # untar clawpack tarball and rename
    print("* Decompress Clawpack tarbal", end="")
    untar_and_rename(claw_tarball, solver_path, "clawpack")
    os.remove(claw_tarball)
    print(" -- done.")

    # download tarball for latest geoclaw-landspill
    print("* Downloading GeoClaw-Landspill", end="")
    response = requests.get(
        "https://api.github.com/repos/barbagroup/geoclaw/pulls/17",
        headers={"Accept": "application/vnd.github.v3+json"})
    response.raise_for_status()

    tar_url = response.json()["archive_url"]
    tar_url = tar_url.replace("{/ref}", "").format(archive_format="tarball")

    response = requests.get(
        tar_url, headers={"Accept": "application/vnd.github.v3+json"})
    response.raise_for_status()

    # write the geoclaw-landspill tarball to local drive
    geo_tarball = os.path.join(solver_path, "geoclaw.tar.gz")
    with open(geo_tarball, "wb") as f:
        f.write(response.content)
    print(" -- done.")

    # untar geoclaw-landspill tarball and rename
    print("* Decompress GeoClaw-Landspill tarbal", end="")
    untar_and_rename(geo_tarball, solver_path, "geoclaw-landspill")
    os.remove(geo_tarball)
    print(" -- done.")

def init_git_submodules():
    """If this is a development version, use git submodule."""
    import shutil

    # absolute path to this repository
    repo_path = os.path.dirname(os.path.abspath(__file__))

    # get git executable
    git = shutil.which("git")

    # test if git exists
    assert git is not None, "Can not find git command."

    # change working directory in case this script is launched at other location
    pwd = os.getcwd()
    os.chdir(repo_path)

    print("\n* This is a development version. Initializing submodules", end="")
    # run git submodule update --init --recursive
    job = subprocess.run(
        [git, "submodule", "update", "--init", "--recursive"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        job.check_returncode()
    except subprocess.CalledProcessError:
        print(" -- FAILED!\n")
        err = job.stderr.decode('UTF-8')
        err = textwrap.wrap(err, width=68)
        print("\n{}".format(err))
        print("\nSetup failed and is exiting.", file=sys.stderr)
        sys.exit(1)
    else:
        print(" -- done.")

    # go back to original location
    os.chdir(pwd)

def setup_clawpack():
    """Bypass clawpack's setup and use our own to include our GeoClaw."""
    from solver.clawpack import setup as claw_setup

    repo_dir = os.path.dirname(os.path.abspath(__file__))
    solver_path = os.path.join(repo_dir, "solver")
    clawpack_path = os.path.join(solver_path, "clawpack")
    geo_path = os.path.join(solver_path, "geoclaw-landspill")
    subpackages = claw_setup.SUBPACKAGES

    print("\n* Setting up Python package of Clawpack", end="")

    # delete geoclaw info from clawpack subpackage list
    del subpackages["geoclaw"]

    # delete forestclaw from symlink because this cause Clawpack dirty
    del subpackages["pyclaw"]["python_src_dir"][2]

    # setup soft links, excluding GeoClaw
    pwd = os.path.abspath(os.getcwd())
    os.chdir(clawpack_path)
    claw_setup.make_symlinks(subpackages)
    os.chdir(pwd)

    # setup soft link for geoclaw-landspill
    claw_setup.symlink(
        os.path.join(geo_path, "src", "python", "geoclaw"),
        os.path.join(repo_dir, "solver", "clawpack", "clawpack", "geoclaw"))
    print(" -- done.")

def make_geoclaw_bin():
    """Compile and build the binary executable for GeoClaw-Landspill."""

    # absolute path to this repository
    repo_path = os.path.dirname(os.path.abspath(__file__))

    # absolute path to the makefile
    makefile_path = os.path.join(repo_path, "solver", "Makefile")

    print("\n* Compiling and building the solver.")

    # create a folder for binary
    bin_dir = os.path.join(repo_path, "solver", "bin")
    print("* Creating folder \"bin\"", end="")
    if not os.path.isdir(bin_dir):
        os.mkdir(bin_dir)
        print(" -- done.")
    else:
        print(" -- already exists. Skip.")

    # generate binary
    print("* Generating binary executable of the solver", end="")
    sys.stdout.flush()
    job = subprocess.run(
        ["make", "-f", makefile_path, "new"],
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
    else:
        print(" -- done.")

if __name__ == "__main__":

    # path to this repository
    repo_dir = os.path.dirname(os.path.abspath(__file__))

    # get clawpack and geoclaw-landspill based on whether this is a git repo
    if os.path.isdir(os.path.join(repo_dir, ".git")):
        init_git_submodules()
    else:
        download_submodules()

    # setup Clawpack Python package
    setup_clawpack()

    # compile and build solver
    make_geoclaw_bin()

    # setup finished
    print("\nSetup done.\n")
