#/usr/bin/python
# CDL Convert
# Converts between common ASC CDL formats
# By Sean Wallitsch, 2014/04/16

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
* CCC
* OCIOCDLTransform (nk)
* CDL

To:

* CC
* OCIOCDLTransform (nk)
* CDL

With support for both from and to expanding in the future.

## Code

CDLConvert is written for Python 2.6 and up, with support for Python 3 coming
in the future. Code is written for PEP 8 compliance, although at the time of
this writing function & variable naming uses camelCasing. Docstrings follow
Google code standards.

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

#===============================================================================
# IMPORTS
#===============================================================================

from argparse import ArgumentParser
from ast import literal_eval
import os

#===============================================================================
# GLOBALS
#===============================================================================

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
CDL = """{slopeR} {slopeG} {slopeB} {offsetR} {offsetG} {offsetB} {powerR} {powerG} {powerB} {sat}
"""

#===============================================================================
# CLASSES
#===============================================================================

class AscCdl(object):
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

        colorCorrectionRef : (str)
            This is a reference to another CDL's unique id. Defaults to None.

        description : (str)
            Comments and notes on the correction. Defaults to None.

        fileIn : (str)
            Filepath used to create this CDL.

            Required attribute.

        fileOut : (str)
            Filepath this CDL will be written to.

        id : (str)
            Unique XML URI to identify this CDL. Often  a shot or sequence name.

            Required attribute.

        inputDescription : (str)
            Description of the color space, format and properties of the input
            images. Defaults to None.

        mediaRef : (str)
            A reference link to an image or an image sequence. Defaults to None.

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

        viewingDescription : (str)
            Viewing device, settings and environment. Defaults to None.

    """

    def __init__(self, id, file):
        """Inits an instance of an ASC CDL"""

        # Non-ASC attributes
        self._fileIn = os.path.abspath(file)
        self._fileOut = None

        # The id is really the only required part of an ASC CDL.
        # Each ID should be unique
        self._id = id

        # ASC_SOP attributes
        self._slope = [1.0, 1.0, 1.0]
        self._offset = [0.0, 0.0, 0.0]
        self._power = [1.0, 1.0, 1.0]

        # ASC_SAT attribute
        self._sat = 1.0

        # Metadata
        self.colorCorrectionRef = None
        self.description = None
        self.inputDescription = None
        self.mediaRef = None
        self.viewingDescription = None

    # Properties ===============================================================

    @property
    def fileIn(self):
        return self._fileIn

    @property
    def fileOut(self):
        return self._fileOut

    @property
    def id(self):
        return self._id

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offsetRGB):
        # Offset must be a list with 3 values.
        try:
            assert len(offsetRGB) == 3
        except AssertionError:
            raise ValueError("Offset must be set with all three RGB values")
        try:
            assert type(offsetRGB) in [list, tuple]
        except AssertionError:
            raise TypeError("Offset must be a list or tuple")

        offsetRGB = list(offsetRGB)

        for i in xrange(len(offsetRGB)):
            try:
                offsetRGB[i] = float(offsetRGB[i])
            except ValueError:
                raise TypeError("Offset values must be ints or floats")

        self._offset = offsetRGB

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, powerRGB):
        # Slope must be a list with 3 values, all of which are positive floats
        try:
            assert len(powerRGB) == 3
        except AssertionError:
            raise ValueError("Power must be set with all three RGB values")
        try:
            assert type(powerRGB) in [list, tuple]
        except AssertionError:
            raise TypeError("Power must be a list or tuple")

        powerRGB = list(powerRGB)

        for i in xrange(len(powerRGB)):
            try:
                powerRGB[i] = float(powerRGB[i])
            except ValueError:
                raise TypeError("Power values must be ints or floats")
            try:
                assert powerRGB[i] >= 0.0
            except AssertionError:
                raise ValueError("Power values must not be negative")

        self._power = powerRGB

    @property
    def slope(self):
        return self._slope

    @slope.setter
    def slope(self, slopeRGB):
        # Slope must be a list with 3 values, all of which are positive floats
        try:
            assert len(slopeRGB) == 3
        except AssertionError:
            raise ValueError("Slope must be set with all three RGB values")
        try:
            assert type(slopeRGB) in [list, tuple]
        except AssertionError:
            raise TypeError("Slope must be a list or tuple")

        slopeRGB = list(slopeRGB)

        for i in xrange(len(slopeRGB)):
            try:
                slopeRGB[i] = float(slopeRGB[i])
            except ValueError:
                raise TypeError("Slope values must be ints or floats")
            try:
                assert slopeRGB[i] >= 0.0
            except AssertionError:
                raise ValueError("Slope values must not be negative")

        self._slope = slopeRGB

    @property
    def sat(self):
        return self._sat

    @sat.setter
    def sat(self, satValue):
        try:
            satValue = float(satValue)
        except ValueError:
            raise TypeError("Saturation must be a float or int")
        try:
            assert satValue >= 0.0
        except AssertionError:
            raise ValueError("Saturation must be a positive value")

        self._sat = float(satValue)

    #===========================================================================
    # METHODS
    #===========================================================================

    def determineDest(self, output):
        """Determines the destination file and sets it on the cdl"""

        dir = os.path.dirname(self.fileIn)

        filename = "{id}.{ext}".format(id=self.id, ext=output)

        self._fileOut = os.path.join(dir, filename)

#===============================================================================
# FUNCTIONS
#===============================================================================

def parseALE(file):
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
    ASC_SAT_I = None
    ASC_SOP_I = None
    scan_filename = None

    cdls = []

    with open(file, 'rb') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('Column'):
                column = True
                continue
            elif line.startswith('Data'):
                data = True
                continue
            elif column:
                columns = line.split('\t')
                ASC_SAT_I = columns.index('ASC_SAT')
                ASC_SOP_I = columns.index('ASC_SOP')
                scan_filename = columns.index('Scan Filename')
                column = False
            elif data:
                cdlData = line.split('\t')

                sat = cdlData[ASC_SAT_I]
                sop = cdlData[ASC_SOP_I]
                id = cdlData[scan_filename]

                # Determine slope, offset and power from sop
                # sop should look like:
                # (1.4 1.9 1.7)(-0.1 -0.26 -0.20)(0.87 1.0 1.32)
                sop = sop.replace(' ', ', ')
                sop = sop.replace(')(', ')|(')
                sop = sop.split('|')
                slope = literal_eval(sop[0])
                offset = literal_eval(sop[1])
                power = literal_eval(sop[2])

                cdl = AscCdl(id, file)

                cdl.sat = float(sat)
                cdl.slope = slope
                cdl.offset = offset
                cdl.power = power

                cdls.append(cdl)

    return cdls

#===============================================================================

def parseFLEx(file):
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

    with open(file, 'rb') as f:
        lines = f.readlines()

        filename = os.path.basename(file).split('.')[0]

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
                    id = scene
                    if take:
                        id += '_' + take
                        if reel:
                            id += '_' + reel
                else:
                    if title:
                        id = title
                    else:
                        id = filename + str(len(cdls) + 1)

                # If we already have slope/offset/power:
                if slope and offset and power:
                    # Make a cdl, add it to the cdls list
                    cdl = AscCdl(id, file)

                    cdl.slope = slope
                    cdl.offset = offset
                    cdl.power = power

                    if sat:
                        cdl.sat = sat
                    if title:
                        cdl.description = title

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
        id = scene
        if take:
            id += '_' + take
            if reel:
                id += '_' + reel
    else:
        if title:
            id = title
        else:
            id = filename + str(len(cdls) + 1)

    # If we have slope/offset/power:
    if slope and offset and power:
        # Make a cdl, add it to the cdls list
        cdl = AscCdl(id, file)

        cdl.slope = slope
        cdl.offset = offset
        cdl.power = power

        if sat:
            cdl.sat = sat
        if title:
            cdl.description = title

        cdls.append(cdl)

    return cdls


#===============================================================================

def parseCDL(file):
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

    with open(file, 'rb') as f:
        # We only need to read the first line
        line = f.readline()
        line = line.split()

        # The filename without extension will become the id
        filename = os.path.basename(file).split('.')[0]

        slope = [line[0], line[1], line[2]]
        offset = [line[3], line[4], line[5]]
        power = [line[6], line[7], line[8]]

        sat = line[9]

        cdl = AscCdl(filename, file)

        cdl.slope = slope
        cdl.offset = offset
        cdl.power = power
        cdl.sat = sat

        cdls.append(cdl)

    return cdls

#===============================================================================

def sanitize(name):
    """Removes any characters in string name that aren't alnum or in '_.'"""
    from re import compile
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
    pattern = compile(r'[^a-zA-Z0-9\._]+')
    # Then we sub them with nothing
    fixed = pattern.sub('', name)

    return fixed

