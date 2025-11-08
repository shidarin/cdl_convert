# OTIO Format Support

`cdl_convert` supports parsing OpenTimelineIO (.otio) timeline files that contain embedded CDL metadata. This allows for seamless integration with OTIO-based workflows and applications.

## OTIO CDL Metadata Structure

When working with OpenTimelineIO files, `cdl_convert` expects CDL metadata to be stored in clip metadata following the standard OTIO CDL conventions:

```python
clip.metadata['cdl'] = {
    'asc_sop': {
        'slope': [1.2, 1.0, 0.8],
        'offset': [0.1, 0.0, -0.1], 
        'power': [1.0, 1.1, 0.9]
    },
    'asc_sat': 1.2
}
```

### Required Structure

- **asc_sop**: Dictionary containing slope, offset, and power values
  
  - **slope**: List of three float values for RGB slope
  - **offset**: List of three float values for RGB offset  
  - **power**: List of three float values for RGB power

- **asc_sat**: Single float value for saturation

## Timeline Support

`cdl_convert` supports various OTIO timeline structures:

- **Single-track timelines**: Simple timelines with one video track
- **Multi-track timelines**: Complex timelines with multiple video and audio tracks
- **Nested compositions**: Timelines containing sub-timelines and nested structures
- **Mixed content**: Timelines where only some clips contain CDL metadata

Clips without CDL metadata are automatically skipped during parsing.
