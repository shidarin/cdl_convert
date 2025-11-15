# Color Decisions

Color Decisions are the mechanism for linking color corrections with media references in ASC CDL workflows. They provide the bridge between the color correction data and the actual media files being graded.

## Overview

A {class}`~cdl_convert.decision.ColorDecision` is a container that associates:
- A {class}`~cdl_convert.correction.ColorCorrection` (or reference to one)
- An optional {class}`~cdl_convert.decision.MediaRef` pointing to media files

ColorDecisions are typically found within {class}`~cdl_convert.collection.ColorCollection` objects when working with CDL (ColorDecisionList) format files, but can be created and used independently.

## When to Use ColorDecision

Use ColorDecision when you need to:
- Link color corrections to specific media files or sequences
- Work with CDL (ColorDecisionList) format files
- Reference the same ColorCorrection from multiple locations
- Maintain media file paths alongside color correction data

Use plain {class}`~cdl_convert.correction.ColorCorrection` when:
- Working with simple color correction data without media references
- Exporting to CCC (ColorCorrectionCollection) format
- You don't need to track which media files the corrections apply to

## Creating ColorDecision

### Basic Creation

Create a ColorDecision by providing a ColorCorrection and optional MediaRef:

```python
import cdl_convert as cdl

# Create a color correction
cc = cdl.ColorCorrection(id='shot_001')
cc.slope = (1.2, 1.1, 1.0)
cc.offset = (0.01, -0.02, 0.0)
cc.power = (1.0, 1.0, 0.95)
cc.sat = 1.1

# Create a media reference
media = cdl.MediaRef('footage/shot_001.0001.exr')

# Create the color decision linking them together
decision = cdl.ColorDecision(cc, media_ref=media)
```

### Creating Without Media Reference

ColorDecisions can exist without media references:

```python
cc = cdl.ColorCorrection(id='master_grade')
cc.slope = (1.1, 1.0, 0.9)

# Create decision without media reference
decision = cdl.ColorDecision(cc)
```

### Adding Media Reference Later

You can add or change the media reference after creation:

```python
decision = cdl.ColorDecision(cc)

# Add media reference later
media = cdl.MediaRef('renders/final_v01.mov')
decision.media_ref = media
```

## Working with ColorDecision

### Accessing the ColorCorrection

Access the contained ColorCorrection through the `cc` property:

```python
>>> decision.cc.id
'shot_001'
>>> decision.cc.slope
(Decimal('1.2'), Decimal('1.1'), Decimal('1.0'))
>>> decision.cc.sat
Decimal('1.1')
```

### Accessing the MediaRef

Access the media reference through the `media_ref` property:

```python
>>> decision.media_ref.ref
'footage/shot_001.0001.exr'
>>> decision.media_ref.is_seq
True
>>> decision.media_ref.seq
'shot_001.####.exr'
```

### Descriptions and Metadata

ColorDecision inherits description capabilities from base classes:

```python
# Add descriptions
decision.desc = 'Hero shot with practical lighting'
decision.desc = 'Increased warmth in highlights'

# Set input and viewing descriptions
decision.input_desc = 'LogC from Alexa'
decision.viewing_desc = 'Rec709 on Eizo CG319X'

# Access descriptions
>>> decision.desc
['Hero shot with practical lighting', 'Increased warmth in highlights']
```

## ColorCorrectionRef - Referencing Existing Corrections

{class}`~cdl_convert.decision.ColorCorrectionRef` allows you to reference an existing ColorCorrection by ID rather than duplicating it. This is useful when the same color correction applies to multiple media files.

### Creating References

```python
# Create the original color correction
cc = cdl.ColorCorrection(id='day_exterior_grade')
cc.slope = (1.15, 1.05, 0.95)
cc.sat = 1.2

# Create multiple decisions referencing the same correction
ref1 = cdl.ColorCorrectionRef('day_exterior_grade')
decision1 = cdl.ColorDecision(ref1, media_ref=cdl.MediaRef('shot_010.mov'))

ref2 = cdl.ColorCorrectionRef('day_exterior_grade')
decision2 = cdl.ColorDecision(ref2, media_ref=cdl.MediaRef('shot_011.mov'))

ref3 = cdl.ColorCorrectionRef('day_exterior_grade')
decision3 = cdl.ColorDecision(ref3, media_ref=cdl.MediaRef('shot_012.mov'))
```

### Resolving References

Access the actual ColorCorrection through the reference:

```python
>>> ref = cdl.ColorCorrectionRef('day_exterior_grade')
>>> ref.id
'day_exterior_grade'
>>> ref.cc.slope
(Decimal('1.15'), Decimal('1.05'), Decimal('0.95'))
```

### Checking if ColorDecision Contains a Reference

```python
>>> decision1.is_ref
True
>>> decision_with_direct_cc.is_ref
False
```

### Reference Validation

By default, references don't need to point to existing ColorCorrections when created. Enable strict validation:

```python
import cdl_convert as cdl

# Enable strict error checking
cdl.config.HALT_ON_ERROR = True

# This will raise ValidationError if 'nonexistent_id' doesn't exist
try:
    ref = cdl.ColorCorrectionRef('nonexistent_id')
except cdl.ValidationError as e:
    print(f"Reference validation failed: {e}")
```

## Using ColorDecisions in Collections

ColorDecisions are typically used within ColorCollections:

```python
# Create a collection
collection = cdl.ColorCollection()
collection.type = 'cdl'  # ColorDecisionList format

# Create multiple decisions
cc1 = cdl.ColorCorrection(id='shot_100')
cc1.slope = (1.1, 1.0, 0.9)
decision1 = cdl.ColorDecision(cc1, media_ref=cdl.MediaRef('shot_100.mov'))

cc2 = cdl.ColorCorrection(id='shot_101')
cc2.slope = (1.2, 1.1, 1.0)
decision2 = cdl.ColorDecision(cc2, media_ref=cdl.MediaRef('shot_101.mov'))

# Add decisions to collection
collection.append_child(decision1)
collection.append_child(decision2)

# Access decisions
>>> collection.color_decisions
[
    <cdl_convert.decision.ColorDecision object at 0x...>,
    <cdl_convert.decision.ColorDecision object at 0x...>
]
```

## Parsing ColorDecisions from Files

When parsing CDL files, ColorDecisions are automatically created:

```python
# Parse a CDL file
collection = cdl.parse_cdl('timeline.cdl')

# Access the color decisions
for decision in collection.color_decisions:
    print(f"ID: {decision.cc.id}")
    if decision.media_ref:
        print(f"Media: {decision.media_ref.ref}")
    print(f"Slope: {decision.cc.slope}")
    print()
```

## Writing ColorDecisions

### Writing to CDL Format

ColorDecisions with media references are preserved when writing to CDL format:

```python
collection = cdl.ColorCollection()
collection.type = 'cdl'

# Add decisions with media references
decision = cdl.ColorDecision(
    cdl.ColorCorrection(id='shot_001'),
    media_ref=cdl.MediaRef('footage/shot_001.mov')
)
collection.append_child(decision)

# Write to CDL format (preserves media references)
collection.determine_dest('cdl', './output/')
cdl.write_cdl(collection)
```

## See Also

- {doc}`usage_mediaref` - Detailed MediaRef usage and path manipulation
- {doc}`usage_ccc` - Working with ColorCollection
- {doc}`usage_cc` - Working with ColorCorrection
- {class}`~cdl_convert.decision.ColorDecision` - API reference
- {class}`~cdl_convert.decision.ColorCorrectionRef` - API reference
