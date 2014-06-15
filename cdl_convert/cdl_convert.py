#!/usr/bin/env python
"""

CDL Convert
==========

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

Unofficial Formats:

* OCIOCDLTransform, a Foundry Nuke node
* Space Separated CDL, a Rhythm and Hues cdl format

It is the purpose of CDLConvert to convert ASC CDL information between these
basic formats to further facilitate the ease of exchange of color data within
the Film and TV industries.

**CDLConvert is not associated with the American Society of Cinematographers**

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

# Standard Imports

from argparse import ArgumentParser
import os
import sys

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

# Python 3 compatibility

try:
    xrange
except NameError:  # pragma: no cover
    xrange = range  # pylint: disable=W0622, C0103
try:
    raw_input
except NameError:  # pragma: no cover
    raw_input = input  # pylint: disable=W0622, C0103

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

# INPUT_FORMATS and OUTPUT_FORMATS are globals but located in the MAIN section
# of the file, as they are dispatcher dictionaries that require the functions
# to be parsed by python before the dictionary can be built.

if sys.version_info[0] >= 3:  # pragma: no cover
    enc = lambda x: bytes(x, 'UTF-8')  # pylint: disable=C0103
else:  # pragma: no cover
    enc = lambda x: x  # pylint: disable=C0103

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

# ==============================================================================
# MAIN
# ==============================================================================

# These globals need to be after the parse/write functions but before the
# parse_args.

INPUT_FORMATS = {
    'ale': parse_ale,
    'ccc': parse_ccc,
    'cc': parse_cc,
    'cdl': parse_cdl,
    'flex': parse_flex,
    'rcdl': parse_rnh_cdl,
}

OUTPUT_FORMATS = {
    'cc': write_cc,
    'ccc': write_ccc,
    'cdl': write_cdl,
    'rcdl': write_rnh_cdl,
}

COLLECTION_FORMATS = ['ale', 'ccc', 'cdl', 'flex']
SINGLE_FORMATS = ['cc', 'rcdl']

# ==============================================================================


def parse_args():
    """Uses argparse to parse command line arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "input_file",
        help="the file to be converted"
    )
    parser.add_argument(
        "-i",
        "--input",
        help="specify the filetype to convert from. Use when CDLConvert "
             "cannot determine the filetype automatically. Supported input "  # pylint: disable=C0330
             "formats are: "  # pylint: disable=C0330
             "{inputs}".format(inputs=str(INPUT_FORMATS.keys()))  # pylint: disable=C0330
    )
    parser.add_argument(
        "-o",
        "--output",
        help="specify the filetype to convert to, comma separated lists are "
             "accepted. Defaults to a .cc XML. Supported output formats are: "  # pylint: disable=C0330
             "{outputs}".format(outputs=str(OUTPUT_FORMATS.keys()))  # pylint: disable=C0330
    )
    parser.add_argument(
        "-d",
        "--destination",
        help="specify an output directory to save converted files to. If not "
             "provided will default to ./converted/"  # pylint: disable=C0330
    )
    parser.add_argument(
        "--halt",
        action='store_true',
        help="turns off exception handling default behavior. Turn this on if "
             "you want the conversion process to fail and not continue,"  # pylint: disable=C0330
             "rather than relying on default behavior for bad values. Examples "  # pylint: disable=C0330
             "are clipping negative values to 0.0 for Slope, Power and "  # pylint: disable=C0330
             "Saturation, and automatically generating a new id for a "  # pylint: disable=C0330
             "ColorCorrect if no or a bad id is given."  # pylint: disable=C0330
    )
    parser.add_argument(
        "--no-output",
        action='store_true',
        help="parses all incoming files but no files will be written. Use this "
             "in conjunction with '--halt' and '--check' to try and "  # pylint: disable=C0330
             "track down any oddities observed in the CDLs."  # pylint: disable=C0330
    )
    parser.add_argument(
        "--check",
        action='store_true',
        help="checks all ColorCorrects that were parsed for odd values. Odd "
             "values are any values over 3 or under 0.1 for Slope, Power "  # pylint: disable=C0330
             "and Saturation. For offset, any value over 1 and under -1 is "  # pylint: disable=C0330
             "flagged. Note that depending on the look, these still might "  # pylint: disable=C0330
             "be correct values."  # pylint: disable=C0330
    )

    args = parser.parse_args()

    if args.input:
        if args.input.lower() not in INPUT_FORMATS:
            raise ValueError(
                "The input format: {input} is not supported".format(
                    input=args.input
                )
            )
        else:
            args.input = args.input.lower()

    if args.output:
        # This might be a string separated list of output types.
        # We'll split it, check each against the supported types, convert
        # them to lowercase if not already, and place the resulting list back
        # into args.output
        #
        # TODO: Define and add a new argparse type as described in:
        # http://stackoverflow.com/questions/9978880/python-argument-parser-list-of-list-or-tuple-of-tuples
        output_types = args.output.split(',')
        for i in xrange(len(output_types)):
            if output_types[i].lower() not in OUTPUT_FORMATS.keys():
                raise ValueError(
                    "The output format: {output} is not supported".format(
                        output=output_types[i]
                    )
                )
            else:
                output_types[i] = output_types[i].lower()
        args.output = output_types
    else:
        args.output = ['cc', ]

    if not args.destination:
        args.destination = './converted/'

    if args.halt:
        config.HALT_ON_ERROR = True

    return args

