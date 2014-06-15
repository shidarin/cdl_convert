#!/usr/bin/env python
"""

CDL Convert Utils
=================

Contains basic utility functions for cdl_convert

## License

The MIT License (MIT)

cdl_convert
Copyright (c) 2014 Sean Wallitsch
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

# cdl_convert Imports
from .collection import ColorCollection
from .correction import ColorCorrection
from .decision import ColorCorrectionRef, ColorDecision, MediaRef

# ==============================================================================
# GLOBALS
# ==============================================================================

# Python 3 Compatibility

try:
    xrange
except NameError:  # pragma: no cover
    xrange = range  # pylint: disable=W0622, C0103

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'reset_all',
    'sanity_check',
]

# ==============================================================================
# PUBLIC FUNCTIONS
# ==============================================================================


def reset_all():
    """Resets all class level member lists and dictionaries"""
    ColorCorrection.reset_members()
    ColorCorrectionRef.reset_members()
    ColorDecision.reset_members()
    ColorCollection.reset_members()
    MediaRef.reset_members()

# ==============================================================================


def sanity_check(colcor):
    """Checks values on :class:`ColorCorrection` for sanity.

    **Args:**
        colcor : (:class:`ColorCorrection`)
            The :class:`ColorCorrection` to check for sane values.

    **Returns:**
        (bool)
            Returns True if all values are sane.

    **Raises:**
        N/A

    Will print a warning to stdout if any values exceed normal limits.
    Normal limits are defined as:

    For Slope, Power and Saturation:
        Any value over 3 or under 0.1

    For Offset:
        Any value over 1 or under -1

    Note that depending on the desired look for a shot or sequence, it's
    possible that a single ColorCorrection element might have very odd
    looking values and still achieve a correct look.

    """
    sane_values = True

    def _check_value(value, minmax, value_type):
        """Checks if a value falls outside of min or max"""
        if value <= minmax[0] or value >= minmax[1]:
            print(
                'The ColorCorrection "{id}" was given a {type} value of '
                '"{value}", which might be incorrect.'.format(
                    id=colcor.id,
                    type=value_type,
                    value=value
                )
            )
            return False
        else:
            return True

    if colcor.has_sop:
        for i in xrange(3):
            slope = _check_value(colcor.slope[i], (0.1, 3.0), 'Slope')
            offset = _check_value(colcor.offset[i], (-1.0, 1.0), 'Offset')
            power = _check_value(colcor.power[i], (0.1, 3.0), 'Power')
            if not slope or not offset or not power:
                sane_values = False

    if colcor.has_sat:
        if not _check_value(colcor.sat, (0.1, 3.0), 'Saturation'):
            sane_values = False

    return sane_values
