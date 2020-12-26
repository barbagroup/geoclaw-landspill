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


def check_folder(folder: os.PathLike):
    """To check if a folder exist and raise corresponding errors.

    Arguments
    ---------
    folder : os.PathLike
        The path to the target folder.

    Exceptions
    ----------
    `FileNotFoundError` if the folder does not exist or is not a valid folder.
    """

    if not pathlib.Path(folder).is_dir():
        raise FileNotFoundError("{} does not exist or is not a folder.".format(folder))


def str_to_bool(value: str):
    """Convert a string to bool.

    Arguments
    ---------
    value : str
        A string representation of a boolean.

    Returns
    -------
    A bool.

    Exceptions
    ----------
    Raise a ValueError if the string is not recognized as a boolean's string representation.
    """

    if value.lower() in ["true", "on", "1", "yes"]:
        return True

    if value.lower() in ["false", "off", "0", "no"]:
        return False

    raise ValueError("Not recognized as a bool: {}".format(value))


def process_path(path, parent, default):
    """Convert a path to an absolute path based on its current value.

    Arguments
    ---------
    path : PathLike
        The path to be processed.
    parent : PathLike
        The parent path that `path` will be appended to if `path` is a relative path.
    default : PathLike
        If the content of `path` is None, substitute `path` with this value.

    Returns
    -------
    If `path` is None and `default` is a relative path, return `parent/default`.
    If `path` is None and `default` is an absolute path, return `default`.
    If `path` is a relative path, return `parent/path`.
    If `path` is an absolute path, return `path`.

    The type of the retuen is `pathlib.Path`.
    """
    path = pathlib.Path(default) if path is None else pathlib.Path(path)

    if path.is_absolute():
        return path

    return pathlib.Path(parent).joinpath(path)