# ==============================================================================


def parse_file(filepath, filetype=None):
    """Determines & uses the correct parser to use on a CDL file"""
    if not filetype:
        filetype = os.path.basename(filepath).split('.')[-1].lower()

    return INPUT_FORMATS[filetype](filepath)

# ==============================================================================


def main():  # pylint: disable=R0912
    """Will figure out input and destination filetypes, then convert"""
    args = parse_args()

    if args.no_output:
        print("Dry run initiated, no files will be written.")

    filepath = os.path.abspath(args.input_file)
    destination_dir = os.path.abspath(args.destination)

    if not os.path.exists(destination_dir):
        print(
            "Destination directory {dir} does not exist.".format(
                dir=destination_dir
            )
        )
        if not args.no_output:
            print("Creating destination directory.")
            os.makedirs(destination_dir)
        else:
            print("--no-output argument provided. Skipping directory creation")

    if not args.input:
        filetype_in = os.path.basename(filepath).split('.')[-1].lower()
    else:
        filetype_in = args.input

    color_decisions = parse_file(filepath, filetype_in)

    def write_single_file(cdl, ext):
        """Writes a single color correction file"""
        cdl.determine_dest(ext, destination_dir)
        print(
            "Writing cdl {id} to {path}".format(
                id=cdl.id,
                path=cdl.file_out
            )
        )
        if not args.no_output:
            OUTPUT_FORMATS[ext](cdl)

    def write_collection_file(col, ext):
        """Writes a collection file"""
        col.type = ext
        col.determine_dest(destination_dir)
        print(
            "Writing collection to {path}".format(
                path=col.file_out
            )
        )
        if not args.no_output:
            OUTPUT_FORMATS[ext](col)

    if color_decisions:
        # Sanity Check
        if args.check:
            if filetype_in in COLLECTION_FORMATS:
                for color_correct in color_decisions.color_corrections:
                    sanity_check(color_correct)
            else:
                sanity_check(color_decisions)

        # Writing
        for ext in args.output:
            if ext in SINGLE_FORMATS:
                if filetype_in in COLLECTION_FORMATS:
                    for color_correct in color_decisions.color_corrections:
                        write_single_file(color_correct, ext)
                else:
                    write_single_file(color_decisions, ext)
            else:
                if filetype_in in COLLECTION_FORMATS:
                    # If we read a collection type, color_decisions is
                    # already a ColorCollection.
                    write_collection_file(color_decisions, ext)
                else:
                    # If we read a single, non-collection file, we need to
                    # create a collection for exporting.
                    #
                    # Since we only read a single file, we can safely use that
                    # filepath as the input_file.
                    #
                    # If we read a group of files, we would want to default to
                    # the generic collection naming.
                    collection = ColorCollection(input_file=filepath)
                    collection.append_child(color_decisions)
                    write_collection_file(collection, ext)

if __name__ == '__main__':  # pragma: no cover
    try:
        main()
    except Exception as err:  # pylint: disable=W0703
        import traceback
        print('Unexpected error encountered:')
        print(err)
        print(traceback.format_exc())
        raw_input('Press enter key to exit')
