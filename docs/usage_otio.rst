*******************
OTIO Format Support
*******************

``cdl_convert`` supports parsing OpenTimelineIO (.otio) timeline files that contain
embedded CDL metadata. This allows for seamless integration with OTIO-based workflows
and applications.

OTIO CDL Metadata Structure
===========================

When working with OpenTimelineIO files, ``cdl_convert`` expects CDL metadata to be
stored in clip metadata following the standard OTIO CDL conventions:

.. code-block:: python

    clip.metadata['cdl'] = {
        'asc_sop': {
            'slope': [1.2, 1.0, 0.8],
            'offset': [0.1, 0.0, -0.1], 
            'power': [1.0, 1.1, 0.9]
        },
        'asc_sat': 1.2
    }

Required Structure
------------------

- **asc_sop**: Dictionary containing slope, offset, and power values
  
  - **slope**: List of three float values for RGB slope
  - **offset**: List of three float values for RGB offset  
  - **power**: List of three float values for RGB power

- **asc_sat**: Single float value for saturation

Timeline Support
================

``cdl_convert`` supports various OTIO timeline structures:

- **Single-track timelines**: Simple timelines with one video track
- **Multi-track timelines**: Complex timelines with multiple video and audio tracks
- **Nested compositions**: Timelines containing sub-timelines and nested structures
- **Mixed content**: Timelines where only some clips contain CDL metadata

Clips without CDL metadata are automatically skipped during parsing.

Usage Examples
==============

Command Line Usage
------------------

Convert an OTIO timeline to CDL formats:

.. code-block:: bash

    # Convert to Color Correction Collection
    $ cdl_convert timeline.otio -o ccc
    
    # Convert to multiple formats
    $ cdl_convert project_timeline.otio -o cc,ccc,cdl
    
    # Specify output directory
    $ cdl_convert timeline.otio -d ./cdl_output/ -o ccc

Python API Usage
----------------

Parse OTIO files programmatically:

.. code-block:: python

    import cdl_convert as cdl
    
    # Parse OTIO timeline
    collection = cdl.parse_otio('timeline.otio')
    
    # Access extracted color corrections
    for cc in collection.color_corrections:
        print(f"Clip: {cc.id}")
        print(f"Slope: {cc.slope}")
        print(f"Saturation: {cc.sat}")

Error Handling
==============

``cdl_convert`` provides comprehensive error handling for OTIO files:

- **Missing OTIO**: Clear error if OpenTimelineIO is not installed
- **Malformed files**: Descriptive errors for corrupted .otio files
- **Invalid CDL data**: Warnings for incomplete or malformed CDL metadata
- **Empty timelines**: Graceful handling of timelines without CDL data

Validation and Checking
=======================

Use the ``--check`` flag to validate CDL values extracted from OTIO files:

.. code-block:: bash

    $ cdl_convert timeline.otio --check --no-output
    
This will flag any unusual CDL values without writing output files, useful for
validating OTIO timeline CDL metadata before conversion.

Compatibility
=============

OTIO format support requires:

- **OpenTimelineIO**: Version 0.17.0 or higher
- **Python**: 3.11 or higher (as required by cdl_convert)

The OTIO parser uses OpenTimelineIO's built-in JSON adapter, so no additional
adapter packages are required for basic .otio file support.