# Media References

Media references provide a powerful interface for managing and manipulating file paths associated with color corrections. The {class}`~cdl_convert.decision.MediaRef` class handles URIs, local paths, image sequences, and provides path manipulation capabilities.

## Overview

{class}`~cdl_convert.decision.MediaRef` is designed to:
- Store references to media files or directories
- Parse and manipulate URI components (protocol, directory, filename)
- Detect image sequences
- Provide cross-platform path handling
- Validate file existence

MediaRef instances are typically found within {class}`~cdl_convert.decision.ColorDecision` objects, linking color corrections to specific media files.

## Creating MediaRef

### Basic Creation

Create a MediaRef with a file path:

```python
import cdl_convert as cdl

# Simple file reference
media = cdl.MediaRef('footage/shot_001.mov')

# Image sequence
media = cdl.MediaRef('renders/shot_001.0001.exr')

# Directory reference
media = cdl.MediaRef('footage/dailies/')
```

### With URI Protocol

MediaRef supports URI protocols:

```python
# HTTP reference
media = cdl.MediaRef('http://server.com/media/shot_001.mov')

# File protocol
media = cdl.MediaRef('file:///mnt/storage/footage/shot_001.mov')

# Custom protocol
media = cdl.MediaRef('smb://nas/projects/film/shot_001.mov')
```

### With Parent ColorDecision

Optionally specify the parent ColorDecision:

```python
cc = cdl.ColorCorrection(id='shot_001')
decision = cdl.ColorDecision(cc)

# Create MediaRef with parent
media = cdl.MediaRef('footage/shot_001.mov', parent=decision)
```

## Accessing Path Components

MediaRef breaks URIs into components for easy manipulation:

### Complete Reference

```python
media = cdl.MediaRef('http://server.com/footage/dailies/shot_001.mov')

# Get complete URI
>>> media.ref
'http://server.com/footage/dailies/shot_001.mov'

# Get path without protocol
>>> media.path
'footage/dailies/shot_001.mov'
```

### Protocol

```python
>>> media.protocol
'http'

# Set protocol
media.protocol = 'https'
>>> media.ref
'https://server.com/footage/dailies/shot_001.mov'

# Remove protocol
media.protocol = ''
>>> media.ref
'footage/dailies/shot_001.mov'
```

### Directory

```python
>>> media.directory
'footage/dailies'

# Change directory
media.directory = 'renders/final'
>>> media.ref
'http://server.com/renders/final/shot_001.mov'
```

### Filename

```python
>>> media.filename
'shot_001.mov'

# Change filename
media.filename = 'shot_001_v02.mov'
>>> media.ref
'http://server.com/footage/dailies/shot_001_v02.mov'
```

## Path Manipulation

### Changing Complete Reference

Replace the entire URI:

```python
media = cdl.MediaRef('old/path/file.mov')

# Set new complete reference
media.ref = 'new/path/different_file.mov'
>>> media.ref
'new/path/different_file.mov'
```

### Preserving Path Separators

MediaRef preserves the original path separator style:

```python
# Unix-style paths
media = cdl.MediaRef('footage/shot_001.mov')
>>> media.path
'footage/shot_001.mov'

# Windows-style paths
media = cdl.MediaRef('footage\\shot_001.mov')
>>> media.path
'footage\\shot_001.mov'

# Mixed paths default to forward slash
media = cdl.MediaRef('footage/dailies\\shot_001.mov')
media.directory = 'renders'
>>> media.path
'renders/shot_001.mov'
```

### Converting Absolute to Relative Paths

```python
# Start with absolute path
media = cdl.MediaRef('/mnt/storage/footage/shot_001.mov')
>>> media.is_abs
True

# Convert to relative
media.directory = 'footage'
>>> media.is_abs
False
>>> media.path
'footage/shot_001.mov'
```

## Image Sequence Detection

MediaRef automatically detects image sequences and provides sequence information:

### Detecting Sequences

