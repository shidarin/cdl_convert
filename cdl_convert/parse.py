#!/usr/bin/env python
"""

CDL Convert Parse
=================

Contains parser functions for converting files to cdl_convert objects.

## Public Functions

    parse_ale()
        Parses an ALE EDL file into a ColorCollection set to ccc.

    parse_cc()
        Parses an XML CC file into a ColorCorrection.

    parse_ccc()
        Parses an XML CCC file into a ColorCollection set to ccc.

    parse_cdl
        Parses an XML CDL file into a ColorCollection set to cdl.

    parse_file()
        Determines which parse function to call based on file extension (or
        provided ext arg) and calls that function. Returns result.

    parse_flex()
        Parses a FLEx EDL into a ColorCollection set to ccc.

    parse_rnh_cdl
        Parses a Rhythm & Hues Space Separated cdl file, which is based on a
        very early ASC CDL spec, into a single ColorCorrection.

## GLOBALS

    INPUT_FORMATS
        A dictionary whose keys are file extensions and values are the above
        functions. Used by ``parse_file()`` to determine what parser to call.

## License

The MIT License (MIT)

cdl_convert
Copyright (c) 2015 Sean Wallitsch
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

from __future__ import absolute_import, print_function

# Standard Imports

from ast import literal_eval
import os
import re
from xml.etree import ElementTree

# cdl_convert imports

from . import collection, correction

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'parse_ale',
    'parse_cc',
    'parse_ccc',
    'parse_cdl',
    'parse_file',
    'parse_flex',
    'parse_rnh_cdl'
]

# ==============================================================================
# FUNCTIONS
# ==============================================================================


def parse_ale(input_file):  # pylint: disable=R0914
    """Parses an Avid Log Exchange (ALE) file for CDLs

    **Args:**
        input_file : (str)
            The filepath to the ALE EDL

    **Returns:**
        (:class:`ColorCollection`)
            A collection that contains all found ColorCorrections

    **Raises:**
        N/A

    An ALE file is traditionally gathered during a telecine transfer using
    standard ASCII characters. Each line theoretically represents a single
    clip/take/shot.

    Each field of data is tab delineated. We'll be searching for the ASC_SOP,
    ASC_SAT fields, alone with the standard Scan Filename fields.

    The Data line indicates that all the following lines are comprised of
    shot information.

    """
    # When we enter a section, we're store the section name
    section = {
        'column': False,
        'data': False
    }

    # We'll store the correlation between index and field name
    ale_indexes = {}

    cdls = []

    with open(input_file, 'r') as edl:
        lines = edl.readlines()
        for line in lines:
            if line.startswith('Column'):
                section['column'] = True
                continue
            elif line.startswith('Data'):
                section['data'] = True
                continue
            elif section['column']:
                for i, field in enumerate(line.split('\t')):
                    ale_indexes[field.strip()] = i
                section['column'] = False
            elif section['data']:
                cdl_data = line.split('\t')

                sat = cdl_data[ale_indexes['ASC_SAT']]
                sop = cdl_data[ale_indexes['ASC_SOP']]
                try:
                    cc_id = cdl_data[ale_indexes['Scan Filename']]
                except KeyError:
                    # Scan Filename is usually more descriptive, but we can
                    # fall back on the always present 'Name' field if
                    # Scan Filename is missing.
                    cc_id = cdl_data[ale_indexes['Name']]

                # Determine slope, offset and power from sop
                # sop should look like:
                # (1.4 1.9 1.7)(-0.1 -0.26 -0.20)(0.87 1.0 1.32)
                sop = sop.replace(' ', ', ')
                sop = sop.replace(')(', ')|(')
                sop = sop.split('|')
                sop_values = {
                    'slope': literal_eval(sop[0]),
                    'offset': literal_eval(sop[1]),
                    'power': literal_eval(sop[2])
                }

                cdl = correction.ColorCorrection(cc_id, input_file)

                cdl.sat = sat
                cdl.slope = sop_values['slope']
                cdl.offset = sop_values['offset']
                cdl.power = sop_values['power']

                cdls.append(cdl)

    ccc = collection.ColorCollection()
    ccc.file_in = input_file
    ccc.append_children(cdls)

    return ccc

# ==============================================================================


def parse_cc(input_file):  # pylint: disable=R0912
    """Parses a .cc file for ASC CDL information

    **Args:**
        input_file : (str|<ElementTree.Element>)
            The filepath to the CC or the ``ElementTree.Element`` object.

    **Returns:**
        (:class:`ColorCorrection`)
            The :class:`ColorCorrection` described within.

    **Raises:**
        ValueError:
            Bad XML formatting can raise ValueError is missing required
            elements.

    A CC file is really only a single element of a larger CDL or CCC XML file,
    but this element has become a popular way of passing around single shot
    CDLs, rather than the much bulkier CDL file.

    A sample CC XML file has text like:
    ::
        <ColorCorrection id="cc03340">
            <SOPNode>
                <Description>change +1 red, contrast boost</Description>
                <Slope>1.2 1.3 1.4</Slope>
                <Offset>0.3 0.0 0.0</Offset>
                <Power>1.0 1.0 1.0</Power>
            </SOPNode>
            <SatNode>
                <Saturation>1.2</Saturation>
            </SatNode>
        </ColorCorrection>

    Additional elements can include multiple descriptions at every level,
    a description of the input colorspace, and a description of the viewing
    colorspace and equipment.

    """
    if type(input_file) is str:
        root = _remove_xmlns(input_file)
        file_in = input_file
    else:
        root = input_file
        file_in = None

    if not root.tag == 'ColorCorrection':
        # This is not a CC file...
        raise ValueError('CC parsed but no ColorCorrection found')

    try:
        cc_id = root.attrib['id']
    except KeyError:
        raise ValueError('No id found on ColorCorrection')

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
                'The ColorCorrection element could not be parsed because the '
                'XML is missing required elements: {elems}'.format(
                    elems=str(names)
                )
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
        raise ValueError(
            'The ColorCorrection element requires either a Sop node or a Sat '
            'node, and it is missing both.'
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


def parse_ccc(input_file):
    """Parses a .ccc file into a :class:`ColorCollection` with type 'ccc'

    **Args:**
        input_file : (str)
            The filepath to the CCC.

    **Returns:**
        (:class:`ColorCollection`)
            A collection of all the found :class:`ColorCorrection` as well
            as any metadata within the XML

    **Raises:**
        ValueError:
            Bad XML formatting can raise ValueError is missing required
            elements.

    A ColorCorrectionCollection is just that- a collection of ColorCorrection
    elements. It does not contain any ColorDecision or MediaRef elements,
    but is free to contain as many Description elements as someone adds in.

    It should also contain an InputDescription element, describing the color
    space and other properties of the incoming image, as well as a
    ViewingDescription which describes the viewing environment as well
    as any relevant hardware devices used to view or grade.

    """
    root = _remove_xmlns(input_file)

    if root.tag != 'ColorCorrectionCollection':
        # This is not a CCC file...
        raise ValueError('CCC parsed but no ColorCorrectionCollection found')

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
        raise ValueError(
            'ColorCorrectionCollections require at least one ColorCorrection '
            'node, but no ColorCorrection nodes were found.'
        )

    return ccc

# ==============================================================================


def parse_cdl(input_file):
    """Parses a .cdl file into a :class:`ColorCollection` with type 'cdl'

    **Args:**
        input_file : (str)
            The filepath to the CDL.

    **Returns:**
        (:class:`ColorCollection`)
            A collection of all the found :class:`ColorDecisions` as well
            as any metadata within the XML

    **Raises:**
        ValueError:
            Bad XML formatting can raise ValueError is missing required
            elements.

    A ColorDecicionList is just that- a list of ColorDecision elements. It does
    not directly contain any ColorCorrections or Media Ref, only
    ColorDecisions, but is free to contain as many Description elements as
    someone adds in.

    It should also contain an InputDescription element, describing the color
    space and other properties of the incoming image, as well as a
    ViewingDescription which describes the viewing environment as well
    as any relevant hardware devices used to view or grade.

    """
    root = _remove_xmlns(input_file)

    if root.tag != 'ColorDecisionList':
        # This is not a CDL file...
        raise ValueError('CDL parsed but no ColorDecisionList found')

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
        raise ValueError(
            'ColorDecisionLists require at least one ColorDecision node, but '
            'no ColorDecision nodes were found.'
        )

    return cdl

# ==============================================================================


def parse_flex(input_file):  # pylint: disable=R0912,R0914
    """Parses a DaVinci FLEx telecine EDL for ASC CDL information.

    **Args:**
        input_file : (str)
            The filepath to the FLEx EDL

    **Returns:**
        (:class:`ColorCollection`)
            A collection that contains all the ColorCorrection objects found
            within this EDL

    **Raises:**
        N/A

    The DaVinci FLEx EDL is an odd duck, it's information conveyed via an
    extremely strict line & character addressing system.

    Each line must begin with a line number header that indicated what type
    of information the line contains, with line number 100 indicating the
    start of a new shot/take. Lines 000-099 contain session information.

    Within each line, important information is constricted to a certain
    range of characters, rather than space or comma separated like in an
    ALE EDL.

    Some line numbers we care about, and the character indexes:

    +--------+---------------+------------+---------------------------------+
    | Line # | Line Name     | Char Index | Data Type                       |
    +========+===============+============+=================================+
    | 010    | Project Title | 10-79      | Title                           |
    +--------+---------------+------------+---------------------------------+
    | 100    | Slate Info    | 10-17      | Scene                           |
    +--------+---------------+------------+---------------------------------+
    |        |               | 24-31      | Take ID                         |
    +--------+---------------+------------+---------------------------------+
    |        |               | 42-49      | Camera Reel ID                  |
    +--------+---------------+------------+---------------------------------+
    | 701    | ASC SOP       | (This entry can be safely space separated)   |
    +--------+---------------+------------+---------------------------------+
    | 702    | ASC SAT       | (This entry can be safely space separated)   |
    +--------+---------------+------------+---------------------------------+

    We'll try and default to using the Slate information to derive the
    resultant filename, however that information is optional. If no
    slate information is found, we'll iterate up at the end of the title.
    If no title information is found, we'll have to iterate up on the
    actual input filename, which is far from ideal.

    """

    cdls = []

    with open(input_file, 'r') as edl:
        lines = edl.readlines()

        filename = os.path.basename(input_file).split('.')[0]

        title = None
        # Metadata will store, in order, the various scene, take, reel fields
        # it finds.
        metadata = []

        sop = {}
        sat = None

        def build_cc(line_id, edl_path, sop_dict, sat_value, title_line):
            """Builds and returns a cc if sop/sat values found"""
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

        for line in lines:
            if line.startswith('100'):
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

            elif line.startswith('010'):
                # Title Line
                # 10-79 Title
                title = line[10:80].strip()
            elif line.startswith('110'):
                # Slate Information
                # 10-17 Scene
                # 24-31 Take ID
                # 42-49 Camera Reel ID
                metadata = [
                    line[10:18].strip(),  # Scene
                    line[24:32].strip(),  # Take
                    line[42:50].strip(),  # Reel
                ]
            elif line.startswith('701'):
                # ASC SOP
                # 701 ASC_SOP(# # #)(-# -# -#)(# # #)
                sop = {
                    'slope': line[12:32].split(),
                    'offset': line[34:57].split(),
                    'power': line[59:79].split()
                }
            elif line.startswith('702'):
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


def parse_rnh_cdl(input_file):
    """Parses a space separated .cdl file for ASC CDL information.

    **Args:**
        input_file : (str)
            The filepath to the CDL

    **Returns:**
        (:class:`ColorCorrection`)
            The single ColorCorrection object retrieved from the beta CDL

    **Raises:**
        N/A

    A space separated cdl file is an internal Rhythm & Hues format used by
    the Rhythm & Hues for displaying shot level and sequence level within
    their internally developed playback software.

    The file is a simple file consisting of one line. That line has 10, space
    separated elements that correspond to the ten ASC CDL elements in order of
    operations.

    ``SlopeR SlopeG SlopeB OffsetR OffsetG OffsetB PowerR PowerG PowerB Sat``

    """

    with open(input_file, 'r') as cdl_f:
        # We only need to read the first line
        line = cdl_f.readline()
        line = line.split()

        # The filename without extension will become the id
        filename = os.path.basename(input_file).split('.')[0]

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
# PRIVATE FUNCTIONS
# ==============================================================================


def _remove_xmlns(input_file):
    """Removes the xmlns attribute from XML files, then returns the element"""
    # We're going to open the file as a string and remove the xmlns, as
    # it doesn't do a lot for us when working with CDLs, and in fact
    # just clutters everything the hell up.
    with open(input_file, 'r') as xml_file:
        xml_string = xml_file.read()

    xml_string = re.sub(' xmlns="[^"]+"', '', xml_string, count=1)

    return ElementTree.fromstring(xml_string)

# ==============================================================================
# GLOBALS
# ==============================================================================

INPUT_FORMATS = {
    'ale': parse_ale,
    'ccc': parse_ccc,
    'cc': parse_cc,
    'cdl': parse_cdl,
    'flex': parse_flex,
    'rcdl': parse_rnh_cdl,
}

# ==============================================================================
# PARSE FILE
# ==============================================================================


def parse_file(filepath, filetype=None):
    """Determines & uses the correct parser to use on a CDL file

    Args:
        filepath : (str)
            The filepath to the file. Must exist.

        filetype=None : (str)
            A file extension corresponding to the CDL type to convert from.
            If not provided, we'll derive it from the filepath.

            Should not include a '.'

    Raises:
        N/A

    Returns:
        :class:`ColorCorrection` or :class:`ColorCollection`
            Depending on the type of input file, this function will
            either return a single :class:`ColorCorrection` or a full
            :class:`ColorCollection` , containing one or more
            :class:`ColorCorrection` or :class:`ColorDecision`

    """
    if not filetype:
        filetype = os.path.basename(filepath).split('.')[-1].lower()

    return INPUT_FORMATS[filetype](filepath)
