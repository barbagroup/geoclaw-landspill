#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang and Lorena A. Barba
#
# Distributed under terms of the BSD 3-Clause license.

"""A hydrocarbon overland flow simulator for pipeline rupture events.
"""
import sys
sys.modules["clawpack"] = sys.modules["gclandspill"] # trick python to believe this is also clawpack

from . import pyclaw
from . import clawutil
from . import amrclaw
from . import geoclaw

# meta
__version__ = "1.0.dev0"
__author__ = "Pi-Yueh Chuang <pychuang@gwu.edu>"