```python
# Single frame from sequence
media = cdl.MediaRef('renders/shot_001.0001.exr')

>>> media.is_seq
True
>>> media.seq
'shot_001.####.exr'
```

### Sequence Patterns

MediaRef recognizes multiple sequence patterns:

```python
# Numeric padding
media = cdl.MediaRef('image.0001.exr')
>>> media.seq
'image.####.exr'

# Different padding lengths
media = cdl.MediaRef('image.001.exr')
>>> media.seq
'image.###.exr'

# Printf-style formatting
media = cdl.MediaRef('image.%04d.exr')
>>> media.seq
'image.%04d.exr'

# Hash padding
media = cdl.MediaRef('image.####.exr')
>>> media.seq
'image.####.exr'
```

### Working with Directories

When pointing to a directory, MediaRef can detect all sequences within:

```python
# Directory containing multiple sequences
media = cdl.MediaRef('renders/shot_001/')

>>> media.is_dir
True
>>> media.is_seq
True
>>> media.seqs
['shot_001_beauty.####.exr', 'shot_001_depth.####.exr', 'shot_001_normals.####.exr']

# Get first sequence
>>> media.seq
'shot_001_beauty.####.exr'
```

## File System Operations

### Checking Existence

```python
media = cdl.MediaRef('footage/shot_001.mov')

>>> media.exists
True

# Check if it's a directory
>>> media.is_dir
False

# Check if path is absolute
>>> media.is_abs
False
```

### Handling Non-Existent Paths

```python
media = cdl.MediaRef('footage/missing_file.mov')

>>> media.exists
False

# With strict error checking
cdl.config.HALT_ON_ERROR = True

# This will raise ValidationError for non-existent directories
try:
    media = cdl.MediaRef('nonexistent_dir/')
    _ = media.is_seq  # Triggers sequence detection
except cdl.ValidationError as e:
    print(f"Path validation failed: {e}")
```

## Common Use Cases

### Fixing Broken Paths

Update directory paths without touching filenames:

```python
# Original path is broken
media = cdl.MediaRef('/old/server/footage/shot_001.mov')

# Fix just the directory
media.directory = '/mnt/new_server/footage'
>>> media.ref
'/mnt/new_server/footage/shot_001.mov'
```

### Converting Absolute to Relative

```python
# Absolute path from another system
media = cdl.MediaRef('file:///Volumes/ProjectA/footage/shot_001.mov')

# Convert to relative path
media.protocol = ''
media.directory = './footage'
>>> media.ref
'./footage/shot_001.mov'
```

## Advanced Features

### URI Component Dataclass

MediaRef uses a {class}`~cdl_convert.decision.MediaRefInfo` dataclass internally:

```python
media = cdl.MediaRef('http://server.com/footage/shot_001.mov')

# Access internal info structure (not typically needed)
>>> media._ref_info.protocol
'http'
>>> media._ref_info.directory
'footage'
>>> media._ref_info.filename
'shot_001.mov'
>>> media._ref_info.original_uri
'http://server.com/footage/shot_001.mov'
```

### Class-Level Tracking

MediaRef maintains a class-level dictionary of all instances:

```python
# Create multiple references
media1 = cdl.MediaRef('shot_001.mov')
media2 = cdl.MediaRef('shot_002.mov')
media3 = cdl.MediaRef('shot_001.mov')  # Same as media1

# Check members dictionary
>>> 'shot_001.mov' in cdl.MediaRef.members
True
>>> len(cdl.MediaRef.members['shot_001.mov'])
2  # media1 and media3

# Reset tracking
cdl.MediaRef.reset_members()
>>> cdl.MediaRef.members
{}
```

## See Also

- {doc}`usage_cdl` - Working with ColorDecision
- {doc}`usage_ccc` - Working with ColorCollection
- {class}`~cdl_convert.decision.MediaRef` - API reference
- {class}`~cdl_convert.decision.MediaRefInfo` - MediaRefInfo dataclass
- {class}`~cdl_convert.decision.SequenceInfo` - SequenceInfo dataclass
