#!/usr/bin/env python
"""

CDL Convert
==========

Converts between common ASC CDL (http://en.wikipedia.org/wiki/AscCdl)
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

## Conversions

Currently we support converting from:

* ALE
* CC
* FLEx
* CDL

To:

* CC
* CDL

With support for both from and to expanding in the future.

## Code

CDL Convert is written for Python 2.6, including Python 3.2 and 3.4. Code is
written for PEP 8 compliance, although at the time of this writing function &
variable naming uses camelCasing. Docstrings follow Google code standards.

Development uses Git Flow model.

## License

The MIT License (MIT)

Copyright (c) 2014 Sean Wallitsch

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

Classes
-------

AscCdl
    The base class for the ASC CDL, containing attributes for all ten of the
    color conversion numbers needed to fully describe an ASC CDL.

Functions
---------

"""

# ==============================================================================
# IMPORTS
# ==============================================================================

from argparse import ArgumentParser
from ast import literal_eval
import os
import sys
import xml.etree.ElementTree as ET

# Python 3 compatibility
try:
    xrange
except NameError:  # pragma: no cover
    xrange = range  # pylint: disable=W0622, C0103
try:
    raw_input
except NameError:  # pragma: no cover
    raw_input = input  # pylint: disable=W0622, C0103

from __future__ import print_function

# ==============================================================================
# GLOBALS
# ==============================================================================

__author__ = "Sean Wallitsch"
__copyright__ = "Copyright 2014, Sean Wallitsch"
__credits__ = ["Sean Wallitsch", ]
__license__ = "MIT"
__version__ = "0.4"
__maintainer__ = "Sean Wallitsch"
__email__ = "shidarin@alphamatte.com"
__status__ = "Development"

# INPUT_FORMATS and OUTPUT_FORMATS are globals but located in the MAIN section
# of the file, as they are dispatcher dictionaries that require the functions
# to be parsed by python before the dictionary can be built.

# Because it's getting late and I'm too tired to dive into writing XML today
CC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="{id}">
    <SOPNode>
        <Description></Description>
        <Slope>{slopeR} {slopeG} {slopeB}</Slope>
        <Offset>{offsetR} {offsetG} {offsetB}</Offset>
        <Power>{powerR} {powerG} {powerB}</Power>
    </SOPNode>
    <SatNode>
        <Saturation>{sat}</Saturation>
    </SatNode>
