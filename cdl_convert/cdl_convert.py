#!/usr/bin/env python
"""

CDL Convert Cdl_Convert
=======================

Contains the script functions for using cdl_convert as a script.

## Public Functions

    parse_args()
        Uses argparse to parse the command line args provided to cdl_convert.

    main()
        Main script runner, this calls parse_args, determines the input and
        output extensions, calls the correct parser and determines how to
        fulfill the output requested.

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

# Standard Imports

from argparse import ArgumentParser
import os

# cdl_convert imports

from . import config, parse, write
from .collection import ColorCollection
from .utils import sanity_check

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
# EXPORTS
# ==============================================================================

__all__ = []

# ==============================================================================
# PUBLIC FUNCTIONS
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
             "{inputs}".format(inputs=str(parse.INPUT_FORMATS.keys()))  # pylint: disable=C0330
    )
    parser.add_argument(
        "-o",
        "--output",
        help="specify the filetype to convert to, comma separated lists are "
             "accepted. Defaults to a .cc XML. Supported output formats are: "  # pylint: disable=C0330
             "{outputs}".format(outputs=str(write.OUTPUT_FORMATS.keys()))  # pylint: disable=C0330
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
    parser.add_argument(
        "--single",
        action='store_true',
        help="only write a single color decision per file when given collection"
             "formats. This means that a single input CDL will export multiple"
             "CDL files, one per color decision."
    )

    args = parser.parse_args()

    if args.input:
        if args.input.lower() not in parse.INPUT_FORMATS:
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
            if output_types[i].lower() not in write.OUTPUT_FORMATS.keys():
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
# MAIN
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

    color_decisions = parse.parse_file(filepath, filetype_in)

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
            write.OUTPUT_FORMATS[ext](cdl)

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
            write.OUTPUT_FORMATS[ext](col)

    if color_decisions:
        # Sanity Check
        if args.check:
            if filetype_in in config.COLLECTION_FORMATS:
                for color_correct in color_decisions.color_corrections:
                    sanity_check(color_correct)
            else:
                sanity_check(color_decisions)

        # Writing
        for ext in args.output:
            if ext in config.SINGLE_FORMATS or args.single:
                if filetype_in in config.COLLECTION_FORMATS:
                    for color_correct in color_decisions.color_corrections:
                        write_single_file(color_correct, ext)
                else:
                    write_single_file(color_decisions, ext)
            else:
                if filetype_in in config.COLLECTION_FORMATS:
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
