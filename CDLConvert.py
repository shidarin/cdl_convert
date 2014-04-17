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
    color conversion numbers needed to fully describe an ASC CDL

Functions
---------

"""

#===============================================================================
# IMPORTS
#===============================================================================

#===============================================================================
# CLASSES
#===============================================================================

#===============================================================================
# FUNCTIONS
#===============================================================================

#===============================================================================
# MAIN
#===============================================================================

def main():
    pass

if __name__ == '__main__':
    try:
        main()
    except Exception, err:
        print 'Unexpected error encountered:'
        print err
        raw_input('Press enter key to exit')