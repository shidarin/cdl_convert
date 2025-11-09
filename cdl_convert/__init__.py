#!/usr/bin/env python
"""CDL Convert - Modern ASC CDL Format Conversion Library

CDL Convert is a Python library and command-line tool for converting between
common American Society of Cinematographers Color Decision List (ASC CDL)
formats. This modernized version uses Python 3.11+ features including type
hints, pathlib, dataclasses, and enhanced error handling.

https://en.wikipedia.org/wiki/ASC_CDL

CDL is a schema to simplify the process of interchanging color data between
various programs and facilities in the film and television industry.

Supported Input Formats:
    * Avid Log Exchange (ALE)
    * Film Log EDL Exchange (FLEx)
    * CMX EDL
    * XML Color Correction (cc)
    * XML Color Correction Collection (ccc)
    * XML Color Decision List (cdl)
    * Space Separated CDL (RCDL) - Rhythm and Hues format

Supported Output Formats:
    * XML Color Correction (cc)
    * XML Color Correction Collection (ccc)
    * XML Color Decision List (cdl)
    * Space Separated CDL (RCDL)

ToDo:
    * OCIOCDLTransform (Foundry Nuke node)

Example Usage:
    >>> from cdl_convert import parse_file, ColorCorrection
    >>>
    >>> # Parse any supported format
    >>> collection = parse_file("input.ale")
    >>> print(f"Found {len(collection.color_corrections)} corrections")
    >>>
    >>> # Create and modify corrections
    >>> cc = ColorCorrection("my_shot")
    >>> cc.slope = [1.2, 1.1, 1.0]
    >>> cc.sat = 0.9
    >>>
    >>> # Use ColorValues dataclass
    >>> values = cc.get_color_values()
    >>> print(f"Is unity: {values.is_unity()}")

**CDL Convertis not associated with the American Society of Cinematographers**

## Public Functions

    reset_all() -> None
        Resets all the class level memberships lists and dictionaries. This
        effectively resets the entire module.
## License

The MIT License (MIT)

cdl_convert
Copyright (c) 2015-2025 Sean Wallitsch
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

# cdl_convert imports

from cdl_convert.collection import ColorCollection
from cdl_convert.correction import ColorCorrection, SatNode, SopNode
from cdl_convert.decision import ColorCorrectionRef, ColorDecision, MediaRef
from cdl_convert.exceptions import (
    CDLConvertError,
    FormatError,
    ParseError,
    ValidationError,
)
from cdl_convert.parse import (
    parse_ale,
    parse_cc,
    parse_ccc,
    parse_cdl,
    parse_cmx,
    parse_file,
    parse_flex,
    parse_otio,
    parse_rnh_cdl,
)
from cdl_convert.utils import sanity_check, to_decimal
from cdl_convert.write import write_cc, write_ccc, write_cdl, write_rnh_cdl

# ==============================================================================
# GLOBALS
# ==============================================================================

__author__ = "Sean Wallitsch"
__copyright__ = "Copyright 2015-2025, Sean Wallitsch"
__credits__ = ["Sean Wallitsch"]
__license__ = "MIT"
__version__ = "0.9.2"
__maintainer__ = "Sean Wallitsch"
__email__ = "shidarin@alphamatte.com"
__status__ = "Development"

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "CDLConvertError",
    "ColorCorrection",
    "ColorCorrectionRef",
    "ColorCollection",
    "ColorDecision",
    "FormatError",
    "MediaRef",
    "ParseError",
    "parse_ale",
    "parse_cc",
    "parse_ccc",
    "parse_cdl",
    "parse_cmx",
    "parse_file",
    "parse_flex",
    "parse_otio",
    "parse_rnh_cdl",
    "reset_all",
    "sanity_check",
    "SatNode",
    "SopNode",
    "to_decimal",
    "ValidationError",
    "write_cc",
    "write_ccc",
    "write_cdl",
    "write_rnh_cdl",
]

# ==============================================================================
# PUBLIC FUNCTIONS
# ==============================================================================


def reset_all() -> None:
    """Reset all class level member lists and dictionaries.

    This function clears all registered ColorCorrection, ColorCollection,
    ColorDecision, and related class instances. Useful for testing or
    when you need to start with a clean state.

    Example:
        >>> from cdl_convert import ColorCorrection, reset_all
        >>> cc1 = ColorCorrection("test1")
        >>> cc2 = ColorCorrection("test2")
        >>> print(len(ColorCorrection.members))  # 2
        >>> reset_all()
        >>> print(len(ColorCorrection.members))  # 0

    """
    # Import these here to avoid cyclic imports

    ColorCorrection.reset_members()
    ColorCorrectionRef.reset_members()
    ColorDecision.reset_members()
    ColorCollection.reset_members()
    MediaRef.reset_members()
