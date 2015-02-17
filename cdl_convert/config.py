#!/usr/bin/env python
"""

CDL Convert Config
================

Contains simple configuration parameters.

## GLOBALS

    HALT_ON_ERROR
        Parameter to be used globally to determine if common exceptions should
        be handled by default behavior or raise. Setting this to True causes
        exceptions to be raised.

        Default: False

    COLLECTION_FORMATS
        List containing all the formats which are represented by
        ColorCollection.

    SINGLE_FORMATS
        List containing all the formats which are represented by a single
        ColorCorrection.

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
# GLOBALS
# ==============================================================================

# HALT_ON_ERROR is the exception handling variable for exceptions that can
# be handled silently.
#
# If we begin to get more config options, this will be moved into a singleton
# config class.
#
# Used in the following places:
#   Slope, power and sat values can't be negative and will truncate to 0.0
#   If id given to ColorCorrection is blank, will set to number of CCs
#   When determining if a non-existent directory referenced by MediaRef
#       contains an image sequence, will just return False.
#   If attempting to retrieve a referenced ColorCorrection whose id doesn't
#       exist.
#   If attempting to set a ColorCorrectionRef to a ColorCorrection whose
#       id doesn't exist. (Other than first creation)
#   If a ColorCorrection is given a duplicate ID
HALT_ON_ERROR = False

COLLECTION_FORMATS = ['ale', 'ccc', 'cdl', 'flex']
SINGLE_FORMATS = ['cc', 'rcdl']

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = ['HALT_ON_ERROR']
