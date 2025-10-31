#!/usr/bin/env python
"""

CDL Convert Write
=================

Functions for writing different types of cdls.

## Public Functions

    write_cc()
        Writes a given ColorCorrection to disk. ``file_out`` should already be
        set on the ColorCorrection.

    write_ccc()
        Writes a given ColorCollection to disk. ``file_out`` should already be
        set on the ColorCollection.

    write_cdl()
        Writes a given ColorCollection to disk. ``file_out`` should already be
        set on the ColorCollection.

    write_rnh_cdl()
        Writes a given ColorCorrection to disk. ``file_out`` should already be
        set on the ColorCorrection.

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

# Standard Imports

from typing import Union

# cdl_convert imports
from .collection import ColorCollection
from .correction import ColorCorrection
from .exceptions import CDLConvertError

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'write_cc',
    'write_ccc',
    'write_cdl',
    'write_rnh_cdl',
]

# ==============================================================================
# PRIVATE FUNCTIONS
# ==============================================================================


def _temp_container(cdl: ColorCorrection) -> ColorCollection:
    """Builds a temporary collection container for a single cdl file."""
    temp_cdl = ColorCollection()
    orig_parent = cdl.parent
    temp_cdl.append_child(cdl)
    cdl.parent = orig_parent  # Restore original parentage away from temp cdl
    temp_cdl._file_out = cdl.file_out
    return temp_cdl

# ==============================================================================
# PUBLIC FUNCTIONS
# ==============================================================================


def write_cc(cdl: ColorCorrection) -> None:
    """Writes the ColorCorrection to a .cc file"""
    try:
        with open(cdl.file_out, 'w', encoding='utf-8') as cdl_f:
            cdl_f.write(cdl.xml_root)
    except OSError as e:
        raise CDLConvertError(
            f"Failed to write CC file '{cdl.file_out}': {e}"
        ) from e

# ==============================================================================


def write_ccc(cdl: Union[ColorCorrection, ColorCollection]) -> None:
    """Writes the ColorCollection to a .ccc file"""
    if not isinstance(cdl, ColorCollection):
        cdl = _temp_container(cdl)

    collection_type = cdl.type
    cdl.set_to_ccc()
    try:
        with open(cdl.file_out, 'w', encoding='utf-8') as cdl_f:
            cdl_f.write(cdl.xml_root)
    except OSError as e:
        raise CDLConvertError(
            f"Failed to write CCC file '{cdl.file_out}': {e}"
        ) from e
    finally:
        cdl.type = collection_type

# ==============================================================================


def write_cdl(cdl: Union[ColorCorrection, ColorCollection]) -> None:
    """Writes the ColorCollection to a .cdl file"""
    if not isinstance(cdl, ColorCollection):
        cdl = _temp_container(cdl)

    collection_type = cdl.type
    cdl.set_to_cdl()
    try:
        with open(cdl.file_out, 'w', encoding='utf-8') as cdl_f:
            cdl_f.write(cdl.xml_root)
    except OSError as e:
        raise CDLConvertError(
            f"Failed to write CDL file '{cdl.file_out}': {e}"
        ) from e
    finally:
        cdl.type = collection_type

# ==============================================================================


def write_rnh_cdl(cdl: ColorCorrection) -> None:
    """Writes the ColorCorrection to a space separated .cdl file"""
    # Import here to avoid circular imports
    from .correction import _de_exponent

    values = list(cdl.slope)
    values.extend(cdl.offset)
    values.extend(cdl.power)
    values.append(cdl.sat)
    # Use _de_exponent to avoid scientific notation (consistent with XML output)
    values = [_de_exponent(i) for i in values]

    ss_cdl = ' '.join(values)

    try:
        with open(cdl.file_out, 'w', encoding='utf-8') as cdl_f:
            cdl_f.write(ss_cdl)
    except OSError as e:
        raise CDLConvertError(
            f"Failed to write RNH CDL file '{cdl.file_out}': {e}"
        ) from e

# ==============================================================================
# GLOBALS
# ==============================================================================

OUTPUT_FORMATS = {
    'cc': write_cc,
    'ccc': write_ccc,
    'cdl': write_cdl,
    'rcdl': write_rnh_cdl,
}
