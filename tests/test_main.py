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


class TestMain:
    """Test the main function."""
    # pylint: disable=no-self-use

    def test_help(self):
        """Test --help."""
        sys.argv = ["geoclaw-landspill", "--help"]
        _call_main()

    def test_run_help(self):
        """Test run --help."""
        sys.argv = ["geoclaw-landspill", "run", "--help"]
        _call_main()

    def test_createnc_help(self):
        """Test createnc --help."""
        sys.argv = ["geoclaw-landspill", "createnc", "--help"]
        _call_main()

    def test_plotdepth_help(self):
        """Test plotdepth --help."""
        sys.argv = ["geoclaw-landspill", "plotdepth", "--help"]
        _call_main()

    def test_plottopo_help(self):
        """Test plottopo --help."""
        sys.argv = ["geoclaw-landspill", "plottopo", "--help"]
        _call_main()

    def test_volumes_help(self):
        """Test volumes --help."""
        sys.argv = ["geoclaw-landspill", "volumes", "--help"]
        _call_main()


def _call_main():
    """Call the main function and expecting a sys exit code 0."""

    # check if can be called directly in Python
    with pytest.raises(SystemExit) as err:
        gclandspill.__main__.main()
    assert err.type == SystemExit
    assert err.value.code == 0

    # check if can be called through executable
    subprocess.run(sys.argv, capture_output=False, check=True)
