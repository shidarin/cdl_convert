# cdl_convert

## Project Info

[![PyPI Version](https://badge.fury.io/py/cdl_convert.png)](http://badge.fury.io/py/cdl_convert)
[![Build Status](https://github.com/shidarin/cdl_convert/workflows/CI/badge.svg)](https://github.com/shidarin/cdl_convert/actions)
[![Coverage](https://codecov.io/gh/shidarin/cdl_convert/graph/badge.svg?token=TIFtNj7SmO)](https://codecov.io/gh/shidarin/cdl_convert)

- **Name:** cdl_convert
- **Version:** {sub-ref}`release`
- **Author/Maintainer:** Sean Wallitsch
- **Email:** shidarin@alphamatte.com
- **License:** MIT
- **Status:** Development
- **Docs:** <http://cdl-convert.readthedocs.org/>
- **GitHub:** <https://github.com/shidarin/cdl_convert>
- **PyPI:** <https://pypi.org/project/cdl_convert/>
- **Python Versions:** 3.11, 3.12, 3.13, 3.14

## Introduction

`cdl_convert` converts between common [ASC CDL](http://en.wikipedia.org/wiki/ASC_CDL) formats. The [American Society of Cinematographers](http://www.theasc.com/) Color Decision List (ASC CDL, or CDL for short) is a schema to simplify the process of interchanging color data between various programs and facilities.

The ASC has defined schemas for including the 10 basic numbers in 6 different formats:

- Avid Log Exchange (ALE)
- Film Log EDL Exchange (FLEx)
- CMX EDL
- XML Color Correction (cc)
- XML Color Correction Collection (ccc)
- XML Color Decision List (cdl)

Unofficial Formats:

- OpenTimelineIO (OTIO) timeline files with embedded CDL metadata
- Nuke's OCIOCDLTransform nodes, from [The Foundry Nuke](http://www.thefoundry.co.uk/nuke/)
- Space separated CDL (RCDL), a Rhythm & Hues internal cdl format

`cdl_convert` converts ASC CDL information between these basic formats to further facilitate the ease of exchange of color data within the Film and TV industries.

`cdl_convert` supports parsing ALE, FLEx, CC, CCC, CDL, CMX EDL, Nuke (.nk), OTIO, and RCDL. We can write out CC, CCC, CDL, Nuke (.nk), and RCDL.

`cdl_convert` uses the Academy Software Foundation's [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) project for reading ALE, CMX, and OTIO files. This dependency was added because OTIO provides robust EDL parsing with much better compatibility.

**cdl_convert is not associated with the American Society of Cinematographers**

## Quick Start

Install via pip:

```bash
pip install cdl_convert
```

Convert a file:

```bash
cdl_convert input.flex -o cc
```

Use the Python API:

```python
import cdl_convert as cdl

# Parse a CDL file
cc = cdl.parse_cc('path/to/file.cc')

# Access values
print(cc.slope, cc.offset, cc.power, cc.sat)

# Write to different format
cdl.write_ccc(cc)
```

See {doc}`usage` for command-line examples and {doc}`usage_cc` for Python API usage.

## Table of Contents

```{toctree}
:maxdepth: 2

usage
installation
usage_nuke
usage_otio
faq
support
changelog
license
contributing
usage_cc
usage_ccc
usage_cdl
usage_mediaref
api/index
```

## Indices and tables

- {ref}`genindex`
- {ref}`search`
