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
import argparse
import importlib.util

try:
    from typing import TypedDict
except ImportError:  # when python version <= 3.7
    from typing_extensions import TypedDict


class AMRLevelError(Exception):
    """An error to raise when the target AMR level does not exist."""
    pass  # pylint: disable=unnecessary-pass


class NoWetCellError(Exception):
    """An error to raise when there's not we cell."""
    pass  # pylint: disable=unnecessary-pass


class WrongTopoFileError(Exception):
    """An error to raise when users give an unexpected topography format."""
    pass  # pylint: disable=unnecessary-pass


class NoFrameDataError(Exception):
    """An error to raise when no data found for this time frame."""
    pass  # pylint: disable=unnecessary-pass


class FrictionModelError(Exception):
    """An error to raise when both Manning and Darcy-Weisbach models are enabled."""
    pass  # pylint: disable=unnecessary-pass


class DatetimeCtrlParams(TypedDict):
    """A type definition for the `dict` controlling the timestamps."""
    apply_datetime_stamp = bool
    datetime_stamp = str
    calendar_type = str


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


def extract_info_from_setrun(args: argparse.Namespace):
    """Extract frequently used information from a setrun.py and write to a CMD argument object.

    In post-processing functions, Some information is frequently requested from a setrun.py and set
    into a argparse.Namespace object. This function does this job. Currently, the following values
    are processed:

    * args.level: maximum AMR level
    * args.frame_ed: the end frame number
    * args.dry_tol: dry tolerance
    * args.topofiles: a list of topography file paths (abs paths)

    If the provided `args` does not have these keys present, they will be ignore, except
    `topofiles`. Currently, no subcommand set `topofiles` in `args` in geoclaw-landspill. So
    `topofiles` will always be created in this function.

    The provided `args` must have the key `case`. And it is assumed to be a pathlib.Path object.

    Arguments
    ---------
    args : argparse.Namespace
        The CMD arguments parsed by the sub-parsers of subcommands.

    Returns
    -------
    The same `args` object with updated values.
    """

    def test_and_set_amr_level():
        """Local function to avoid pylint's complaint: test and set AMR maximum level."""
        try:
            if args.level is None:
                args.level = rundata.amrdata.amr_levels_max
        except AttributeError as err:
            if str(err).startswith("'Namespace' object"):
                pass

    def test_and_set_frame_ed():
        """Local function to avoid pylint's complaint: test and set end frame number."""
        try:
            if args.frame_ed is not None:
                args.frame_ed += 1  # plus 1 so it can be used as the `end` in the `range` function
            elif rundata.clawdata.output_style == 1:  # if it's None, and the style is 1
                args.frame_ed = rundata.clawdata.num_output_times
                if rundata.clawdata.output_t0:
                    args.frame_ed += 1
            elif rundata.clawdata.output_style == 2:  # if it's None, and the style is 2
                args.frame_ed = len(rundata.clawdata.output_times)
            elif rundata.clawdata.output_style == 3:  # if it's None, and the style is 3
                args.frame_ed = rundata.clawdata.total_steps // rundata.clawdata.output_step_interval
                if rundata.clawdata.output_t0:
                    args.frame_ed += 1
        except AttributeError as err:
            if str(err).startswith("'Namespace' object"):
                pass

    def test_and_set_dry_tol():
        """Local function to avoid pylint's complaint: test and set dry tolerance."""
        try:
            if args.dry_tol is None:
                args.dry_tol = rundata.geo_data.dry_tolerance
        except AttributeError as err:
            if str(err).startswith("'Namespace' object"):
                pass

    # get the case's setrun data
    rundata = import_setrun(args.case).setrun()

    test_and_set_amr_level()
    test_and_set_frame_ed()
    test_and_set_dry_tol()

    # always create topofiles
    args.topofiles = []
    for topo in rundata.topo_data.topofiles:
        if topo[0] != 3:
            raise WrongTopoFileError("Only accept type-3 topography: {} at {}".format(*topo))

        topo[-1] = pathlib.Path(topo[-1])
        if not topo[-1].is_absolute():
            topo[-1] = args.case.joinpath(topo[-1]).resolve()

        args.topofiles.append(topo[-1])

    return args
