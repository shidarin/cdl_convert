# Nuke OCIOCDLTransform Format Support

`cdl_convert` supports full bidirectional conversion with OCIOCDLTransform nodes saved
in The Foundry Nuke's nuke scripts (.nk files). This allows for seamless integration with Nuke-based VFX and compositing workflows. Only tested with a single OCIOCDLTransform
node per script.

## OCIOCDLTransform Node Format

Nuke's OCIOCDLTransform node format is a simple text-based format that stores ASC CDL color correction values:

```
OCIOCDLTransform {
  slope {1.2 1.0 0.8}
  offset {0.1 0.0 -0.1}
  power {1.0 1.1 0.9}
  saturation 1.2
  name shot_001_grade
}
```

### Format Structure

- **slope**: Three space-separated float values for RGB slope
- **offset**: Three space-separated float values for RGB offset
- **power**: Three space-separated float values for RGB power
- **saturation**: Single float value for saturation
- **name**: Node name (used as ColorCorrection ID)

## Command-Line Usage

### Converting from Nuke Format

Convert a Nuke OCIOCDLTransform node to other CDL formats:

```bash
# Convert to Color Correction Collection
$ cdl_convert shot_001.nk -o ccc

# Convert to multiple formats
$ cdl_convert shot_001.nk -o cc,ccc,cdl

# Specify output directory
$ cdl_convert shot_001.nk -d ./output/ -o ccc
```

### Converting to Nuke Format

Convert other CDL formats to Nuke OCIOCDLTransform nodes:

```bash
# Convert from CCC to Nuke
$ cdl_convert input.ccc -o nk

# Convert from ALE to Nuke
$ cdl_convert input.ale -o nk

# Convert with validation
$ cdl_convert input.cc --check -o nk
```

## Python API Usage

### Parsing Nuke Files

```python
import cdl_convert as cdl

# Parse a Nuke OCIOCDLTransform file
cc = cdl.parse_nk('shot_001.nk')

# Access CDL values
print(f"Slope: {cc.slope}")
print(f"Offset: {cc.offset}")
print(f"Power: {cc.power}")
print(f"Saturation: {cc.sat}")
print(f"Node name: {cc.id}")
```

### Writing Nuke Files

```python
import cdl_convert as cdl
from pathlib import Path

# Create or load a ColorCorrection
cc = cdl.ColorCorrection('shot_001_grade')
cc.slope = [1.2, 1.0, 0.8]
cc.offset = [0.1, 0.0, -0.1]
cc.power = [1.0, 1.1, 0.9]
cc.sat = 1.2

# Set output path and write
cc.file_out = Path('output.nk')
cdl.write_nk(cc)
```

### Converting Between Formats

```python
import cdl_convert as cdl
from pathlib import Path

# Parse from one format
cc = cdl.parse_cc('input.cc')

# Write to Nuke format
cc.file_out = Path('output.nk')
cdl.write_nk(cc)

# Or use parse_file for automatic format detection
cc = cdl.parse_file('input.ccc')
cc.file_out = Path('output.nk')
cdl.write_nk(cc)
```

## Format Characteristics

### Single Node Per File

The current implementation supports one OCIOCDLTransform node per .nk file:

- When parsing, only the first OCIOCDLTransform node is extracted
- When writing, a single node is generated
- For multiple corrections, write separate .nk files

## Workflow Examples

### VFX Pipeline Integration

```python
import cdl_convert as cdl
from pathlib import Path

# Parse CDLs from DI department (CCC format)
collection = cdl.parse_ccc('di_grades.ccc')

# Export each correction as a Nuke node for compositors
output_dir = Path('./nuke_grades/')
output_dir.mkdir(exist_ok=True)

for correction in collection.color_corrections:
    correction.file_out = output_dir / f"{correction.id}.nk"
    cdl.write_nk(correction)
    print(f"Exported {correction.id}.nk")
```

### Batch Conversion

```bash
# Convert all Nuke CDL files in a directory to CCC
for file in *.nk; do
    cdl_convert "$file" -o ccc -d ./converted/
done
```

## Error Handling

### Missing Required Fields

When parsing Nuke files, if required fields are missing and `halt_on_error` is False (default), the parser will:

- Return None for missing fields
- Use unity defaults where appropriate
- Continue parsing without raising exceptions

With strict validation:

```bash
$ cdl_convert --halt input.nk -o ccc
```

## See Also

- {func}`~cdl_convert.parse.parse_nk` - parse_nk function API reference
- {func}`~cdl_convert.write.write_nk` - write_nk function API reference
- {func}`~cdl_convert.parse.parse_file` - Generic file parser (auto-detects format)
- {class}`~cdl_convert.correction.ColorCorrection` - ColorCorrection class API reference
- {doc}`usage_cc` - Working with individual ColorCorrection objects
- {doc}`usage` - Command-line usage
- {doc}`api/parse` - All parsing functions
- {doc}`api/write` - All writing functions
