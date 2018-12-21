#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the MIT license.

"""Set up the cases.

Most of the cases require topography files and files describing hydrologic
features. The sizes of these files are not small, and hence they are not
included in this repository. Use this script to download all necessary files so the
cases are complete.
"""
import os
import sys
import time
import functools
import subprocess
import textwrap

# import urlretrieve based on the version of Python
if sys.version_info.major == 2:
    from urllib import urlretrieve
elif sys.version_info.major == 3:
    from urllib.request import urlretrieve
else:
    raise ImportError("Unknown Python version.")


def reporthook(filename, count, block_size, total_size):
    """Progress bar

    This code is modified base on the following code snippet:
    https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
    """
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count*block_size)
    speed = int(progress_size/(1024*duration))
    percent = int(count*block_size*100/total_size)
    print(
        "\r* Downloading file {}".format(filename) +
        " -- [{:d}%, ".format(percent) +
        "{:d} MB, ".format(int(progress_size/(1024*1024))) +
        "{:d} KB/s, ".format(speed) +
        "{:d} sec. passed]".format(int(duration)), end="")
    sys.stdout.flush()

def download_file(fname, furl, dpath):
    """Download a file from a given URL

    Args:
        fname [in]: name of the file.
        furl: [in]: URL of the file.
        dpath [in]: the absolute path of the directory where the downloaded
                    file will go to.
    """

    filepath = os.path.join(dpath, filename)

    if os.path.isfile(filepath):
        print("* Downloading file {}".format(filename) +
                         " -- already exists. Skip.")
    else:
        urlretrieve(fileurl, filepath+".tmp",
                    functools.partial(reporthook, filename))
        os.rename(filepath+".tmp", filepath)
        print(" -- done.")
    sys.stdout.flush()

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

    # download utah_dem_topo_3.txt
    filename = "utah_dem_topo_3.txt"
    fileurl = "https://dl.dropboxusercontent.com/s/hhpebow2s81yzgo/" +\
        "{}?dl=0".format(filename)
    download_file(filename, fileurl, file_dir)

    # download hydro_feature1.asc
    filename = "hydro_feature1.asc"
    fileurl = "https://dl.dropboxusercontent.com/s/02lbf2kg84b5sij/" +\
        "{}?dl=0".format(filename)
    download_file(filename, fileurl, file_dir)

    # download hydro_feature2.asc
    filename = "hydro_feature2.asc"
    fileurl = "https://dl.dropboxusercontent.com/s/mh8eh7wx6jy1z2t/" +\
        "{}?dl=0".format(filename)
    download_file(filename, fileurl, file_dir)

    # download hydro_feature3.asc
    filename = "hydro_feature3.asc"
    fileurl = "https://dl.dropboxusercontent.com/s/gs3g7amhatn9pxf/" +\
        "{}?dl=0".format(filename)
    download_file(filename, fileurl, file_dir)

    # download mountain.asc
    filename = "mountain.asc"
    fileurl = "https://dl.dropboxusercontent.com/s/c21eg6yt90jll1r/" +\
        "{}?dl=0".format(filename)
    download_file(filename, fileurl, file_dir)

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

