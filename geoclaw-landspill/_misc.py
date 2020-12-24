#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020-2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""Miscellaneous functions.
"""
import os
import sys
import pathlib
import importlib.util


def import_setrun(case_dir: os.PathLike):
    """A helper to import setrun.py from a case folder.

    The sys.modules will have a module called `setrun`.

    Arguments
    ---------
    case_dir : PathLike
        The path to the case folder of a simulation. A setrun.py should present in that folder.

    Returns
    -------
    An imported module.
    """

    setrun_path = pathlib.Path(case_dir).expanduser().resolve().joinpath("setrun.py")

    if not setrun_path.is_file():
        raise FileNotFoundError("{} does not exist or is not a file".format(setrun_path))

    spec = importlib.util.spec_from_file_location("setrun", str(setrun_path))
    setrun = importlib.util.module_from_spec(spec)
    sys.modules["setrun"] = setrun
    spec.loader.exec_module(setrun)
    return setrun