</ColorCorrection>
"""

# Space Separated CDL, a Rhythm & Hues format
CDL = "{slopeR} {slopeG} {slopeB} {offsetR} {offsetG} {offsetB} {powerR} {powerG} {powerB} {sat}\n"  # pylint: disable=C0301

if sys.version_info[0] >= 3:  # pragma: no cover
    enc = lambda x: bytes(x, 'UTF-8')  # pylint: disable=C0103
else:  # pragma: no cover
    enc = lambda x: x  # pylint: disable=C0103

# ==============================================================================
# CLASSES
# ==============================================================================


class AscCdl(object):  # pylint: disable=R0902
    """The basic class for the ASC CDL

    Description
    ~~~~~~~~~~~

    This class contains attributes for all 10 color correction numbers needed
    for an ASC CDL, as well as other metadata like shot names that typically
    accompanies a CDL.

    Because these names are standardized by the ASC and it would be odd to
    change them for the sake of a style convention, the attribute names will
    follow the ASC schema. Descriptions for some of these attributes are
    paraphrasing the ASC CDL documentation. For more information on the ASC CDL
    standard and the operations described below, you can obtain the ASC CDL
    implementor-oriented documentation by sending an email to:
    asc-cdl at theasc dot com

    Order of operations is Slope, Offset, Power, then Saturation.

    Attributes:

        cc_ref : (str)
            This is a reference to another CDL's unique id. Defaults to None.

        desc : (str)
            Comments and notes on the correction. Defaults to None.

        file_in : (str)
            Filepath used to create this CDL.

            Required attribute.

        file_out : (str)
            Filepath this CDL will be written to.

        cc_id : (str)
            Unique XML URI to identify this CDL. Often a shot or sequence name.

            Required attribute.

        input_desc : (str)
            Description of the color space, format and properties of the input
            images. Defaults to None.

        media_ref : (str)
            A reference link to an image or an image sequence. Defaults to None

        offset : [float, float, float]
            An rgb list representing the offset, which raises or lowers the
            input brightness while holding the slope constant.

            The default offset value is 0.0

        power : [float, float, float]
            An rgb list representing the power, which is the only function that
            changes the response curve of the function. Note that this has the
            opposite response to adjustments than a traditional gamma operator.
            These values must be positive.

            The default power value is 1.0

        sat : (float)
            A single float to adjust the relative saturation of all three color
            channels. Calculations use the rec709 implementation of saturation.

        slope : [float, float, float]
            An rgb list representing the slope, which changes the slope of the
            input without shifting the black level established by the offset.
            These values must be positive.

            The default slope value is 1.0

        viewing_desc : (str)
            Viewing device, settings and environment. Defaults to None.

    """

    def __init__(self, cc_id, cdl_file):
        """Inits an instance of an ASC CDL"""

        # Non-ASC attributes
        self._file_in = os.path.abspath(cdl_file)
        self._file_out = None

        # The cc_id is really the only required part of an ASC CDL.
        # Each ID should be unique
        self._cc_id = sanitize(cc_id)

        # ASC_SOP attributes
        self._slope = [1.0, 1.0, 1.0]
        self._offset = [0.0, 0.0, 0.0]
        self._power = [1.0, 1.0, 1.0]

        # ASC_SAT attribute
        self._sat = 1.0

        # Metadata
        self.cc_ref = None
        self.desc = None
        self.input_desc = None
        self.media_ref = None
        self.viewing_desc = None

    # Properties ==============================================================

    @property
    def file_in(self):
        """Returns the absolute filepath to the input file"""
        return self._file_in

    @property
    def file_out(self):
        """Returns a theoretical absolute filepath based on output ext"""
        return self._file_out

    @property
    def cc_id(self):
        """Returns unique color correction id field"""
        return self._cc_id

    @property
    def offset(self):
        """Returns list of RGB offset values"""
        return self._offset

    @offset.setter
    def offset(self, offset_rgb):
        """Runs tests and converts offset rgb values before setting"""
        # Offset must be a list with 3 values.
        try:
            assert len(offset_rgb) == 3
        except AssertionError:
            raise ValueError("Offset must be set with all three RGB values")
        try:
            assert type(offset_rgb) in [list, tuple]
        except AssertionError:
            raise TypeError("Offset must be a list or tuple")

        offset_rgb = list(offset_rgb)

        for i in xrange(len(offset_rgb)):
            try:
                offset_rgb[i] = float(offset_rgb[i])
            except ValueError:
                raise TypeError("Offset values must be ints or floats")

        self._offset = offset_rgb

    @property
    def power(self):
        """Returns list of RGB power values"""
        return self._power

    @power.setter
    def power(self, power_rgb):
        """Runs tests and converts power rgb values before setting"""
        # Slope must be a list with 3 values, all of which are positive floats
        try:
            assert len(power_rgb) == 3
        except AssertionError:
            raise ValueError("Power must be set with all three RGB values")
        try:
            assert type(power_rgb) in [list, tuple]
        except AssertionError:
            raise TypeError("Power must be a list or tuple")

        power_rgb = list(power_rgb)

        for i in xrange(len(power_rgb)):
            try:
                power_rgb[i] = float(power_rgb[i])
            except ValueError:
                raise TypeError("Power values must be ints or floats")
            try:
                assert power_rgb[i] >= 0.0
            except AssertionError:
                raise ValueError("Power values must not be negative")

        self._power = power_rgb

    @property
    def slope(self):
        """Returns list of RGB slope values"""
        return self._slope

    @slope.setter
    def slope(self, slope_rgb):
        """Runs tests and converts slope rgb values before setting"""
        # Slope must be a list with 3 values, all of which are positive floats
        try:
            assert len(slope_rgb) == 3
        except AssertionError:
            raise ValueError("Slope must be set with all three RGB values")
        try:
            assert type(slope_rgb) in [list, tuple]
        except AssertionError:
            raise TypeError("Slope must be a list or tuple")

        slope_rgb = list(slope_rgb)

        for i in xrange(len(slope_rgb)):
            try:
                slope_rgb[i] = float(slope_rgb[i])
            except ValueError:
                raise TypeError("Slope values must be ints or floats")
            try:
                assert slope_rgb[i] >= 0.0
            except AssertionError:
                raise ValueError("Slope values must not be negative")

        self._slope = slope_rgb

    @property
    def sat(self):
        """Returns float value for saturation"""
        return self._sat

    @sat.setter
    def sat(self, sat_value):
        """Makes sure provided sat value is a positive float"""
        try:
            sat_value = float(sat_value)
        except ValueError:
            raise TypeError("Saturation must be a float or int")
        try:
            assert sat_value >= 0.0
        except AssertionError:
            raise ValueError("Saturation must be a positive value")

        self._sat = float(sat_value)

    # methods =================================================================

    def determine_dest(self, output):
        """Determines the destination file and sets it on the cdl"""

        directory = os.path.dirname(self.file_in)

        filename = "{id}.{ext}".format(id=self.cc_id, ext=output)

        self._file_out = os.path.join(directory, filename)

# ==============================================================================
# FUNCTIONS
# ==============================================================================


def parse_ale(edl_file):
    """Parses an Avid Log Exchange (ALE) file for CDLs

    Args:
        file : (str)
            The filepath to the ALE EDL

    Returns:
        [<AscCdl>]
            A list of CDL objects retrieved from the ALE

    Raises:
        N/A

    An ALE file is traditionally gathered during a telecine transfer using
    standard ASCII characters. Each line theoretically represents a single
    clip/take/shot.

    Each field of data is tab delineated. We'll be searching for the ASC_SOP,
    ASC_SAT fields, alone with the standard Scan Filename fields.

    The Data line indicates that all the following lines are comprised of
    shot information.

    """
    # We'll use these variables to indicate what sections of the file we are in
    column = False
    data = False

    # We'll use these variables to indicate column indexes
    asc_sat_index = None
    asc_sop_index = None
    scan_filename = None

    cdls = []

    with open(edl_file, 'r') as edl:
        lines = edl.readlines()
        for line in lines:
            if line.startswith('Column'):
                column = True
                continue
            elif line.startswith('Data'):
                data = True
                continue
            elif column:
                columns = line.split('\t')
                asc_sat_index = columns.index('ASC_SAT')
                asc_sop_index = columns.index('ASC_SOP')
                scan_filename = columns.index('Scan Filename')
                column = False
            elif data:
                cdl_data = line.split('\t')

                sat = cdl_data[asc_sat_index]
                sop = cdl_data[asc_sop_index]
                cc_id = cdl_data[scan_filename]

                # Determine slope, offset and power from sop
                # sop should look like:
                # (1.4 1.9 1.7)(-0.1 -0.26 -0.20)(0.87 1.0 1.32)
                sop = sop.replace(' ', ', ')
                sop = sop.replace(')(', ')|(')
                sop = sop.split('|')
                slope = literal_eval(sop[0])
                offset = literal_eval(sop[1])
                power = literal_eval(sop[2])

                cdl = AscCdl(cc_id, edl_file)

                cdl.sat = float(sat)
                cdl.slope = slope
                cdl.offset = offset
                cdl.power = power

                cdls.append(cdl)

    return cdls

# ==============================================================================


def parse_cc(cdl_file):
    """Parses a .cc file for ASC CDL information

    Args:
        file : (str)
            The filepath to the CC

    Return:
        [<AscCdl>]
            A list of CDL objects retrieved from the CC

    Raises:
        N/A

    A CC file is really only a single element of a larger CDL or CCC XML file,
    but this element has become a popular way of passing around single shot
    CDLs, rather than the much bulkier CDL file.

    A sample CC XML file has text like:

    <ColorCorrection id="cc03340">
        <SOPNode>
            <Description>change +1 red, contrast boost</Description>
            <Slope>1.2 1.3 1.4</Slope>
            <Offset>0.3 0.0 0.0</Offset>
            <Power>1.0 1.0 1.0</Power>
        </SOPNode>
        <SatNode>
            <Saturation>1.2</Saturation>
        </SatNode>
    </ColorCorrection>

    We'll check to see if each of these elements exist, and override the AscCdl
    defaults if we find them.
    """
    tree = ET.parse(cdl_file)
    root = tree.getroot()

    cdls = []

    if not root.tag == 'ColorCorrection':
        # This is not a CC file...
        raise ValueError('CC parsed but no ColorCorrection found')

    try:
        cc_id = root.attrib['id']
    except KeyError:
        raise ValueError('No id found on ColorCorrection')

    cdl = AscCdl(cc_id, cdl_file)
    # Neither the SOP nor the Sat node actually HAVE to exist, it literally
    # could just be an id and that's it.
    sop = root.find('SOPNode')
    sat = root.find('SatNode')

    # We make a specific comparison against None, because etree creates errors
    # otherwise (future behavior is changing)
    if sop is not None:
        desc = sop.find('Description')
        slope = sop.find('Slope')
        offset = sop.find('Offset')
        power = sop.find('Power')

        if desc is not None:
            cdl.desc = desc.text
        if slope is not None:
            cdl.slope = slope.text.split()
        if offset is not None:
            cdl.offset = offset.text.split()
        if power is not None:
            cdl.power = power.text.split()
    if sat is not None:
        sat_value = sat.find('Saturation')

        if sat_value is not None:
            cdl.sat = sat_value.text

    cdls.append(cdl)

    return cdls


# ==============================================================================

def parse_flex(edl_file):
    """Parses a DaVinci FLEx telecine EDL for ASC CDL information.

    Args:
        file : (str)
            The filepath to the FLEx EDL

    Return:
        [<AscCdl>]
            A list of CDL objects retrieved from the FLEx

    Raises:
        N/A

    The DaVinci FLEx EDL is an odd duck, it's information conveyed via an
    extremely strict line & character addressing system.

    Each line must begin with a line number header that indicated what type
    of information the line contains, with line number 100 indicating the
    start of a new shot/take. Lines 000-099 contain session information.

    Within each line, important information is constricted to a certain
    range of characters, rather than space or comma separated like in an
    ALE EDL.

    Some line numbers we care about, and the character indexes:

        010 Project Title
            10-79 Title
        100 Indicates the start of a new 'record' (shot/take)
        110 Slate Information
            10-17 Scene
            24-31 Take ID
            42-49 Camera Reel ID
        701 ASC SOP (This entry can be safely space separated)
        702 ASC SAT (This entry can be safely space separated)

    We'll try and default to using the Slate information to derive the
    resultant filename, however that information is optional. If no
    slate information is found, we'll iterate up at the end of the title.
    If no title information is found, we'll have to iterate up on the
    actual input filename, which is far from ideal.

    """

    cdls = []

    with open(edl_file, 'r') as edl:
        lines = edl.readlines()

        filename = os.path.basename(edl_file).split('.')[0]

        # TODO: Make title, scene, take and reel a list or dict
        title = None
        scene = None
        take = None
        reel = None

        slope = []
        offset = []
        power = []
        sat = None

        for line in lines:
            if line.startswith('100'):
                # This is the start of a take/shot
                # We need to dump the previous records to a CDL
                # Then clear the records.
                if scene:
                    cc_id = scene
                    if take:
                        cc_id += '_' + take
                        if reel:
                            cc_id += '_' + reel
                else:
                    if title:
                        cc_id = title + str(len(cdls) + 1).rjust(3, '0')
                    else:
                        cc_id = filename + str(len(cdls) + 1).rjust(3, '0')

                # If we already have slope/offset/power:
                if slope and offset and power:
                    # Make a cdl, add it to the cdls list
                    cdl = AscCdl(cc_id, edl_file)

                    cdl.slope = slope
                    cdl.offset = offset
                    cdl.power = power

                    if sat:
                        cdl.sat = sat
                    if title:
                        cdl.desc = title

                    cdls.append(cdl)

                scene = None
                take = None
                reel = None

                slope = []
                offset = []
                power = []
                sat = None

            elif line.startswith('010'):
                # Title Line
                # 10-79 Title
                title = line[10:80].strip()
            elif line.startswith('110'):
                # Slate Information
                # 10-17 Scene
                # 24-31 Take ID
                # 42-49 Camera Reel ID
                scene = line[10:18].strip()
                take = line[24:32].strip()
                reel = line[42:50].strip()
            elif line.startswith('701'):
                # ASC SOP
                # 701 ASC_SOP(# # #)(-# -# -#)(# # #)
                slope = line[12:32].split()
                offset = line[34:57].split()
                power = line[59:79].split()
                for i in xrange(3):
                    slope[i] = float(slope[i])
                    offset[i] = float(offset[i])
                    power[i] = float(power[i])
            elif line.startswith('702'):
                # ASC SAT
                # 702 ASC_SAT ######
                sat = float(line.split()[-1])

    # We need to dump the last record to the cdl list
    if scene:
        cc_id = scene
        if take:
            cc_id += '_' + take
            if reel:
                cc_id += '_' + reel
    else:
        if title:
            cc_id = title + str(len(cdls) + 1).rjust(3, '0')
        else:
            cc_id = filename + str(len(cdls) + 1).rjust(3, '0')

    # If we have slope/offset/power:
    if slope and offset and power:
        # Make a cdl, add it to the cdls list
        cdl = AscCdl(cc_id, edl_file)

        cdl.slope = slope
        cdl.offset = offset
        cdl.power = power

        if sat:
            cdl.sat = sat
        if title:
            cdl.desc = title

        cdls.append(cdl)

    return cdls


# ==============================================================================


def parse_cdl(cdl_file):
    """Parses a space separated .cdl file for ASC CDL information.

    Args:
        file : (str)
            The filepath to the CDL

    Returns:
        [<AscCdl>]
            A list with only the single CDL object retrieved from the SS CDL

    Raises:
        N/A

    A space separated cdl file is an internal Rhythm & Hues format used by
    the Rhythm & Hues for displaying shot level and sequence level within
    their internally developed playback software.

    The file is a simple file consisting of one line. That line has 10, space
    separated elements that correspond to the ten ASC CDL elements in order of
    operations.

    SlopeR SlopeG SlopeB OffsetR OffsetG OffsetB PowerR PowerG PowerB Sat

    """
    # Although we only parse one cdl file, we still want to return a list
    cdls = []

    with open(cdl_file, 'r') as cdl_f:
        # We only need to read the first line
        line = cdl_f.readline()
        line = line.split()

        # The filename without extension will become the id
        filename = os.path.basename(cdl_file).split('.')[0]

        slope = [line[0], line[1], line[2]]
        offset = [line[3], line[4], line[5]]
        power = [line[6], line[7], line[8]]

        sat = line[9]

        cdl = AscCdl(filename, cdl_file)

        cdl.slope = slope
        cdl.offset = offset
        cdl.power = power
        cdl.sat = sat

        cdls.append(cdl)

    return cdls

# ==============================================================================


def sanitize(name):
    """Removes any characters in string name that aren't alnum or in '_.'"""
    import re
    # Replace any spaces with underscores
    name = name.replace(' ', '_')
    # If we start our string with an underscore or period, remove it
    if name[0] in '_.':
        name = name[1:]
    # a-z is all lowercase
    # A-Z is all uppercase
    # 0-9 is all digits
    # \. is an escaped period
    # _ is an underscore
    # Put them together, negate them by leading with an ^
    # and our compiler will mark every non alnum, non ., _ character
    pattern = re.compile(r'[^a-zA-Z0-9\._]+')
    # Then we sub them with nothing
    fixed = pattern.sub('', name)

    return fixed

