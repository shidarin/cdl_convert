#!/usr/bin/env python
"""CDL Convert Write Module

Provides writing capabilities for all supported ASC CDL output formats.

Public Functions:
    write_cc(ColorCorrection) -> None: Write ColorCorrection to .cc XML format.

    write_ccc(Union[ColorCorrection, ColorCollection]) -> None: Write to .ccc
        XML format (ColorCorrectionCollection) with automatic collection
        wrapping.

    write_cdl(Union[ColorCorrection, ColorCollection]) -> None: Write to .cdl
        XML format (ColorDecisionList).

    write_rnh_cdl(ColorCorrection) -> None: Write to Rhythm & Hues
        space-separated format.

Example Usage:
    >>> from pathlib import Path
    >>> from cdl_convert import ColorCorrection, ColorCollection, write_cc, write_ccc
    >>> 
    >>> # Write single correction
    >>> cc = ColorCorrection("shot_001")
    >>> cc.file_out = Path("output.cc")
    >>> cc.slope = [1.2, 1.1, 1.0]
    >>> 
    >>> try:
    ...     write_cc(cc)
    ...     print(f"Successfully wrote {cc.file_out}")
    ... except CDLConvertError as e:
    ...     print(f"Write error: {e}")
    >>> 
    >>> # Write collection with format handling
    >>> collection = ColorCollection()
    >>> collection.append_child(cc)
    >>> collection.file_out = Path("collection.ccc")
    >>> write_ccc(collection)

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

# Standard Imports

from pathlib import Path
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
    """Build a temporary collection container for a single CDL file.
    
    This helper function creates a temporary ColorCollection to wrap a single
    ColorCorrection for writing operations that require collection format.
    
    Args:
        cdl (ColorCorrection): The ColorCorrection to wrap in a collection.
        
    Returns:
        ColorCollection: A temporary collection containing the single
            correction.
        
    """
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
    """Write a ColorCorrection to a .cc XML file.

    Args:
        cdl (ColorCorrection): The ColorCorrection instance to write. Must have
            a valid file_out attribute set to the target file path.

    Raises:
        CDLConvertError: If the file cannot be written, with the original
            OSError chained for context. This includes permission errors,
            disk space issues, or invalid file paths.

    Example:
        >>> from pathlib import Path
        >>> cc = ColorCorrection("test_id")
        >>> cc.file_out = Path("output.cc")
        >>> cc.slope = [1.2, 1.1, 1.0]
        >>> write_cc(cc)  # Writes XML to output.cc

    """
    if cdl.file_out is None:
        raise CDLConvertError(
            "Output file path not set. Set cdl.file_out before writing."
        )
    
    try:
        with open(cdl.file_out, 'w', encoding='utf-8') as cdl_f:
            cdl_f.write(cdl.xml_root)
    except OSError as e:
        raise CDLConvertError(
            f"Failed to write CC file '{cdl.file_out}': {e}"
        ) from e

# ==============================================================================


def write_ccc(cdl: Union[ColorCorrection, ColorCollection]) -> None:
    """Write a ColorCollection to a .ccc XML file.

    Accepts either a single ColorCorrection (which gets wrapped in a 
    temporary collection) or a full ColorCollection.

    Args:
        cdl (Union[ColorCorrection, ColorCollection]): The color correction
            data to write. If a ColorCorrection is provided, it will be
            wrapped in a temporary ColorCollection.

    Raises:
        CDLConvertError: If the file cannot be written, with the original
            OSError chained for context. This includes permission errors,
            disk space issues, or invalid file paths.

    Example:
        >>> from pathlib import Path
        >>> # Write a single correction
        >>> cc = ColorCorrection("test_id")
        >>> cc.file_out = Path("output.ccc")
        >>> write_ccc(cc)
        
        >>> # Write a collection
        >>> collection = ColorCollection()
        >>> collection.append_child(cc)
        >>> collection.file_out = Path("collection.ccc")
        >>> write_ccc(collection)

    """
    if not isinstance(cdl, ColorCollection):
        cdl = _temp_container(cdl)

    if cdl.file_out is None:
        raise CDLConvertError(
            "Output file path not set. Set cdl.file_out before writing."
        )

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
    """Write a ColorCollection to a .cdl XML file.

    Accepts either a single ColorCorrection (which gets wrapped in a 
    temporary collection) or a full ColorCollection.

    Args:
        cdl (Union[ColorCorrection, ColorCollection]): The color correction
            data to write. If a ColorCorrection is provided, it will be
            wrapped in a temporary ColorCollection.

    Raises:
        CDLConvertError: If the file cannot be written, with the original
            OSError chained for context. This includes permission errors,
            disk space issues, or invalid file paths.

    Example:
        >>> from pathlib import Path
        >>> # Write a single correction as CDL
        >>> cc = ColorCorrection("test_id")
        >>> cc.file_out = Path("output.cdl")
        >>> write_cdl(cc)
        
        >>> # Write a collection as CDL
        >>> collection = ColorCollection()
        >>> collection.append_child(cc)
        >>> collection.file_out = Path("collection.cdl")
        >>> write_cdl(collection)

    """
    if not isinstance(cdl, ColorCollection):
        cdl = _temp_container(cdl)

    if cdl.file_out is None:
        raise CDLConvertError(
            "Output file path not set. Set cdl.file_out before writing."
        )

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

    if cdl.file_out is None:
        raise CDLConvertError(
            "Output file path not set. Set cdl.file_out before writing."
        )

    values = list(cdl.slope)
    values.extend(cdl.offset)
    values.extend(cdl.power)
    values.append(cdl.sat)
    # Use _de_exponent to avoid scientific notation (consistent with XML output)
    str_values = [_de_exponent(i) for i in values]


    str_values = [_de_exponent(i) for i in values]

    ss_cdl = ' '.join(str_values)

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
