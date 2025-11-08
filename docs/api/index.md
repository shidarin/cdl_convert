# API Reference

The class structure of `cdl_convert` mirrors the element structure of the XML schema for `ccc`, `cdl` and `cc` files as defined by the ASC. The XML schemas represent the most complicated and structured variant of the format, and therefore it behooves the project to mimic their structure.

However, where similar elements exist as entirely separate entities in the XML schema, they might have been combined here.

## Core Classes

```{toctree}
:maxdepth: 2

classes
parse
write
utils
```

## Quick Reference

### Main Classes

- {class}`~cdl_convert.correction.ColorCorrection` - The backbone class representing a single CDL
- {class}`~cdl_convert.collection.ColorCollection` - Container for multiple CDLs
- {class}`~cdl_convert.decision.ColorDecision` - Decision with correction and media reference
- {class}`~cdl_convert.correction.SopNode` - Slope, Offset, Power values
- {class}`~cdl_convert.correction.SatNode` - Saturation value

### Parse Functions

- {func}`~cdl_convert.parse.parse_file` - Auto-detect and parse any supported format
- {func}`~cdl_convert.parse.parse_cc` - Parse XML Color Correction
- {func}`~cdl_convert.parse.parse_ccc` - Parse Color Correction Collection
- {func}`~cdl_convert.parse.parse_cdl` - Parse Color Decision List
- {func}`~cdl_convert.parse.parse_ale` - Parse Avid Log Exchange
- {func}`~cdl_convert.parse.parse_cmx` - Parse CMX EDL

### Write Functions

- {func}`~cdl_convert.write.write_cc` - Write XML Color Correction
- {func}`~cdl_convert.write.write_ccc` - Write Color Correction Collection
- {func}`~cdl_convert.write.write_cdl` - Write Color Decision List
- {func}`~cdl_convert.write.write_rnh_cdl` - Write Rhythm & Hues CDL