#===============================================================================

def writeCC(cdl):
    """Writes the AscCdl to a .cc file"""

    xml = CC_XML.format(
        id=cdl.id,
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

    with open(cdl.fileOut, 'wb') as f:
        f.write(xml)

#===============================================================================

def writeCDL(cdl):
    """Writes the AscCdl to a space separated .cdl file"""

    ssCdl = CDL.format(
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

    with open(cdl.fileOut, 'wb') as f:
        f.write(ssCdl)

#===============================================================================
# MAIN
#===============================================================================

# These globals need to be after the parse/write functions but before the
# parseArgs.

INPUT_FORMATS = {
    'ale': parseALE,
    'flex': parseFLEx,
    'cdl': parseCDL,
}

OUTPUT_FORMATS = {
    'cc': writeCC,
    'cdl': writeCDL,
}

#===============================================================================

def parseArgs():
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
        outputTypes = args.output.split(',')
        for i in xrange(len(outputTypes)):
            if outputTypes[i].lower() not in OUTPUT_FORMATS:
                raise ValueError(
                    "The output format: {output} is not supported".format(
                        output=outputTypes[i]
                    )
                )
            else:
                outputTypes[i] = outputTypes[i].lower()
        args.output = outputTypes
    else:
        args.output = ['cc', ]

    return args

#===============================================================================

def main():
    args = parseArgs()

    filepath = os.path.abspath(args.input_file)

    if not args.input:
        filetypeIn = os.path.basename(filepath).split('.')[-1]
    else:
        filetypeIn = args.input

    cdls = INPUT_FORMATS[filetypeIn](filepath)

    for cdl in cdls:
        for ext in args.output:
            cdl.determineDest(ext)
            print "Writing cdl {id} to {path}".format(
                id=cdl.id,
                path=cdl.fileOut
            )
            OUTPUT_FORMATS[ext](cdl)

if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        print 'Unexpected error encountered:'
        print err
        raw_input('Press enter key to exit')