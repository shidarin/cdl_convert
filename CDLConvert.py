#/usr/bin/python
# CDL Convert
# Converts between common ASC CDL formats
# By Sean Wallitsch, 2014/04/16

"""

CDLConvert
==========

Converts between common [ASC CDL](http://en.wikipedia.org/wiki/ASC_CDL)
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

It is the purpose of CDLConvert to convert ASC CDL information between these
basic formats to further facilitate the ease of exchange of color data within
the Film and TV industries.

**CDLConvert is not associated with the American Society of Cinematographers**

## Conversions

Currently we support converting from:

* ALE
* CC
* CCC
* OCIOCDLTransform

To:

* CC
* OCIOCDLTransform

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

ASC_CDL
    The base class for the ASC CDL, containing attributes for all ten of the
    color conversion numbers needed to fully describe an ASC CDL.

Functions
---------

"""

#===============================================================================
# IMPORTS
#===============================================================================

from argparse import ArgumentParser

#===============================================================================
# GLOBALS
#===============================================================================

INPUT_FORMATS = [
    'cc',
]

OUTPUT_FORMATS = [
    'cc',
]

#===============================================================================
# CLASSES
#===============================================================================

class ASC_CDL(object):
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

    def __init__(self, id):
        """Inits an instance of an ASC CDL"""

        # Non-ASC attributes
        self.fileIn = None
        self.fileOut = None

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

        self._offset = list(offsetRGB)

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

        for i in powerRGB:
            try:
                assert i >= 0.0
            except AssertionError:
                raise ValueError("Power values must not be negative")

        self._power = list(powerRGB)

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

        for i in slopeRGB:
            try:
                assert i >= 0.0
            except AssertionError:
                raise ValueError("Slope values must not be negative")

        self._slope = list(slopeRGB)

    @property
    def sat(self):
        return self._sat

    @sat.setter
    def sat(self, satValue):
        try:
            assert satValue >= 0.0
        except AssertionError:
            raise ValueError("Saturation must be a positive value")
        else:
            self._sat = float(satValue)

#===============================================================================
# FUNCTIONS
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
             "{inputs}".format(inputs=str(INPUT_FORMATS))
    )
    parser.add_argument(
        "-o",
        "--output",
        help="specify the filetype to convert to. Defaults to a .cc XML. "
             "Supported output formats are: "
             "{outputs}".format(outputs=str(OUTPUT_FORMATS))
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
        if args.output.lower() not in OUTPUT_FORMATS:
            raise ValueError(
                "The output format: {output} is not supported".format(
                    output=args.output
                )
            )
        else:
            args.output = args.output.lower()

    return args

#===============================================================================
# MAIN
#===============================================================================

def main():
    args = parseArgs()

    print args.input_file
    if args.input:
        print args.input
    if args.output:
        print args.output

if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        print 'Unexpected error encountered:'
        print err
        raw_input('Press enter key to exit')