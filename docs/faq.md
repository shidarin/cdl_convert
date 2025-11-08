# Frequently Asked Questions

## Python Version Support

### What versions of Python does cdl_convert support?

`cdl_convert` requires **Python 3.11 or higher**. Specifically, it supports Python 3.11, 3.12, 3.13, and 3.14.

### What happened to Python 2 support?

Python 2.7 support was removed in version 1.0.0 as part of the modernization effort. Python 2 reached end-of-life on January 1, 2020.

If you need Python 2.7 support, use cdl_convert version 0.9.x or earlier.

### What happened to PyPy support?

PyPy support was also dropped in version 1.0.0. The focus is now on CPython 3.11-3.14 to ensure compatibility with modern Python features and dependencies like OpenTimelineIO.

## CDL Format Support

### What formats does cdl_convert support?

**Input formats:**
- Avid Log Exchange (ALE)
- Film Log EDL Exchange (FLEx)
- CMX EDL
- XML Color Correction (cc)
- XML Color Correction Collection (ccc)
- XML Color Decision List (cdl)
- OpenTimelineIO (OTIO) timeline files
- Space separated CDL (RCDL) - Rhythm & Hues format

**Output formats:**
- XML Color Correction (cc)
- XML Color Correction Collection (ccc)
- XML Color Decision List (cdl)
- Space separated CDL (RCDL)

See {doc}`usage` for examples of converting between formats.

### Why don't you support format X?

There are a few possible reasons:

1. **We haven't had time yet** - Building parsers takes time and testing
2. **We're unaware it exists** - The CDL ecosystem has many variants
3. **It's on the roadmap** - Check the [GitHub issues](https://github.com/shidarin/cdl_convert/issues)

If you need support for a specific format, please [create an issue](https://github.com/shidarin/cdl_convert/issues/new) on GitHub. It helps immensely to include:
- A sample file in that format
- Documentation or specification for the format
- Your use case for needing this format

### Does cdl_convert support OpenTimelineIO?

Yes, CDL Convert uses [OpenTimelineIO](https://github.com/PixarAnimationStudios/OpenTimelineIO) for EDL parsing and can also read OTIO timeline files with embedded CDL metadata. See {doc}`usage_otio` for details.

## Project Structure

### Why the underscore in the name?

`cdl_convert` started as a simple script to convert from one format to another. As such, it wasn't named with the standards typically used for Python modules (which usually use all lowercase without underscores).

By the time the project grew large enough and was published on PyPI, it was already established in too many places to make changing easy. The name has been kept for consistency and to avoid breaking existing installations and documentation.

### Is cdl_convert actively maintained?

For a long time, no. Let's see how things go now.

The project has recently undergone significant modernization:
- Updated to Python 3.11-3.14
- Migrated to modern build system (Hatch/pyproject.toml)
- Upgraded to latest OpenTimelineIO
- Updated documentation
- Migrated CI/CD to GitHub Actions

See {doc}`changelog` for recent updates.

### Why the ten year break between updates?

Work. When I started `cdl_convert`, I was a VFX artist who coded on the side. `cdl_convert` helped me make the transition to Pipeline programmer, where I started writing code daily and stopped having time to do it on the side. Since then, I've stopped coding daily and find more time in my off-hours to code again.

## What's new in version 1.0?

Version 1.0 is a major modernization release with:

- **OTIO backend for ALE and CMX** - More robust EDL parsing
- **OTIO file support** - Read .otio timeline files with CDL metadata
- **Type hints throughout** - Better IDE support and code clarity
- **Modern Python features** - pathlib, dataclasses, f-strings, match statements
- **Enhanced error handling** - Specific exception types for better debugging
- **Hatch build system** - Modern Python packaging

See {doc}`changelog` for the complete list of changes.

## Is version 1.0 compatible with my existing code?

The CLI and API should be compatible with tools written for version 0.9.2, however no warranties or guarantees are given. The public API remains the same, but with improvements like type hints and better error messages.

If you encounter compatibility issues, please [report them on GitHub](https://github.com/shidarin/cdl_convert/issues).

### What are the breaking changes in 1.0?

- **Python 3.11+ required** - Dropped Python 2.7-3.10 and PyPy
- **OpenTimelineIO required** - Now a core dependency for EDL parsing
- **Windows 3.13/3.14 not supported** - Due to OTIO build issues

## Technical Questions

### How does cdl_convert handle invalid CDL values?

By default, cdl_convert attempts to correct invalid values:
- Negative slope, power, or saturation values are clipped to 0.0
- Duplicate IDs are automatically renamed with a numeric suffix

You can enable strict mode with the `--halt` flag to fail on invalid values instead. See {doc}`usage` for details.

### Can I use cdl_convert as a Python library?

Absolutely! CDL Convert is designed to work both as a command-line tool and as a Python library. See {doc}`usage_cc` and {doc}`usage_ccc` for Python API examples.

### Does cdl_convert validate CDL values?

Yes! Use the `--check` flag to validate CDL values and get warnings about potentially incorrect values:
- Slope, Power, Saturation outside 0.1-3.0 range
- Offset outside -1.0 to 1.0 range

See {doc}`usage` for examples.

### What's the difference between ColorCorrection and ColorCollection?

- {class}`~cdl_convert.correction.ColorCorrection` represents a single CDL with slope, offset, power, and saturation values
- {class}`~cdl_convert.collection.ColorCollection` is a container that holds multiple ColorCorrections or ColorDecisions

See {doc}`api/classes` for detailed API documentation.