# ==============================================================================


def write_cc(cdl):
    """Writes the AscCdl to a .cc file"""

    xml = CC_XML.format(
        id=cdl.cc_id,
        slopeR=cdl.slope[0],
        slopeG=cdl.slope[1],
        slopeB=cdl.slope[2],
        offsetR=cdl.offset[0],
        offsetG=cdl.offset[1],
        offsetB=cdl.offset[2],
        powerR=cdl.power[0],
        powerG=cdl.power[1],
        powerB=cdl.power[2],
        sat=cdl.sat
    )

    with open(cdl.file_out, 'wb') as cdl_f:
        cdl_f.write(enc(xml))

# ==============================================================================


def write_cdl(cdl):
    """Writes the AscCdl to a space separated .cdl file"""

    ss_cdl = CDL.format(
        slopeR=cdl.slope[0],
        slopeG=cdl.slope[1],
        slopeB=cdl.slope[2],
        offsetR=cdl.offset[0],
        offsetG=cdl.offset[1],
        offsetB=cdl.offset[2],
        powerR=cdl.power[0],
        powerG=cdl.power[1],
        powerB=cdl.power[2],
        sat=cdl.sat
    )

    with open(cdl.file_out, 'wb') as cdl_f:
        cdl_f.write(enc(ss_cdl))

