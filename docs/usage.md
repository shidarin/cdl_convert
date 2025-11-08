# Script Usage

`cdl_convert` can be used both as a command-line script and as a Python library. The command-line interface provides a simple way to convert between CDL formats.

## Basic Conversion

Convert to a `.cc` XML file (default output):

```bash
$ cdl_convert ./di_v001.flex
```

Override the default output format or provide multiple outputs:

```bash
$ cdl_convert ./di_v001.flex -o cc,cdl
```

Specify output directory:

```bash
$ cdl_convert ./input.flex -d ./output_directory/ -o cc,ccc,cdl
```

## Specifying Input Format

Sometimes it might be necessary to disable cdl_convert's auto-detection of the input file format. This can be done with the `-i` flag:

```bash
$ cdl_convert ./ca102_x34.cdl -i rcdl
```

:::{note}
You should not normally need to do this, but it is possible especially since there are multiple formats sharing the same file extension. In this case, `.cdl` could have indicated either a space separated cdl (an `rcdl`), or an XML cdl. `cdl_convert` does its best to try and guess which one the file is, but if you're running into trouble, it might help to indicate to `cdl_convert` what the input file type is.
:::

## Output Directory

By default, converted files will be written to the `./converted` directory, but a custom destination directory can easily be specified with the `-d` flag:

```bash
$ cdl_convert ./hk416_210.ccc -d /hello_kitty/luts/cdls/
```

:::{warning}
It's possible to pass a `.` to the `-d` flag, causing converted files to be written to the same directory as the directory you're calling cdl_convert from, and often that ends up being the same directory as the file you're converting from. If one isn't careful, there's a possibility you could overwrite the original files.
:::

## Enhanced Error Checking and Validation

`cdl_convert` includes enhanced error checking and validation. Use the `--check` flag to validate CDL values and get warnings about potentially incorrect values.

For Slope, Power and Saturation, any values below `0.1` or above `3.0` will flag. For Offset, any values below `-1.0` or above `1.0` will flag:

```bash
$ cdl_convert ./di_v001.flex --check
The ColorCorrection "a347.x700" was given a Slope value of "0.978", which
might be incorrect.
The ColorCorrection "a400.x050" was given a Saturation value of "3.1",
which might be incorrect.
```

Use enhanced error handling with the `--halt` flag to stop processing on the first error:

```bash
$ cdl_convert --check --halt ./input.ale -o ccc
```

This is especially useful when combined with the `--no-output` flag for dry run mode:

```bash
$ cdl_convert ./timeline.otio --check --no-output
```

## Python API Usage

`cdl_convert` can also be used as a Python library:

```python
import cdl_convert as cdl

# Parse a CDL file
cc = cdl.parse_cc('path/to/file.cc')

# Access CDL values
print(cc.slope)    # (Decimal('1.2'), Decimal('1.0'), Decimal('0.8'))
print(cc.offset)   # (Decimal('0.1'), Decimal('0.0'), Decimal('-0.1'))
print(cc.power)    # (Decimal('1.0'), Decimal('1.1'), Decimal('0.9'))
print(cc.sat)      # Decimal('1.2')

# Write to different format
cdl.write_ccc(cc)
```

See {doc}`usage_cc` for detailed Python API examples and {doc}`usage_ccc` for working with collections.

## Command Line Reference

Full help is available using the standard `--help` command:

```bash
$ cdl_convert --help
usage: cdl_convert [-h] [-i INPUT] [-o OUTPUT] [-d DESTINATION] [--halt]
                   [--no-output] [--check] [--single] [-v] [--debug]
                   input_file

Convert between ASC Color Decision List (CDL) formats

positional arguments:
  input_file            Path to the CDL file to be converted

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Specify input format when auto-detection fails.
                        Choices: ale, cc, ccc, cdl, edl, flex, otio, rcdl
  -o OUTPUT, --output OUTPUT
                        Output format(s), comma-separated for multiple outputs.
                        Choices: cc, ccc, cdl, rcdl. Default: cc
  -d DESTINATION, --destination DESTINATION
                        Output directory for converted files. Default: ./converted/
  --halt                Stop processing on first error instead of using default
                        values. Useful for strict validation of CDL files.
  --no-output           Parse files without writing output. Useful with --halt
                        and --check for validation-only runs.
  --check               Check for unusual color correction values. Flags
                        slope/power/saturation outside 0.1-3.0 range and offset
                        outside -1.0 to 1.0 range.
  --single              Write each color decision to a separate file instead of
                        collections. Converts one input file to multiple output
                        files.
  -v, --verbose         Enable verbose output with detailed processing information
  --debug               Enable debug output with extensive diagnostic information

Supported input formats: ale, cc, ccc, cdl, edl, flex, otio, rcdl
Supported output formats: cc, ccc, cdl, rcdl
```
