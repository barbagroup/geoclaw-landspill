#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Test the main function.
"""
import sys
import subprocess
import pytest
import gclandspill
import gclandspill.__main__


def call_main():
    """Call the main function and the executable, expecting a sys exit code 0."""

    # check if can be called directly in Python
    with pytest.raises(SystemExit) as err:
        gclandspill.__main__.main()
    assert err.type == SystemExit
    assert err.value.code == 0

    # check if can be called through executable
    subprocess.run(sys.argv, capture_output=False, check=True)


def test_help():
    """Test --help."""
    sys.argv = ["geoclaw-landspill", "--help"]
    call_main()


def test_run_help():
    """Test run --help."""
    sys.argv = ["geoclaw-landspill", "run", "--help"]
    call_main()


def test_createnc_help():
    """Test createnc --help."""
    sys.argv = ["geoclaw-landspill", "createnc", "--help"]
    call_main()


def test_plotdepth_help():
    """Test plotdepth --help."""
    sys.argv = ["geoclaw-landspill", "plotdepth", "--help"]
    call_main()


def test_plottopo_help():
    """Test plottopo --help."""
    sys.argv = ["geoclaw-landspill", "plottopo", "--help"]
    call_main()


def test_volumes_help():
    """Test volumes --help."""
    sys.argv = ["geoclaw-landspill", "volumes", "--help"]
    call_main()