# ==============================================================================
# MAIN
# ==============================================================================

# These globals need to be after the parse/write functions but before the
# parse_args.

INPUT_FORMATS = {
    'ale': parse_ale,
    'cc': parse_cc,
    'cdl': parse_cdl,
    'flex': parse_flex,
}

OUTPUT_FORMATS = {
    'cc': write_cc,
    'cdl': write_cdl,
}

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
             "cannot determine the filetype automatically. Supported input "
             "formats are: "
             "{inputs}".format(inputs=str(INPUT_FORMATS.keys()))
    )
    parser.add_argument(
        "-o",
        "--output",
        help="specify the filetype to convert to, comma separated lists are "
             "accepted. Defaults to a .cc XML. Supported output formats are: "
             "{outputs}".format(outputs=str(OUTPUT_FORMATS.keys()))
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

    return args

# ==============================================================================


def main():
    """Will figure out input and destination filetypes, then convert"""
    args = parse_args()

    filepath = os.path.abspath(args.input_file)

    if not args.input:
        filetype_in = os.path.basename(filepath).split('.')[-1].lower()
    else:
        filetype_in = args.input

    cdls = INPUT_FORMATS[filetype_in](filepath)

    if cdls:
        for cdl in cdls:
            for ext in args.output:
                cdl.determine_dest(ext)
                print(
                    "Writing cdl {id} to {path}".format(
                        id=cdl.cc_id,
                        path=cdl.file_out
                    )
                )
                OUTPUT_FORMATS[ext](cdl)

if __name__ == '__main__':  # pragma: no cover
    try:
        main()
    except Exception as err:  # pylint: disable=W0703
        print('Unexpected error encountered:')
        print(err)
        raw_input('Press enter key to exit')
