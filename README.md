# CDL Convert

[![PyPI Version](https://badge.fury.io/py/cdl_convert.png)](http://badge.fury.io/py/cdl_convert)
[![Build Status](https://github.com/shidarin/cdl_convert/workflows/CI/badge.svg)](https://github.com/shidarin/cdl_convert/actions)
[![Coverage](https://codecov.io/gh/shidarin/cdl_convert/graph/badge.svg?token=TIFtNj7SmO)](https://codecov.io/gh/shidarin/cdl_convert)

- **Author/Maintainer:** Sean Wallitsch
- **Email:** shidarin@alphamatte.com
- **License:** MIT
- **Status:** Development
- **Docs:** <http://cdl-convert.readthedocs.org/>
- **GitHub:** <https://github.com/shidarin/cdl_convert>
- **PyPI:** <https://pypi.org/project/cdl_convert/>
- **Python Versions:** 3.11, 3.12, 3.13, 3.14

## Introduction

`cdl_convert` converts between common [ASC CDL](http://en.wikipedia.org/wiki/ASC_CDL) formats. The [American Society of Cinematographers](http://www.theasc.com/) Color Decision List (CDL) is a schema to simplify the process of interchanging color data between various programs and facilities.

The ASC has defined schemas for including the 10 basic numbers in 6 different formats:

- Avid Log Exchange (ALE)
- Film Log EDL Exchange (FLEx)
- CMX EDL
- XML Color Correction (cc)
- XML Color Correction Collection (ccc)
- XML Color Decision List (cdl)

Unofficial Formats:

- OpenTimelineIO (OTIO) timeline files with embedded CDL metadata
- OCIOCDLTransform, a [Foundry Nuke](http://www.thefoundry.co.uk/nuke/) node
- Space separated CDL, a Rhythm & Hues internal cdl format

`cdl_convert` converts ASC CDL information between these basic formats to 
further facilitate the ease of exchange of color data within the Film and TV industries.

`cdl_convert` supports parsing ALE, FLEx, CC, CCC, CDL, CMX EDL, OTIO, and RCDL.
`cdl_convert` can write out CC, CCC, CDL and RCDL.

### New in 1.0

- **OTIO backend for ALE and CMX** allows for more robust EDL parsing
- **OTIO EDL support** for OpenTimelineIO files with CDL metadata
- **Python 3.11-3.14 support**

This version of `cdl_convert` has been modernized with:

- **Type hints** throughout the codebase for better IDE support and code clarity
- **pathlib.Path** for robust cross-platform file operations
- **Dataclasses** for structured color correction data (`ColorValues`)
- **Enhanced error handling** with specific exception types (`ValidationError`, `ParseError`, `FormatError`)
- **f-string formatting** for improved string operations
- **Context managers** for safe resource management
- **Match statements** for cleaner control flow

`cdl_convert` uses the Academy Software Foundation's [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) project for reading ALE, CMX, and OTIO files.

**cdl_convert is not associated with the American Society of Cinematographers**

## Usage

`cdl_convert` can be used both as a command-line script and as a Python library.

### Script Usage

Convert to a `.cc` XML file with defaults:

```bash
$ cdl_convert ./di_v001.flex
```

Override the default output format or provide multiple outputs:

```bash
$ cdl_convert ./di_v001.flex -o cc,cdl
```

Use enhanced error checking and validation:

```bash
$ cdl_convert --check --halt-on-error ./input.ale -o ccc
```

Specify output directory:

```bash
$ cdl_convert ./input.flex -d ./output_directory/ -o cc,ccc,cdl
```

## Installation

### Installing from PyPI

The recommended installation method using pip:

```bash
pip install cdl_convert
```

### Installing from Source

For the latest development version:

```bash
git clone https://github.com/shidarin/cdl_convert.git
cd cdl_convert
pip install -e .
```

### Development Installation

For development work:

```bash
git clone https://github.com/shidarin/cdl_convert.git
cd cdl_convert
pip install -e .[dev]
```

This installs the package in editable mode with all development dependencies
including pytest, mypy, and ruff.

### Building from Source

`cdl_convert` uses current standard Python packaging with `pyproject.toml` and Hatch:

```bash
# Install build dependencies
pip install hatch

# Build wheel and source distributions
hatch build

# Install from built wheel
pip install dist/cdl_convert-*.whl
```

### Development Workflow

The project uses Hatch for development workflow management:

```bash
# Run tests across all python versions
hatch run test:all

# Run tests with coverage
hatch run test:cov

# Run tests in just 3.14
hatch run test

# Run linting
hatch run lint

# Run type checking
hatch run type-check

# Format code
hatch run format
```

### Dependencies

`cdl_convert` automatically installs its dependencies:

- **OpenTimelineIO** - For robust EDL parsing
- **otio-cmx3600-adapter** - CMX EDL format support
- **otio-ale-adapter** - ALE format support
- **defusedxml** - Secure XML parsing to prevent XML attacks

## Changelog

### New in version 1.0.0

**Breaking Changes:**

- **Python 3.11+ Required** - Dropped support for Python 2.7-3.10 and PyPy
- **OpenTimelineIO Required** - We've moved to using OpenTimelineIO's robust EDL adaptor system to parse ALE, CMX, and OTIO EDL files
- **Windows w/ Python 3.14 is not supported** - Due to an OTIO build issue, running on Windows with Python 3.14 is at your own risk
- **MediaRef URI behavior has changed** - Previously, MediaRef URIs could be
impacted based on the OS you were running cdl_convert on. cdl_convert now attempts
to maintain the original os behavior which wrote the URI to start with.
- **SatNode XML tag default changed** - The default XML element tag for Saturation nodes has changed from `SATNode` to `SatNode` for consistency with `SOPNode` naming. Use `--sat-tag SATNode` to maintain legacy behavior.

**New Features:**

- **OTIO support** - Now ingests .otio files with CDL metadata
- **Hatch & pyproject.toml** - Modern python packaging and building
- **Type hints throughout** - Full type annotation for better IDE support
- **pathlib integration** - Modern file path handling with `pathlib.Path`
- **ColorValues dataclass** - Structured color correction data with validation
- **Enhanced error handling** - Specific exception types (`ValidationError`, `ParseError`, `FormatError`)
- **Colored CLI output** - Enhanced command-line experience with colored error messages
- **Configurable XML tag names** - Choose between different XML element tag conventions for SOP and Saturation nodes to improve compatibility with various color correction systems

**CLI and API should be compatible with with tools written for 0.9.2, however
no warranties or gaurantees are given.**

### New in version 0.9.2

- Fixed a bug where ALE's with blank lines would not convert correctly.
- Fixed a bug that was preventing `cdl_convert` from being correctly installed in Python 2.6
- Fixed continuous integration testing.
- No longer officially supporting Python 3.2, as I've had to remove it from our CI builds. It should still work just fine though, but we won't be running CI against it.

### New in version 0.9

- Added ability to parse CMX EDLs
- Fixed a script bug where a collection format containing color decisions will not have those color decisions exported as individual color corrections.
- Fixed a bug where we weren't reading line endings correctly in certain situations.
- Added a cdl_convert.py stub file to the package root level, which will allow running of the cdl_convert script without installation. Due to relative imports in the python code, it was no longer possible to call cdl_convert/cdl_convert.py directly.
- The script, when run directly from cdl_convert.py, will now write errors to stderror correctly, and exit with a status of 1.

See full changelog in the [documentation](http://cdl-convert.readthedocs.org/).

## Frequently Asked Questions

### What versions of Python does cdl_convert support?

`cdl_convert` requires **Python 3.11 or higher**.

### Why the underscore?

`cdl_convert` started as a simple script to convert from one format to another. As such, it wasn't named with the standards that one would usually use for a python module. By the time the project became big enough, was on PyPI, etc, it was too spread out on the web, in too many places to make changing easy. In the end, I opted to keep it.

### Why the ten year break between updates?

Work. When I started `cdl_convert`, I was a VFX artist who coded on the side. `cdl_convert` helped me make the transition to Pipeline programmer, where I started writing code daily and stopped having time to do it on the side. Since then, I've stopped coding daily and find more time in my off-hours to code again.

## GitHub, Bug Reporting and Support

At `cdl_convert`'s [GitHub page](https://github.com/shidarin/cdl_convert) you can browse the code and the history of the project.

Builds can be downloaded from the GitHub page or the [PyPI repository](https://pypi.org/project/cdl_convert/).

The [issues page](https://github.com/shidarin/cdl_convert/issues) on GitHub is the best place to report bugs or request support, and while `cdl_convert` is distributed with no warranty of any kind, issues will be read and helped if able.

## Contributing

### Samples

Please, *please*, **please** submit samples of the following formats:

- FLEx
- ALE
- CMX
- CCC

These are complex formats, and seeing real world samples helps write tests that ensure correct parsing of real world EDLs and CDLs. If you don't even see a format of CDL listed that you know exists, open an issue at the github [issues page](https://github.com/shidarin/cdl_convert/issues) asking for parse/write support for the format, and include a sample.

### Squashing Bugs

Take a look at the [issues page](https://github.com/shidarin/cdl_convert/issues) and if you see something that you think you can bang out, leave a comment saying you're going to take it on. While many issues are already assigned to the principal authors, just because it's assigned doesn't mean any work has begun.

### Submitting Code

Before generating a pull request, make sure to run the full development workflow:

```bash
# Run all checks
hatch run test:cov
hatch run lint
hatch run type-check
```

If the tests fail, note which tests are failing and how they would have been affected by your code. The tests are run every push with GitHub Actions, so they should have been passing before your changes. If you know you didn't break something, and the tests are simply reporting out of date results based on your changes, so *change the tests.*

If your code fails the tests (GitHub Actions checks all pull requests when you create them) it will be **rejected**. If the code style doesn't follow PEP-8, type hints are missing, or linting fails, please correct these issues.

**Code Quality Standards:**

- **Type hints** are required for all new code
- **PEP-8 compliance** enforced by ruff
- **Test coverage** should be maintained or improved
- **Documentation** should be updated for API changes

When submitting, you'll be asked to waive copyright to your submitted code to the listed authors. This is so we can keep a tight handle on the code and change the license for future releases if needed.

## License

The MIT License (MIT)

**cdl_convert**  
Copyright (c) 2015-2025 Sean Wallitsch  
<http://github.com/shidarin/cdl_convert/>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
