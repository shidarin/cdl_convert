"""All code for cdl_convert lives under the cdl_convert.py file"""
# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import absolute_import, print_function

# cdl_convert imports

from .collection import ColorCollection
from . import config
from .correction import ColorCorrection, SatNode, SopNode
from .decision import ColorCorrectionRef, ColorDecision, MediaRef
from .parse import (
    parse_ale, parse_cc, parse_ccc, parse_cdl, parse_flex, parse_rnh_cdl
)
from .utils import reset_all, sanity_check
from .write import write_cc, write_ccc, write_cdl, write_rnh_cdl

# ==============================================================================
# GLOBALS
# ==============================================================================

__author__ = "Sean Wallitsch"
__copyright__ = "Copyright 2014, Sean Wallitsch"
__credits__ = ["Sean Wallitsch", ]
__license__ = "MIT"
__version__ = "0.6.1"
__maintainer__ = "Sean Wallitsch"
__email__ = "shidarin@alphamatte.com"
__status__ = "Development"

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'ColorCorrection',
    'ColorCorrectionRef',
    'ColorDecision',
    'MediaRef',
    'parse_ale',
    'parse_cc',
    'parse_ccc',
    'parse_cdl',
    'parse_file',
    'parse_flex',
    'parse_rnh_cdl',
    'reset_all',
    'sanity_check',
    'SatNode',
    'SopNode',
    'write_cc',
    'write_ccc',
    'write_cdl',
    'write_rnh_cdl',
]