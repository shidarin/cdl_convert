# Installation

## Installing from PyPI (Recommended)

The recommended installation method using pip:

```bash
pip install cdl_convert
```

This installs cdl_convert both as a Python module and a command-line script.

### Install from Source

To install the latest development version from GitHub:

```bash
pip install git+https://github.com/shidarin/cdl_convert.git
```

## Requirements

CDL Convert requires:
- **Python 3.11 or higher** (supports 3.11, 3.12, 3.13, 3.14)
- [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO)
- **otio-cmx3600-adapter** - CMX EDL format support
- **otio-ale-adapter** - ALE format support
- **defusedxml** - Secure XML parsing

All dependencies are installed automatically via pip.

## Verifying Installation

After installation, verify that cdl_convert is available:

```bash
cdl_convert --help
```

You should see the command-line help output.

## Python Module Usage

Once installed, you can import cdl_convert in your Python code:

```python
import cdl_convert as cdl

# Parse a CDL file
cc = cdl.parse_cc('path/to/file.cc')

# Access CDL values
print(cc.slope)
print(cc.offset)
print(cc.power)
print(cc.sat)
```

See {doc}`usage` for command-line usage and {doc}`usage_cc` for Python API examples.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure all dependencies are installed:

```bash
pip install --upgrade cdl_convert
```

### Command Not Found

If the `cdl_convert` command is not found after installation, ensure your Python scripts directory is in your PATH:

```bash
# On macOS/Linux
export PATH="$HOME/.local/bin:$PATH"

# On Windows
# Add %APPDATA%\Python\Scripts to your PATH environment variable
```

### OpenTimelineIO Issues

If you have issues with EDL parsing, verify OpenTimelineIO is installed:

```bash
python -c "import opentimelineio; print(opentimelineio.__version__)"
```

If not installed, install it manually:

```bash
pip install opentimelineio
```

## Uninstalling

To uninstall cdl_convert:

```bash
pip uninstall cdl_convert
```
