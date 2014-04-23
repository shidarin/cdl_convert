CDL Convert
==========

[![Build Status](https://travis-ci.org/shidarin/cdl_convert.svg?branch=develop)](https://travis-ci.org/shidarin/cdl_convert)[![Coverage Status](https://coveralls.io/repos/shidarin/cdl_convert/badge.png?branch=develop)](https://coveralls.io/r/shidarin/cdl_convert?branch=develop)

Converts between common [ASC CDL](http://en.wikipedia.org/wiki/ASC_CDL)
formats. The [American Society of Cinematographers](http://www.theasc.com/) Color
Decision List (ASC CDL, or CDL for short) is a schema to simplify the process
of interchanging color data between various programs and facilities.

The ASC has defined schemas for including the 10 basic numbers in 5 different
formats:

* Avid Log Exchange (ALE)
* Film Log EDL Exchange (FLEx)
* CMX EDL
* XML Color Correction (cc)
* XML Color Correction Collection (ccc)

Unofficial Formats:

* OCIOCDLTransform, a [Foundry Nuke](www.thefoundry.co.uk/nuke/) node
* Space separated CDL, a Rhythm & Hues internal cdl format

It is the purpose of CDL Convert to convert ASC CDL information between these
basic formats to further facilitate the ease of exchange of color data within
the Film and TV industries.

**CDL Convert is not associated with the American Society of Cinematographers**

## Conversions

Currently we support converting from:

* ALE
* CC
* FLEx
* CDL

To:

* CC
* Space Separated CDL

With support for both from and to expanding in the future.

## Code

CDL Convert is written for Python 2.6, including Python 3.2 and 3.4. Code is
written for PEP 8 compliance, although at the time of this writing function &
variable naming uses camelCasing. Docstrings follow Google code standards.

Development uses Git Flow model.

## License

Basic MIT License. If you use or modify the project I would love to hear from
you. For more information on the license, please see the LICENSE file that
accompanies the project.