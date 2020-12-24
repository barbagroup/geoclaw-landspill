#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018-2021 Pi-Yueh Chuang and Lorena A. Barba.
#
# Distributed under terms of the BSD 3-Clause license.

"""Build geoclaw-landspull package as a Python package.
"""
import re
import pathlib
import skbuild


def get_strings():
    """Get content of __version__, description, and README.

    Note for __version__:
        It's is not recommended to get __version__ by importing the package
        because it may cause problems if __init__.py imports packages that will
        be listed in install_requires of setuptools.setup. So instead, it is
        recommended to use string parsing to obtain the version.

    For description, it's just convenient to mantain such string at a single
    place.

    Args:
    -----
        None.

    Returns:
    --------
        version: a str: the version string.
        desc: a str: one line description summarizing the package.
        readme: a str; the content of README.md.
    """

    # the absolute path to the root directory
    rootdir = pathlib.Path(__file__).resolve().parent

    # read README.md and overwrite readme
    with open(rootdir.joinpath("README.md"), 'r') as fileobj:
        readme = fileobj.read()

    # read __init__.py
    with open(rootdir.joinpath("geoclaw-landspill", "__init__.py"), 'r') as fileobj:
        content = fileobj.read()

    # version
    version = re.search(r"__version__\s*?=\s*?(?P<version>\S+?)$", content, re.MULTILINE)
    version = version.group("version").strip("\"\'")

    # desc
    desc = re.search(r"^\"\"\"(?P<desc>\S.*?)$", content, re.MULTILINE)
    desc = desc.group("desc")

    return version, desc, readme


# basic information
meta = dict(
    name="geoclaw-landspill",
    long_description_content_type="text/markdown",
    author="Pi-Yueh Chuang",
    author_email="pychuang@gwu.edu",
    url="https://github.com/barba/geoclaw-landspill",
    keywords=["landspill", "overland flow", "pipeline", "geoclaw", "clawpack"],
    license="BSD 3-Clause License",
)

# info from __init__.py
meta["version"], meta["description"], meta["long_description"] = get_strings()

# classifiers for categorizing; see https://pypi.org/classifiers/
meta["classifiers"] = [
    "Development Status :: 1 - Planning"
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Operating System :: Unix",
    "Programming Language :: Fortran",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering"
]

# packages to be installed
meta["packages"] = ["gclandspill", "gclandspill.clawutil", "gclandspill.pyclaw"]
meta["package_dir"] = {
    "gclandspill": "lib/gclandspill",
    "gclandspill.amrclaw": "lib/gclandspill/amrclaw",
    "gclandspill.geoclaw": "lib/gclandspill/geoclaw",
    "gclandspill.clawutil": "lib/gclandspill/clawutil",
    "gclandspill.pyclaw": "lib/gclandspill/pyclaw"
}

# executable
meta["entry_points"] = {"console_scripts": ["geoclaw-landspill = gclandspill.__main__:main"]}

# scikit-build specific
meta["cmake_with_sdist"] = True
meta["cmake_languages"] = ["Fortran"]
meta["cmake_minimum_required_version"] = "3.14"

if __name__ == "__main__":
    skbuild.setup(**meta)
