#!/usr/bin/env python
"""CDL Convert Parse Module

Parsing functions for converting CDL files to cdl_convert objects.

Public Functions:
    parse_ale(Union[str, Path]) -> ColorCollection: Parse Avid Log Exchange
        files.

    parse_cc(Union[str, Path]) -> ColorCorrection: Parse XML Color Correction
        files.

    parse_ccc(Union[str, Path]) -> ColorCollection: Parse XML Color Correction
        Collection files.

    parse_cdl(Union[str, Path]) -> ColorCollection: Parse XML Color Decision
        List files.

    parse_cmx(Union[str, Path]) -> ColorCollection: Parse CMX EDL files
        using OpenTimelineIO adapter.

    parse_file(Union[str, Path], Optional[str]) -> Union[ColorCorrection, ColorCollection]:
        Format detection and parsing.

    parse_flex(Union[str, Path]) -> ColorCollection: Parse Film Log EDL
        Exchange files.

    parse_otio(Union[str, Path]) -> ColorCollection: Parse OpenTimelineIO
        timeline files.

    parse_rnh_cdl(Union[str, Path]) -> ColorCorrection: Parse Rhythm & Hues
        space-separated CDL files.

Global Configuration:
    INPUT_FORMATS: Type-safe dictionary mapping file extensions to parser
        functions for automatic format detection and processing.

Example Usage:
    >>> from pathlib import Path
    >>> from cdl_convert import parse_file, parse_ale
    >>> 
    >>> # File parsing with pathlib
    >>> input_file = Path("input.ale")
    >>> collection = parse_file(input_file)
    >>> print(f"Found {len(collection.color_corrections)} corrections")
    >>> 
    >>> # Specific format parsing
    >>> try:
    ...     ale_collection = parse_ale(input_file)
    ... except ParseError as e:
    ...     print(f"Parse error: {e}")
    ... except ValidationError as e:
    ...     print(f"Validation error: {e}")

## License

The MIT License (MIT)

cdl_convert
Copyright (c) 2015-2025 Sean Wallitsch
http://github.com/shidarin/cdl_convert/

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

# ==============================================================================
# IMPORTS
# ==============================================================================



# Standard Imports

from pathlib import Path
import re
from typing import List, Optional, Union
from xml.etree import ElementTree

# cdl_convert imports

from . import config, collection, correction
from .exceptions import ParseError, ValidationError, OTIOAdapterError

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'parse_ale',
    'parse_cc',
    'parse_ccc',
    'parse_cdl',
    'parse_cmx',
    'parse_file',
    'parse_flex',
    'parse_otio',
    'parse_rnh_cdl'
]

# ==============================================================================
# FUNCTIONS
# ==============================================================================


def parse_ale(input_file: Union[str, Path]) -> collection.ColorCollection:
    """Parse an Avid Log Exchange (ALE) file for CDL color corrections using OTIO.

    Parses an ALE file to extract ASC CDL color correction data embedded as
    ASC_SOP and ASC_SAT columns. This function uses the OpenTimelineIO 
    otio-ale-adapter for ALE parsing and CDL metadata extraction.

    CDL data appears in ALE files as tab-delimited columns:
    - ASC_SOP: (slope_r slope_g slope_b)(offset_r offset_g offset_b)(power_r power_g power_b)
    - ASC_SAT: saturation_value

    Args:
        input_file (Union[str, Path]): The filepath to the ALE file.

    Returns:
        ColorCollection: A collection containing all found ColorCorrections
            with the collection type set to 'ccc'.

    Raises:
        OTIOAdapterError: If otio-ale-adapter is not installed or available.
        ParseError: If ALE file cannot be parsed by OpenTimelineIO adapter.
        ValidationError: If color correction values fail validation.
        FileNotFoundError: If the input file does not exist.

    Example:
        >>> ale_collection = parse_ale("project.ale")
        >>> print(f"Found {len(ale_collection.color_corrections)} clips with CDL")

    """
    # Check that the required OTIO adapter is available
    _check_otio_adapter('ale')
    
    try:
        import opentimelineio as otio
        
        # Use OTIO adapter to read the ALE file
        clip_collection = otio.adapters.read_from_file(input_file)
        
        # Extract CDL metadata from the clip collection
        cdl_corrections = _extract_cdl_from_ale_collection(clip_collection, input_file)
        
    except Exception as e:
        raise ParseError(
            f"Failed to parse ALE file '{input_file}' "
            f"with OTIO ale adapter: {e}"
        )

    # Create and return ColorCollection
    ccc = collection.ColorCollection()
    ccc.file_in = input_file
    ccc.append_children(cdl_corrections)

    return ccc

# ==============================================================================


def parse_cc(input_file: Union[str, Path, ElementTree.Element]) -> correction.ColorCorrection:  # pylint: disable=R0912
    """Parse XML Color Correction (.cc) file or element.
    
    Parses a single ColorCorrection XML element containing ASC CDL values.
    CC files represent individual color corrections and are commonly used
    for single-shot CDL exchange instead of larger CDL or CCC files.
    
    The parser extracts SOP (Slope, Offset, Power) and Saturation values
    along with descriptions, input/viewing colorspace information, and
    other metadata from the XML structure.
    
    Args:
        input_file (Union[str, Path, ElementTree.Element]): File path to
            CC file or pre-parsed ElementTree Element containing
            ColorCorrection data.
            
    Returns:
        ColorCorrection: ColorCorrection instance with parsed CDL values
            and metadata.
            
    Raises:
        ParseError: If XML structure is invalid or required elements missing.
        ValidationError: If CDL values fail validation checks.
        FileNotFoundError: If input file path does not exist.
        
    Example:
        >>> cc = parse_cc("shot_001.cc")
        >>> print(f"ID: {cc.id}, Slope: {cc.slope}")

    """
    # Use match statement for input type handling
    match input_file:
        case str() | Path():
            root = _remove_xmlns(input_file)
            file_in = input_file
        case ElementTree.Element():
            root = input_file
            file_in = None
        case _:
            raise ParseError(
                f"Invalid input type: {type(input_file).__name__}. "
                f"Expected str, Path, or ElementTree.Element."
            )

    # Use match statement for XML root tag validation
    match root.tag:
        case 'ColorCorrection':
            pass  # Valid CC file
        case _:
            raise ParseError(
                f'Invalid CC file format: expected root element "ColorCorrection", found "{root.tag}". '
                f'This file does not appear to be a valid ASC CDL ColorCorrection (.cc) file.'
            )

    try:
        cc_id = root.attrib['id']
    except KeyError:
        if config.config.halt_on_error:
            raise ParseError(
                'Missing required "id" attribute on ColorCorrection element. '
                'ASC CDL ColorCorrection elements must have an "id" attribute for identification.'
            )
        else:
            cc_id = None

    cdl = correction.ColorCorrection(cc_id)
    if file_in:
        cdl.file_in = file_in

    # Grab our descriptions and add them to the cdl.
    cdl.parse_xml_descs(root)
    # See if we have a viewing description.
    cdl.parse_xml_viewing_desc(root)
    # See if we have an input description.
    cdl.parse_xml_input_desc(root)

    def find_required(elem, names):
        """Finds the required element and returns the found value.

        Args:
            root : <ElementTree.Element>
                The element to search in.

            names : [str]
                A list of names the element might be under.

        Raises:
            ValueError:
                If element does not contain the required name.

        Returns:
            <ElementTree.Element>

        """
        found_element = None

        for possibility in names:
            found_element = elem.find(possibility)
            if found_element is not None:
                break

        # element might never have been triggered.
        if found_element is None:
            raise ValueError(
                f'The ColorCorrection element could not be parsed because the '
                f'XML is missing required elements: {str(names)}'
            )
        else:
            return found_element

    try:
        sop_xml = find_required(root, correction.SopNode.element_names)
    except ValueError:
        sop_xml = None
    try:
        sat_xml = find_required(root, correction.SatNode.element_names)
    except ValueError:
        sat_xml = None

    if sop_xml is None and sat_xml is None:
        raise ParseError(
            'Incomplete ColorCorrection: missing both SOP and SAT nodes. '
            'A valid ColorCorrection must contain at least one of: '
            'SOPNode/SopNode (slope, offset, power) or SATNode/SatNode (saturation).'
        )

    if sop_xml is not None:
        cdl.slope = find_required(sop_xml, ['Slope']).text.split()
        cdl.offset = find_required(sop_xml, ['Offset']).text.split()
        cdl.power = find_required(sop_xml, ['Power']).text.split()

        # Calling the slope, offset and power attributes on the cdl will have
        # created an instance of SopNode on cdl.sop_node, so we can populate
        # those descriptions.
        cdl.sop_node.parse_xml_descs(sop_xml)

    if sat_xml is not None:
        cdl.sat = find_required(sat_xml, ['Saturation']).text

        # In the same manor of sop, we can call the sat node now to set the
        # desc descriptions.
        cdl.sat_node.parse_xml_descs(sat_xml)

    return cdl

# ==============================================================================


def parse_ccc(input_file: Union[str, Path]) -> collection.ColorCollection:
    """Parse XML Color Correction Collection (.ccc) file.
    
    Parses a ColorCorrectionCollection XML file containing multiple
    ColorCorrection elements. CCC files are collections of individual
    color corrections without ColorDecision or MediaRef elements.
    
    The parser extracts all ColorCorrection elements along with collection-
    level descriptions, InputDescription (source colorspace), and
    ViewingDescription (viewing environment and hardware) metadata.
    
    Args:
        input_file (Union[str, Path]): File path to CCC file to parse.
        
    Returns:
        ColorCollection: Collection containing all found ColorCorrections
            with type set to 'ccc' and parsed metadata.
            
    Raises:
        ParseError: If XML structure is invalid or root element is not
            ColorCorrectionCollection.
        ValidationError: If CDL values fail validation checks.
        FileNotFoundError: If input file path does not exist.
        
    Example:
        >>> ccc = parse_ccc("show_corrections.ccc")
        >>> print(f"Found {len(ccc.color_corrections)} corrections")

    """
    root = _remove_xmlns(input_file)

    # Use match statement for XML root tag validation
    match root.tag:
        case 'ColorCorrectionCollection':
            pass  # Valid CCC file
        case _:
            raise ParseError(
                f'Invalid CCC file format: expected root element "ColorCorrectionCollection", found "{root.tag}". '
                f'This file does not appear to be a valid ASC CDL ColorCorrectionCollection (.ccc) file.'
            )

    ccc = collection.ColorCollection()
    ccc.set_to_ccc()
    ccc.file_in = input_file

    # Grab our descriptions and add them to the ccc.
    ccc.parse_xml_descs(root)
    # See if we have a viewing description.
    ccc.parse_xml_viewing_desc(root)
    # See if we have an input description.
    ccc.parse_xml_input_desc(root)
    # Add all of our found color corrections. If the parse_xml returns False,
    # (for no CCs found) we raise a value error.
    if not ccc.parse_xml_color_corrections(root):
        raise ParseError(
            'Empty ColorCorrectionCollection: no ColorCorrection elements found. '
            'A valid CCC file must contain at least one ColorCorrection element.'
        )

    return ccc

# ==============================================================================


def parse_cdl(input_file: Union[str, Path]) -> collection.ColorCollection:
    """Parse XML Color Decision List (.cdl) file.
    
    Parses a ColorDecisionList XML file containing ColorDecision elements
    that link ColorCorrections with MediaRef elements. CDL files represent
    the complete ASC CDL workflow including media references.
    
    The parser extracts all ColorDecision elements along with collection-
    level descriptions, InputDescription (source colorspace), and
    ViewingDescription (viewing environment and hardware) metadata.
    
    Args:
        input_file (Union[str, Path]): File path to CDL file to parse.
        
    Returns:
        ColorCollection: Collection containing all found ColorDecisions
            with type set to 'cdl' and parsed metadata.
            
    Raises:
        ParseError: If XML structure is invalid or root element is not
            ColorDecisionList.
        ValidationError: If CDL values fail validation checks.
        FileNotFoundError: If input file path does not exist.
        
    Example:
        >>> cdl = parse_cdl("project_decisions.cdl")
        >>> print(f"Found {len(cdl.color_decisions)} decisions")

    """
    root = _remove_xmlns(input_file)

    # Use match statement for XML root tag validation
    match root.tag:
        case 'ColorDecisionList':
            pass  # Valid CDL file
        case _:
            raise ParseError(
                f'Invalid CDL file format: expected root element "ColorDecisionList", found "{root.tag}". '
                f'This file does not appear to be a valid ASC CDL ColorDecisionList (.cdl) file.'
            )

    cdl = collection.ColorCollection()
    cdl.set_to_cdl()
    cdl.file_in = input_file

    # Grab our descriptions and add them to the ccc.
    cdl.parse_xml_descs(root)
    # See if we have a viewing description.
    cdl.parse_xml_viewing_desc(root)
    # See if we have an input description.
    cdl.parse_xml_input_desc(root)
    # Add all of our found color decisions. If the parse_xml returns False,
    # (for no CDs found) we raise a value error.
    if not cdl.parse_xml_color_decisions(root):
        raise ParseError(
            'Empty ColorDecisionList: no ColorDecision elements found. '
            'A valid CDL file must contain at least one ColorDecision element.'
        )

    return cdl

# ==============================================================================


def parse_cmx(input_file: Union[str, Path]) -> collection.ColorCollection:
    """Parse CMX EDL file for ASC CDL color correction information using OTIO.
    
    Parses a CMX Edit Decision List file to extract ASC CDL color correction
    data embedded as *ASC_SOP and *ASC_SAT comments. This function uses the
    OpenTimelineIO otio-cmx3600-adapter for EDL parsing and timeline structure
    handling
    
    CDL data appears in CMX EDL files as comment lines following edit entries:

    ASC_SOP (slope_r slope_g slope_b)(offset_r offset_g offset_b)(power_r power_g power_b)
    ASC_SAT saturation_value
    
    ```
    001  DS0010.bg1 V     C     00:08:07:23 00:08:16:10 01:00:00:00 01:00:08:11
    *ASC_SOP (1.45 1.22 1.15)(-0.14 -0.11 -0.11)(1.00 1.00 1.00)
    *ASC_SAT 0.773000
    ```
    
    Args:
        input_file (Union[str, Path]): File path to CMX EDL file to parse.
        
    Returns:
        ColorCollection: Collection containing ColorCorrections extracted
            from EDL with clip names as IDs and filename as source.
            
    Raises:
        OTIOAdapterError: If otio-cmx3600-adapter is not installed or available.
        ParseError: If EDL file cannot be parsed by OpenTimelineIO adapter.
        FileNotFoundError: If input file path does not exist.
        
    Example:
        >>> edl_collection = parse_cmx("project.edl")
        >>> print(f"Found {len(edl_collection.color_corrections)} clips with CDL")

    """
    # Check that the required OTIO adapter is available
    _check_otio_adapter('cmx_3600')
    
    try:
        import opentimelineio as otio
        
        # Use OTIO adapter to read the CMX EDL file
        timeline = otio.adapters.read_from_file(input_file)
        
        # Extract CDL metadata from the timeline
        cdl_corrections = _extract_cdl_metadata(timeline, input_file)
        
    except Exception as e:
        raise ParseError(
            f"Failed to parse CMX EDL file '{input_file}'" 
            f"with OTIO cmx_3600 adapter: {e}"
        )

    # Create and return ColorCollection
    ccc = collection.ColorCollection()
    ccc.file_in = input_file
    ccc.append_children(cdl_corrections)

    return ccc

# ==============================================================================


def parse_flex(input_file: Union[str, Path]) -> collection.ColorCollection:  # pylint: disable=R0912,R0914
    """Parse DaVinci FLEx telecine EDL file for ASC CDL information.
    
    Parses a Film Log EDL Exchange (FLEx) file from DaVinci telecine systems.
    FLEx uses a strict line-based format with fixed character positions for
    data fields rather than delimited values.
    
    The parser extracts ASC CDL data from line types 701 (SOP values) and
    702 (Saturation values), along with shot identification from line 100
    (slate information) and project title from line 010.
    
    FLEx Format Structure:
    - Lines 000-099: Session information
    - Line 010: Project title (chars 10-79)
    - Line 100: Slate info - Scene (10-17), Take (24-31), Reel (42-49)
    - Line 701: ASC SOP values (space-separated)
    - Line 702: ASC SAT value (space-separated)
    
    Args:
        input_file (Union[str, Path]): File path to FLEx EDL file to parse.
        
    Returns:
        ColorCollection: Collection containing ColorCorrections extracted
            from FLEx with shot identifiers derived from slate information
            or project title.
            
    Raises:
        ParseError: If FLEx file format is invalid or cannot be parsed.
        ValidationError: If CDL values fail validation checks.
        FileNotFoundError: If input file path does not exist.
        
    Example:
        >>> flex_collection = parse_flex("telecine_session.flex")
        >>> print(f"Found {len(flex_collection.color_corrections)} shots")

    """

    cdls = []

    filename = Path(input_file).stem

    title = None
    # Metadata will store, in order, the various scene, take, reel fields
    # it finds.
    metadata = []

    sop = {}
    sat = None

    def build_cc(line_id, edl_path, sop_dict, sat_value, title_line):
        """Build ColorCorrection from FLEx EDL data if CDL values are present.
        
        Creates a ColorCorrection instance from parsed FLEx data, setting
        SOP values, saturation, and description if available.
        
        Args:
            line_id: Identifier for the color correction.
            edl_path: Source EDL file path.
            sop_dict: Dictionary with 'slope', 'offset', 'power' keys or None.
            sat_value: Saturation value or None.
            title_line: Project title for description or None.
            
        Returns:
            ColorCorrection: ColorCorrection with parsed CDL values.

        """
        col_cor = correction.ColorCorrection(line_id, edl_path)
        if title_line:
            col_cor.desc = title_line
        if sop_dict:
            # If it finds the 701 line, it will have all three
            col_cor.slope = sop_dict['slope']
            col_cor.offset = sop_dict['offset']
            col_cor.power = sop_dict['power']
        if sat_value:
            col_cor.sat = sat_value

        return col_cor

    with open(input_file, 'r') as edl:
        for line in edl:
            # Use match statement for line prefix detection
            line_prefix = line[:3]
            match line_prefix:
                case '100':
                    # This is the start of a take/shot
                    # We need to dump the previous records to a CDL
                    # Then clear the records.
                    # Note that the first data line will also hit this.
                    metadata = [i for i in metadata if i != '']
                    if metadata:
                        cc_id = '_'.join(metadata)
                    else:
                        field = title if title else filename
                        cc_id = field + str(len(cdls) + 1).rjust(3, '0')

                    # If we already have values:
                    if sop or sat:
                        cdl = build_cc(cc_id, input_file, sop, sat, title)
                        cdls.append(cdl)

                    metadata = []
                    sop = {}
                    sat = None

                case '010':
                    # Title Line
                    # 10-79 Title
                    title = line[10:80].strip()
                    
                case '110':
                    # Slate Information
                    # 10-17 Scene
                    # 24-31 Take ID
                    # 42-49 Camera Reel ID
                    metadata = [
                        line[10:18].strip(),  # Scene
                        line[24:32].strip(),  # Take
                        line[42:50].strip(),  # Reel
                    ]
                    
                case '701':
                    # ASC SOP
                    # 701 ASC_SOP(# # #)(-# -# -#)(# # #)
                    sop = {
                        'slope': line[12:32].split(),
                        'offset': line[34:57].split(),
                        'power': line[59:79].split()
                    }
                    
                case '702':
                    # ASC SAT
                    # 702 ASC_SAT ######
                    sat = line.split()[-1]

    # We need to dump the last record to the cdl list
    metadata = [i for i in metadata if i != '']
    if metadata:
        cc_id = '_'.join(metadata)
    else:
        field = title if title else filename
        cc_id = field + str(len(cdls) + 1).rjust(3, '0')

    # If we found values at all:
    if sop or sat:
        cdl = build_cc(cc_id, input_file, sop, sat, title)
        cdls.append(cdl)

    ccc = collection.ColorCollection()
    ccc.file_in = input_file
    ccc.append_children(cdls)

    return ccc

# ==============================================================================


def parse_otio(input_file: Union[str, Path]) -> collection.ColorCollection:
    """Parse OpenTimelineIO (.otio) timeline file for ASC CDL color corrections.

    Parses an OTIO timeline file to extract ASC CDL color correction data
    embedded in clip metadata. This function uses OpenTimelineIO's native
    deserialization to read .otio files and extract CDL metadata from all
    clips in the timeline structure.

    CDL data appears in OTIO files as clip metadata:
    clip.metadata['cdl'] = {
        'asc_sop': {
            'slope': [float, float, float],
            'offset': [float, float, float],
            'power': [float, float, float]
        },
        'asc_sat': float
    }

    Args:
        input_file (Union[str, Path]): The filepath to the .otio file.

    Returns:
        ColorCollection: A collection containing all found ColorCorrections
            with the collection type set to 'ccc'.

    Raises:
        OTIOAdapterError: If OpenTimelineIO is not installed or available.
        ParseError: If .otio file cannot be parsed by OpenTimelineIO.
        ValidationError: If color correction values fail validation.
        FileNotFoundError: If the input file does not exist.

    Example:
        >>> otio_collection = parse_otio("timeline.otio")
        >>> print(f"Found {len(otio_collection.color_corrections)} clips with CDL")

    """
    # Check that OTIO is available (using built-in JSON adapter)
    _check_otio_adapter('otio_json')
    
    try:
        import opentimelineio as otio
        
        # Use OTIO's native deserialization for .otio files
        timeline = otio.adapters.read_from_file(input_file)
        
        # Extract CDL metadata from the timeline
        cdl_corrections = _extract_cdl_metadata(timeline, input_file)
        
    except Exception as e:
        raise ParseError(
            f"Failed to parse OTIO file '{input_file}': {e}"
        )

    # Create and return ColorCollection
    ccc = collection.ColorCollection()
    ccc.file_in = input_file
    ccc.append_children(cdl_corrections)

    return ccc

# ==============================================================================


def parse_rnh_cdl(input_file: Union[str, Path]) -> correction.ColorCorrection:
    """Parse Rhythm & Hues space-separated CDL file format.
    
    Parses a simple text file containing a single line with 10 space-separated
    numeric values representing ASC CDL parameters. This format was used
    internally by Rhythm & Hues for shot and sequence level color correction
    data in their playback software.
    
    The format contains exactly 10 values in ASC CDL order of operations:
    
    `SlopeR SlopeG SlopeB OffsetR OffsetG OffsetB PowerR PowerG PowerB Sat`
    
    Args:
        input_file (Union[str, Path]): File path to space-separated CDL file.
        
    Returns:
        ColorCorrection: Single ColorCorrection with filename (without
            extension) as ID and parsed CDL values.
            
    Raises:
        ParseError: If file format is invalid or values cannot be parsed.
        ValidationError: If CDL values fail validation checks.
        FileNotFoundError: If input file path does not exist.
        IndexError: If file does not contain exactly 10 space-separated values.
        
    Example:
        >>> cc = parse_rnh_cdl("shot_001.cdl")
        >>> print(f"Slope: {cc.slope}, Saturation: {cc.sat}")
    """

    with open(input_file, 'r') as cdl_f:
        # We only need to read the first line
        line = cdl_f.readline()
        line = line.split()

        # The filename without extension will become the id
        filename = Path(input_file).stem

        slope = [line[0], line[1], line[2]]
        offset = [line[3], line[4], line[5]]
        power = [line[6], line[7], line[8]]

        sat = line[9]

        cdl = correction.ColorCorrection(filename, input_file)

        cdl.slope = slope
        cdl.offset = offset
        cdl.power = power
        cdl.sat = sat

    return cdl

# ==============================================================================
# OTIO HELPER FUNCTIONS
# ==============================================================================


def _check_otio_adapter(adapter_name: str) -> None:
    """Check if specific OTIO adapter is available.
    
    Validates that OpenTimelineIO is installed and that the specified
    adapter is available for use. Raises OTIOAdapterError with clear
    installation instructions if the adapter is missing.
    
    Args:
        adapter_name (str): Name of the OTIO adapter to check
            (e.g., 'cmx_3600', 'ale').
        
    Raises:
        OTIOAdapterError: If OpenTimelineIO is not installed or if the
            specified adapter is not available.
            
    Example:
        >>> _check_otio_adapter('cmx_3600')  # Validates CMX adapter
        >>> _check_otio_adapter('ale')       # Validates ALE adapter
    """
    try:
        import opentimelineio as otio
    except ImportError:
        raise OTIOAdapterError(
            "OpenTimelineIO not installed. Install with: "
            "pip install OpenTimelineIO"
        )
    
    try:
        available_adapters = otio.adapters.available_adapter_names()
        if adapter_name not in available_adapters:
            # Provide specific installation instructions based on adapter
            if adapter_name == 'cmx_3600':
                install_cmd = "pip install otio-cmx3600-adapter>=1.0.0"
            elif adapter_name == 'ale':
                install_cmd = "pip install otio-ale-adapter>=1.0.0"
            elif adapter_name == 'otio_json':
                # Built-in adapter should always be available with OTIO
                raise OTIOAdapterError(
                    f"Built-in OTIO adapter '{adapter_name}' not available. "
                    f"This may indicate an OpenTimelineIO installation issue."
                )
            else:
                install_cmd = f"pip install otio-{adapter_name}-adapter"
                
            raise OTIOAdapterError(
                f"Missing required OTIO adapter: '{adapter_name}'. "
                f"Install with: {install_cmd}"
            )
    except Exception as e:
        # Handle any other OTIO-related errors
        raise OTIOAdapterError(
            f"Error checking OTIO adapter availability: {e}"
        )


def _extract_cdl_from_otio_clip(clip, source_file: Union[str, Path]) -> Optional[correction.ColorCorrection]:
    """Extract CDL metadata from OTIO clip object.
    
    Extracts ASC CDL color correction data from an OpenTimelineIO clip's
    metadata structure and creates a ColorCorrection object. Handles
    missing or malformed CDL metadata gracefully by returning None.

    Will convert OpenTimelineIO's AnyDictionary and AnyVector types to
    normal dict and list types.

    Expected OTIO CDL metadata structure:
        clip.metadata['cdl'] = {
            'asc_sop': {
                'slope': [float, float, float],
                'offset': [float, float, float], 
                'power': [float, float, float]
            },
            'asc_sat': float
        }
    
    Args:
        clip: OTIO clip object containing potential CDL metadata.
        source_file (Union[str, Path]): Source file path for ColorCorrection.
        
    Returns:
        Optional[ColorCorrection]: ColorCorrection object with extracted CDL
            values, or None if no valid CDL metadata is found.
            
    Example:
        >>> cc = _extract_cdl_from_otio_clip(otio_clip, "input.edl")
        >>> if cc:
        ...     print(f"Extracted CDL for {cc.id}")

    """
    # Check if clip has CDL metadata
    if not hasattr(clip, 'metadata') or 'cdl' not in clip.metadata:
        return None
        
    cdl_data = clip.metadata['cdl']
    
    # Determine clip ID - prefer Scan Filename over Name for compatibility
    clip_name = getattr(clip, 'name', 'Unknown')
    if hasattr(clip, 'metadata') and 'ALE' in clip.metadata:
        ale_metadata = clip.metadata['ALE']
        # Try to get Scan Filename first, fall back to Name
        if 'Scan Filename' in ale_metadata:
            clip_name = ale_metadata['Scan Filename']
        elif 'Name' in ale_metadata:
            clip_name = ale_metadata['Name']
    
    cc = correction.ColorCorrection(clip_name, source_file)
    
    try:
        # Extract SOP values if present
        if 'asc_sop' in cdl_data:
            sop_data = dict(cdl_data['asc_sop'])
            # Validate that sop_data is a dictionary
            if not isinstance(sop_data, dict):
                raise TypeError(
                    f"Expected dict for asc_sop, got {type(sop_data).__name__}"
                    )
            if 'slope' in sop_data:
                cc.slope = list(sop_data['slope'])
            if 'offset' in sop_data:
                cc.offset = list(sop_data['offset'])
            if 'power' in sop_data:
                cc.power = list(sop_data['power'])
                
        # Extract saturation value if present
        if 'asc_sat' in cdl_data:
            cc.sat = cdl_data['asc_sat']
            
        return cc
        
    except (KeyError, TypeError, ValueError) as e:
        # Handle malformed CDL metadata gracefully
        if config.config.halt_on_error:
            raise ParseError(
                f"Malformed CDL metadata in clip '{clip_name}': {e}"
            )
        else:
            # Return None for malformed data when not in strict mode
            return None


def _extract_cdl_metadata(timeline, source_file: Union[str, Path]) -> List[correction.ColorCorrection]:
    """Process OTIO timeline structure to extract all clips with CDL data.
    
    Iterates through all tracks and clips in an OpenTimelineIO timeline
    to extract CDL metadata and create ColorCorrection objects. Maintains
    consistent error handling across formats.
    
    Args:
        timeline: OTIO Timeline object to process.
        source_file (Union[str, Path]): Source file path for ColorCorrections.
        
    Returns:
        List[ColorCorrection]: List of ColorCorrection objects extracted
            from timeline clips that contain valid CDL metadata.
            
    Raises:
        ParseError: If timeline structure is invalid or cannot be processed.
        
    Example:
        >>> corrections = _extract_cdl_metadata(otio_timeline, "input.edl")
        >>> print(f"Found {len(corrections)} clips with CDL data")
        
    """
    cdl_corrections = []
    
    try:
        # Iterate through all tracks in the timeline
        for track in timeline.tracks:
            # OTIO tracks are list-like, iterate through clips directly
            for clip in track:
                cc = _extract_cdl_from_otio_clip(clip, source_file)
                if cc is not None:
                    cdl_corrections.append(cc)
                    
    except Exception as e:
        raise ParseError(
            f"Error processing OTIO timeline structure: {e}"
        )
        
    return cdl_corrections


def _extract_cdl_from_ale_collection(clip_collection, source_file: Union[str, Path]) -> List[correction.ColorCorrection]:
    """Process OTIO SerializableCollection from ALE adapter to extract CDL data.
    
    Iterates through all clips in an OpenTimelineIO SerializableCollection
    (returned by otio-ale-adapter) to extract CDL metadata and create 
    ColorCorrection objects. Maintains consistent error handling across formats.
    
    Args:
        clip_collection: OTIO SerializableCollection object from ALE adapter.
        source_file (Union[str, Path]): Source file path for ColorCorrections.
        
    Returns:
        List[ColorCorrection]: List of ColorCorrection objects extracted
            from collection clips that contain valid CDL metadata.
            
    Raises:
        ParseError: If collection structure is invalid or cannot be processed.
        
    Example:
        >>> corrections = _extract_cdl_from_ale_collection(otio_collection, "input.ale")
        >>> print(f"Found {len(corrections)} clips with CDL data")
        
    """
    cdl_corrections = []
    
    try:
        # ALE adapter returns a SerializableCollection of clips directly
        for clip in clip_collection:
            cc = _extract_cdl_from_otio_clip(clip, source_file)
            if cc is not None:
                cdl_corrections.append(cc)
                    
    except Exception as e:
        raise ParseError(
            f"Error processing OTIO ALE collection structure: {e}"
        )
        
    return cdl_corrections


# ==============================================================================
# PRIVATE FUNCTIONS
# ==============================================================================


def _remove_xmlns(input_file):
    """Remove xmlns namespace attribute from XML file, return parsed element.
    
    Reads XML file content, strips the xmlns namespace declaration to simplify
    parsing, and returns the parsed ElementTree root element. Handles encoding
    issues by falling back from UTF-8 to default encoding if needed.
    
    Args:
        input_file: File path to XML file to process.
        
    Returns:
        ElementTree.Element: Parsed XML root element with xmlns removed.
        
    Raises:
        ParseError: If XML cannot be parsed after xmlns removal.
        FileNotFoundError: If input file does not exist.

    """
    # We're going to open the file as a string and remove the xmlns, as
    # it doesn't do a lot for us when working with CDLs, and in fact
    # just clutters everything the hell up.
    try:
        with open(input_file, 'r', encoding='utf-8') as xml_file:
            xml_string = xml_file.read()
    except UnicodeDecodeError:
        # Fallback to default encoding if UTF-8 fails
        with open(input_file, 'r') as xml_file:
            xml_string = xml_file.read()

    xml_string = re.sub(' xmlns="[^"]+"', '', xml_string, count=1)

    try:
        return ElementTree.fromstring(xml_string)
    except ElementTree.ParseError as e:
        raise ParseError(f"Invalid XML format in file '{input_file}': {e}") from e

# ==============================================================================
# GLOBALS
# ==============================================================================

INPUT_FORMATS = {
    'ale': parse_ale,
    'ccc': parse_ccc,
    'cc': parse_cc,
    'cdl': parse_cdl,
    'edl': parse_cmx,
    'flex': parse_flex,
    'otio': parse_otio,
    'rcdl': parse_rnh_cdl,
}

# ==============================================================================
# PARSE FILE
# ==============================================================================


def parse_file(filepath: Union[str, Path], filetype: Optional[str] = None) -> Union[correction.ColorCorrection, collection.ColorCollection]:
    """Parse CDL file using automatic format detection or specified type.
    
    Determines the appropriate parser based on file extension and delegates
    to the corresponding format-specific parsing function. Supports all
    CDL-related formats including XML variants and EDL formats.
    
    Args:
        filepath (Union[str, Path]): Path to CDL file to parse.
            File must exist.
        filetype (Optional[str]): File format override. If not provided,
            format is detected from file extension. Should not include
            leading dot (e.g., 'ccc' not '.ccc').
            
    Returns:
        Union[ColorCorrection, ColorCollection]: Single ColorCorrection for
            formats like .cc and .rcdl, or ColorCollection for multi-correction
            formats like .ccc, .cdl, .ale, .edl, and .flex.
            
    Raises:
        ParseError: If file format is not supported or parsing fails.
        FileNotFoundError: If input file path does not exist.
        
    Example:
        >>> result = parse_file("project.ccc")
        >>> if isinstance(result, ColorCollection):
        ...     print(f"Found {len(result.color_corrections)} corrections")
        
    """
    if not filetype:
        filetype = Path(filepath).suffix.removeprefix('.').lower()

    # Use match statement for format validation with better error handling
    match filetype:
        case filetype if filetype in INPUT_FORMATS:
            return INPUT_FORMATS[filetype](filepath)
        case _:
            raise ParseError(
                f"Unsupported file format: '{filetype}'. "
                f"Supported formats are: {', '.join(INPUT_FORMATS.keys())}"
            )
