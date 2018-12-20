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
    sys.stdout.write(
        "\rDownloading file {}".format(filename) +
        " -- [{:d}%, ".format(percent) +
        "{:d} MB, ".format(int(progress_size/(1024*1024))) +
        "{:d} KB/s, ".format(speed) +
        "{:d} sec. passed]".format(int(duration)))
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
        sys.stdout.write("Downloading file {}".format(filename) +
                         " -- already exists. Skip.\n")
    else:
        urlretrieve(fileurl, filepath+".tmp",
                    functools.partial(reporthook, filename))
        os.rename(filepath+".tmp", filepath)
        sys.stdout.write(" -- done.\n")
    sys.stdout.flush()


if __name__ == "__main__":

    # absolute path to this repository
    repo_path = os.path.dirname(os.path.abspath(__file__))

    # path to the folder that will hold topo and hydro files
    file_dir = os.path.join(repo_path, "common-files")

    # create a folder for topo and hydro files
    sys.stdout.write("Creating folder \"common-files\"")
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)
        sys.stdout.write(" -- done.\n")
    else:
        sys.stdout.write(" -- already exists. Skip.\n")
    sys.stdout.flush()

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

    print("Setup done.")

