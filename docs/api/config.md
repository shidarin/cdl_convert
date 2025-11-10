# Configuration

The {mod}`~cdl_convert.config` module provides centralized configuration management for cdl_convert through a type-safe dataclass-based system.

## Overview

The configuration system consists of three main components:

1. {class}`~cdl_convert.config.CDLFormat` - An enum defining all supported CDL format types
2. {class}`~cdl_convert.config.Config` - A dataclass containing all global settings with validation
3. {data}`~cdl_convert.config.config` - A global configuration instance for centralized access

## Global Configuration Instance

The module exports a global {data}`~cdl_convert.config.config` instance that provides centralized access to all settings:

```python
from cdl_convert.config import config

# Check error handling mode
if config.halt_on_error:
    # Strict validation mode
    pass

# Check if a format is a collection format
if config.is_collection_format('ccc'):
    # Handle collection format
    pass
```

## CDLFormat Enum

The {class}`~cdl_convert.config.CDLFormat` enum provides type-safe format identifiers for all supported CDL formats:

```python
from cdl_convert.config import CDLFormat

# Access format types
format_type = CDLFormat.CCC
print(format_type.value)  # 'ccc'

# Use in comparisons
if my_format == CDLFormat.CC:
    # Handle CC format
    pass
```

Supported formats:

- `CDLFormat.ALE` - Avid Log Exchange
- `CDLFormat.CC` - XML Color Correction (single)
- `CDLFormat.CCC` - XML Color Correction Collection
- `CDLFormat.CDL` - XML Color Decision List
- `CDLFormat.EDL` - CMX EDL
- `CDLFormat.FLEX` - Film Log EDL Exchange
- `CDLFormat.FLEX` - ASWF's OpenTimeineIO EDL Exchange
- `CDLFormat.RCDL` - Space-separated CDL (Rhythm & Hues)

```{eval-rst}
.. autoclass:: cdl_convert.config.CDLFormat
```

## Config Class

The {class}`~cdl_convert.config.Config` class is a dataclass that contains all global configuration settings with proper type hints and validation.

### Attributes

**halt_on_error** : `bool`
: If `True`, exceptions are raised instead of being handled with default behavior. Used for strict validation mode. Default is `False`.

**collection_formats** : `FrozenSet[CDLFormat]`
: Immutable set of formats that represent {class}`~cdl_convert.collection.ColorCollection` objects. Includes: ALE, CCC, CDL, EDL, and FLEx.

**single_formats** : `FrozenSet[CDLFormat]`
: Immutable set of formats that represent single {class}`~cdl_convert.correction.ColorCorrection` objects. Includes: CC and RCDL.

**sop_tag_name** : `str`
: XML element tag name for SOP (Slope/Offset/Power) nodes. Valid values: `'SOPNode'` (default), `'ASC_SOP'`. Controls the XML tag used when generating SOP elements in output files.

**sat_tag_name** : `str`
: XML element tag name for Saturation nodes. Valid values: `'SatNode'` (default), `'SATNode'` (legacy), `'ASC_SAT'`. Controls the XML tag used when generating Saturation elements in output files. Default changed from `'SATNode'` to `'SatNode'` in v1.0 to finally adhere correctly to specification.

### Methods

The {class}`~cdl_convert.config.Config` class provides helper methods for format type checking and tag name configuration:

```python
from cdl_convert.config import config

# Check if a format string is a collection format
if config.is_collection_format('ccc'):
    print("CCC is a collection format")

# Check if a format string is a single correction format
if config.is_single_format('cc'):
    print("CC is a single correction format")

# Configure XML tag names
config.set_sop_tag_name('ASC_SOP')
config.set_sat_tag_name('ASC_SAT')
```

```{eval-rst}
.. autoclass:: cdl_convert.config.Config
```

## Usage Examples

### Strict Validation Mode

Enable strict validation to raise exceptions instead of using default behavior:

```python
from cdl_convert.config import config

# Enable strict mode
config.halt_on_error = True

# Now parsing errors will raise exceptions
try:
    cc = parse_cc('invalid.cc')
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Format Type Checking

Use the configuration to determine how to handle different format types:

```python
from cdl_convert.config import config

def process_file(filepath, format_type):
    if config.is_collection_format(format_type):
        # Parse as collection
        collection = parse_collection(filepath)
        return collection
    elif config.is_single_format(format_type):
        # Parse as single correction
        correction = parse_correction(filepath)
        return correction
    else:
        raise ValueError(f"Unknown format: {format_type}")
```

### Working with Format Enums

Use the {class}`~cdl_convert.config.CDLFormat` enum for type-safe format handling:

```python
from cdl_convert.config import CDLFormat, config

def get_parser(format_type: CDLFormat):
    """Get the appropriate parser for a format type."""
    if format_type in config.collection_formats:
        return parse_collection
    elif format_type in config.single_formats:
        return parse_correction
    else:
        raise ValueError(f"Unsupported format: {format_type}")

# Use with enum
parser = get_parser(CDLFormat.CCC)
```

### Configurable XML Tag Names

Configure the XML element tag names used for SOP and Saturation nodes to improve compatibility with different color correction systems:

```python
from cdl_convert.config import config
from cdl_convert import write_cc, ColorCorrection

# Use ASC CDL specification-compliant tag names
config.set_sop_tag_name('ASC_SOP')
config.set_sat_tag_name('ASC_SAT')

# Create and write a color correction
cc = ColorCorrection('shot_001')
cc.slope = [1.2, 1.1, 1.0]
cc.sat = 0.9
write_cc(cc)  # Will use ASC_SOP and ASC_SAT tags

# Use legacy SATNode tag for backward compatibility
config.set_sat_tag_name('SATNode')
write_cc(cc)  # Will use SOPNode and SATNode tags
```

**Available SOP Tag Names:**
- `'SOPNode'` (default) - Standard format
- `'ASC_SOP'` - ASC CDL specification format

**Available Saturation Tag Names:**
- `'SatNode'` (default) - Standard format (new in v1.0)
- `'SATNode'` - Legacy format (pre-v1.0)
- `'ASC_SAT'` - ASC CDL specification format

:::{note}
The default Saturation tag changed from `'SATNode'` to `'SatNode'` in v1.0 to adhere to the CDL specification. Use `config.set_sat_tag_name('SATNode')` to maintain legacy behavior.
:::

## Migration from Legacy Configuration

Prior to version 1.0, cdl_convert used a simple module-level `HALT_ON_ERROR` boolean. The new configuration system provides:

- **Type safety** through dataclasses and enums
- **Validation** of configuration values
- **Extensibility** for future configuration options
- **Better IDE support** with type hints

Legacy code:

```python
# Old way (pre-1.0)
from cdl_convert import config
config.HALT_ON_ERROR = True
```

Modern code:

```python
# New way (1.0+)
from cdl_convert.config import config
config.halt_on_error = True
```

:::{note}
The global {data}`~cdl_convert.config.config` instance is mutable, allowing you to change settings at runtime. However, be aware that changes affect all subsequent operations in your application.
:::

:::{warning}
The `collection_formats` and `single_formats` attributes are frozen sets and cannot be modified. This ensures consistency in format type classification throughout the library.
:::
