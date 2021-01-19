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

# the absolute path to the root directory
rootdir = pathlib.Path(__file__).resolve().parent

# basic package information
meta = dict(
    name="geoclaw-landspill",
    author="Pi-Yueh Chuang",
    author_email="pychuang@gwu.edu",
    url="https://github.com/barbagroup/geoclaw-landspill",
    keywords=["landspill", "overland flow", "pipeline", "geoclaw", "clawpack"],
    license="BSD 3-Clause License",
)

# classifiers for categorizing; see https://pypi.org/classifiers/
meta["classifiers"] = [
    "Development Status :: 1 - Planning",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Operating System :: Unix",
    "Programming Language :: Fortran",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering"
]

# license files
meta["license_files"] = [
    "LICENSE",
    "third-party/amrclaw/LICENSE",
    "third-party/geoclaw/LICENSE",
    "third-party/pyclaw/LICENSE",
    "third-party/clawutil/LICENSE"
]

# version and short sescription (read from __init__.py)
with open(rootdir.joinpath("gclandspill", "__init__.py"), 'r') as fileobj:
    content = fileobj.read()
    # version
    meta["version"] = re.search(
        r"__version__\s*?=\s*?(?P<version>\S+?)$", content, re.MULTILINE
    ).group("version").strip("\"\'")
    # one line description
    meta["description"] = re.search(
        r"^\"\"\"(?P<desc>\S.*?)$", content, re.MULTILINE
    ).group("desc")

# long  description (read from README.md)
with open(rootdir.joinpath("README.md"), 'r') as fileobj:
    meta["long_description"] = fileobj.read()
    meta["long_description_content_type"] = "text/markdown"

# dependencies
with open(rootdir.joinpath("requirements.txt"), "r") as fileobj:
    deps = fileobj.readlines()
    meta["python_requires"] = ">=3.7"
    meta["install_requires"] = [line.strip() for line in deps]

# packages to be installed
meta["packages"] = ["gclandspill"]
meta["package_dir"] = {"gclandspill": "gclandspill"}

# executable
meta["entry_points"] = {"console_scripts": ["geoclaw-landspill = gclandspill.__main__:main"]}

# scikit-build specific
meta["cmake_with_sdist"] = False
meta["cmake_languages"] = ["Fortran"]
meta["cmake_minimum_required_version"] = "3.14"

if __name__ == "__main__":
    skbuild.setup(**meta)
