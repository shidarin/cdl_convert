#!/usr/bin/env python
"""

CDL Convert
===========

Converts between common ASC CDL (http://en.wikipedia.org/wiki/ASC_CDL)
formats. The American Society of Cinematographers Color Decision List (ASC CDL,
or CDL for short) is a schema to simplify the process of interchanging color
data between various programs and facilities.

The ASC has defined schemas for including the 10 basic numbers in 5 different
formats:

* Avid Log Exchange (ALE)
* Film Log EDL Exchange (FLEx)
* CMX EDL
* XML Color Correction (cc)
* XML Color Correction Collection (ccc)
* XML Color Decision List (cdl)

Unofficial Formats:

* OCIOCDLTransform, a Foundry Nuke node
* Space Separated CDL, a Rhythm and Hues cdl format

It is the purpose of CDLConvert to convert ASC CDL information between these
basic formats to further facilitate the ease of exchange of color data within
the Film and TV industries.

`cdl_convert` supports parsing ALE, FLEx, CC, CCC, CDL and RCDL. We can write
out CC, CCC, CDL and RCDL.

**CDLConvert is not associated with the American Society of Cinematographers**

## Public Functions

    reset_all()
        Resets all the class level memberships lists and dictionaries. This
        effectively resets the entire module.

## License

The MIT License (MIT)

cdl_convert
Copyright (c) 2015 Sean Wallitsch
http://github.com/shidarin/cdl_convert/

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import absolute_import, print_function

# cdl_convert imports

from .collection import ColorCollection
from .correction import ColorCorrection, SatNode, SopNode
from .decision import ColorCorrectionRef, ColorDecision, MediaRef
from .parse import (
    parse_ale, parse_cc, parse_ccc,
    parse_cdl, parse_file, parse_flex,
    parse_rnh_cdl
)
from .utils import sanity_check, to_decimal
from .write import write_cc, write_ccc, write_cdl, write_rnh_cdl

# ==============================================================================
# GLOBALS
# ==============================================================================

__author__ = "Sean Wallitsch"
__copyright__ = "Copyright 2015, Sean Wallitsch"
__credits__ = ["Sean Wallitsch", ]
__license__ = "MIT"
__version__ = "0.8"
__maintainer__ = "Sean Wallitsch"
__email__ = "shidarin@alphamatte.com"
__status__ = "Development"

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'ColorCorrection',
    'ColorCorrectionRef',
    'ColorCollection',
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
    'to_decimal',
    'write_cc',
    'write_ccc',
    'write_cdl',
    'write_rnh_cdl',
]

# ==============================================================================
# PUBLIC FUNCTIONS
# ==============================================================================


def reset_all():
    """Resets all class level member lists and dictionaries"""
    # Import these here to avoid cyclic imports

    ColorCorrection.reset_members()
    ColorCorrectionRef.reset_members()
    ColorDecision.reset_members()
    ColorCollection.reset_members()
    MediaRef.reset_members()
