#!/usr/bin/env python
"""

CDL Convert
==========

Converts between common ASC CDL (http://en.wikipedia.org/wiki/AscCdl)
formats. The American Society of Cinematographers Color Decision List (ASC CDL,
or CDL for short) is a schema to simplify the process of interchanging color
data between various programs and facilities.

The ASC has defined schemas for including the 10 basic numbers in 5 different
formats:

* Avid Log Exchange (ALE)
* Film Log EDL Exchange (FLEx)
* CMX EDL
* XML Color Correction (cc)
* XML Color Correction Collection (ccc)

Unofficial Formats:

* OCIOCDLTransform, a Foundry Nuke node
* Space Separated CDL, a Rhythm and Hues cdl format

It is the purpose of CDLConvert to convert ASC CDL information between these
basic formats to further facilitate the ease of exchange of color data within
the Film and TV industries.

**CDLConvert is not associated with the American Society of Cinematographers**

## License

The MIT License (MIT)

Copyright (c) 2014 Sean Wallitsch

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

Classes
-------

AscCdl
    The base class for the ASC CDL, containing attributes for all ten of the
    color conversion numbers needed to fully describe an ASC CDL.

Functions
---------

"""

# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import print_function

from argparse import ArgumentParser
from ast import literal_eval
import os
import sys
import xml.etree.ElementTree as ElementTree

# Python 3 compatibility
try:
    xrange
except NameError:  # pragma: no cover
    xrange = range  # pylint: disable=W0622, C0103
try:
    raw_input
except NameError:  # pragma: no cover
    raw_input = input  # pylint: disable=W0622, C0103

# ==============================================================================
# GLOBALS
# ==============================================================================

__author__ = "Sean Wallitsch"
__copyright__ = "Copyright 2014, Sean Wallitsch"
__credits__ = ["Sean Wallitsch", ]
__license__ = "MIT"
__version__ = "0.5.post2"
__maintainer__ = "Sean Wallitsch"
__email__ = "shidarin@alphamatte.com"
__status__ = "Development"

# INPUT_FORMATS and OUTPUT_FORMATS are globals but located in the MAIN section
# of the file, as they are dispatcher dictionaries that require the functions
# to be parsed by python before the dictionary can be built.

# Because it's getting late and I'm too tired to dive into writing XML today
CC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="{id}">
    <SOPNode>
        <Description></Description>
        <Slope>{slopeR} {slopeG} {slopeB}</Slope>
        <Offset>{offsetR} {offsetG} {offsetB}</Offset>
        <Power>{powerR} {powerG} {powerB}</Power>
    </SOPNode>
    <SatNode>
        <Saturation>{sat}</Saturation>
    </SatNode>
</ColorCorrection>
"""

if sys.version_info[0] >= 3:  # pragma: no cover
    enc = lambda x: bytes(x, 'UTF-8')  # pylint: disable=C0103
else:  # pragma: no cover
    enc = lambda x: x  # pylint: disable=C0103

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'AscCdl',
    'ColorNodeBase',
    'SatNode',
    'SopNode',
    'parse_ale',
    'parse_cc',
    'parse_cdl',
    'parse_flex',
    'write_cc',
    'write_cdl',
]

# ==============================================================================
# CLASSES
# ==============================================================================


class AscCdl(object):  # pylint: disable=R0902
    """The basic class for the ASC CDL

    Description
    ~~~~~~~~~~~

    This class contains attributes for all 10 color correction numbers needed
    for an ASC CDL, as well as other metadata like shot names that typically
    accompanies a CDL.

    These names are standardized by the ASC and where possible the attribute
    names will follow the ASC schema. Descriptions for some of these attributes
    are paraphrasing the ASC CDL documentation. For more information on the ASC
    CDL standard and the operations described below, you can obtain the ASC CDL
    implementor-oriented documentation by sending an email to:
    asc-cdl at theasc dot com

    Order of operations is Slope, Offset, Power, then Saturation.

    **Class Attributes:**

        members : {str}
            All instanced :class:`AscCdl` are added to this member dictionary,
            with their unique id being the key and the :class:`AscCdl` being
            the value.

    **Attributes:**

        file_in : (str)
            Filepath used to create this CDL.

        file_out : (str)
            Filepath this CDL will be written to.

        cc_id : (str)
            Unique XML URI to identify this CDL. Often a shot or sequence name.

            Changing this value does a check against the cls.members dictionary
            to ensure the new id is open. If it is, the key is changed to the
            new id and the id is changed.

        metadata : {str}
            metadata is a dictionary of the various descriptions that a CDL
            might have. Included are the 5 default:

                cc_ref:
                    This is a reference to another CDL's unique id.

                desc: [(str)]
                    Comments and notes on the correction.

                input_desc:
                    Description of the color space, format and
                    properties of the input images.

                media_ref:
                    A reference link to an image or an image sequence.

                viewing_desc:
                    Viewing device, settings and environment.

        sat_node : ( :class:`SatNode` )
            Contains a reference to a single instance of :class:`SatNode` ,
            which contains the saturation value and descriptions.

        sop_node : ( :class:`SopNode` )
            Contains a reference to a single instance of :class:`SopNode` ,
            which contains the slope, offset, power values and descriptions.

    """

    members = {}

    def __init__(self, cc_id, cdl_file):
        """Inits an instance of an ASC CDL"""

        # Non-ASC attributes
        self._files = {
            'file_in': os.path.abspath(cdl_file),
            'file_out': None
        }

        # The cc_id is really the only required part of an ASC CDL.
        # Each ID should be unique
        cc_id = _sanitize(cc_id)
        if cc_id in AscCdl.members.keys():
            raise ValueError(
                'Error initiating cc_id to "{cc_id}". This id is already a'
                'registered id.'.format(
                    cc_id=cc_id
                )
            )
        self._cc_id = cc_id

        # Register with member dictionary
        AscCdl.members[self._cc_id] = self

        # ASC_SAT attribute
        self.sat_node = None

        # ASC_SOP attributes
        self.sop_node = None

        # Metadata
        self.metadata = {
            'cc_ref': None,
            'desc': [],
            'input_desc': None,
            'media_ref': None,
            'viewing_desc': None
        }

    # Properties ==============================================================

    @property
    def file_in(self):
        """Returns the absolute filepath to the input file"""
        return self._files['file_in']

    @property
    def file_out(self):
        """Returns a theoretical absolute filepath based on output ext"""
        return self._files['file_out']

    @property
    def cc_id(self):
        """Returns unique color correction id field"""
        return self._cc_id

    @cc_id.setter
    def cc_id(self, value):
        self._set_id(value)

    @property
    def offset(self):
        """Returns list of RGB offset values"""
        if not self.sop_node:
            self.sop_node = SopNode(self)
        return self.sop_node.offset

    @offset.setter
    def offset(self, offset_rgb):
        """Runs tests and converts offset rgb values before setting"""
        if not self.sop_node:
            self.sop_node = SopNode(self)
        self.sop_node.offset = offset_rgb

    @property
    def power(self):
        """Returns list of RGB power values"""
        if not self.sop_node:
            self.sop_node = SopNode(self)
        return self.sop_node.power

    @power.setter
    def power(self, power_rgb):
        """Runs tests and converts power rgb values before setting"""
        if not self.sop_node:
            self.sop_node = SopNode(self)
        self.sop_node.power = power_rgb

    @property
    def slope(self):
        """Returns list of RGB slope values"""
        if not self.sop_node:
            self.sop_node = SopNode(self)
        return self.sop_node.slope

    @slope.setter
    def slope(self, slope_rgb):
        """Runs tests and converts slope rgb values before setting"""
        if not self.sop_node:
            self.sop_node = SopNode(self)
        self.sop_node.slope = slope_rgb

    @property
    def sat(self):
        """Returns float value for saturation"""
        if not self.sat_node:
            self.sat_node = SatNode(self)
        return self.sat_node.sat

    @sat.setter
    def sat(self, sat_value):
        """Makes sure provided sat value is a positive float"""
        if not self.sat_node:
            self.sat_node = SatNode(self)
        self.sat_node.sat = sat_value

    # private methods =========================================================

    def _set_id(self, new_id):
        """Changes the id field if the new id is unique"""
        cc_id = _sanitize(new_id)
        # Check if this id is already registered
        if cc_id in AscCdl.members.keys():
            raise ValueError(
                'Error setting the cc_id to "{cc_id}". This id is already a '
                'registered id.'.format(
                    cc_id=cc_id
                )
            )
        else:
            # Clear the current id from the dictionary
            AscCdl.members.pop(self._cc_id)
            self._cc_id = cc_id
            # Register the new id with the dictionary
            AscCdl.members[self._cc_id] = self

    # methods =================================================================

    def determine_dest(self, output):
        """Determines the destination file and sets it on the cdl"""

        directory = os.path.dirname(self.file_in)

        filename = "{id}.{ext}".format(id=self.cc_id, ext=output)

        self._files['file_out'] = os.path.join(directory, filename)

# ==============================================================================


class ColorNodeBase(object):  # pylint: disable=R0903
    """Base class for SOP and SAT nodes

    **Attributes:**

        desc : [str]
            Since both SAT and SOP nodes can contain an infinite number of
            descriptions, the desc attribute is a list, allowing us to store
            every single description found during parsing.

            Setting desc directly will cause the value given to append to the
            end of the list, but desc can also be extended by passing it a list
            or tuple.

    """
    def __init__(self):
        self._desc = []

    @property
    def desc(self):
        """Returns the list of descriptions"""
        return tuple(self._desc)

    @desc.setter
    def desc(self, value):
        """Adds an entry to the descriptions"""
        if type(value) in [list, tuple]:
            self._desc.extend(value)
        else:
            self._desc.append(value)

# ==============================================================================


class SatNode(ColorNodeBase):
    """Color node that contains saturation data.

    **Class Attributes:**

        element_names : [str]
            Contains a list of XML Elements that refer to this class for use
            in parsing XML files.

    **Attributes:**

        parent : ( :class:`AscCdl` )
            The parent :class:`AscCdl` instance that created this instance.

        sat : (float)
            The saturation value (to be applied with Rec 709 coefficients) is
            stored here. Saturation is the last operation to be applied when
            applying a CDL.

            sat can be set with a float, int or numeric string.

    """

    # XML Fields for SopNodes can be one of these names:
    element_names = ['ASC_SAT', 'SATNode']

    def __init__(self, parent):
        super(SatNode, self).__init__()

        self._parent = parent
        self._sat = 1.0

    @property
    def parent(self):
        """Returns which :class:`AscCdl` created this SatNode"""
        return self._parent

    @property
    def sat(self):
        """Returns the protected sat attribute"""
        return self._sat

    @sat.setter
    def sat(self, value):
        """Runs checks and converts saturation value before setting"""
        # If given as a string, the string must be convertible to a float
        if type(value) == str:
            try:
                value = float(value)
            except ValueError:
                raise TypeError(
                    'Error setting saturation with value: "{value}". '
                    'Value is not a number.'.format(
                        value=value
                    )
                )
        # Number must be positive
        if type(value) in [float, int]:
            if value < 0:
                raise ValueError(
                    'Error setting saturation with value: "{value}". '
                    'Values must not be negative'.format(
                        value=value
                    )
                )
            else:
                self._sat = float(value)
        else:
            raise TypeError(
                'Saturation cannot be set directly with objects of type: '
                '"{type}". Value given: "{value}".'.format(
                    type=type(value),
                    value=value,
                )
            )

# ==============================================================================


class SopNode(ColorNodeBase):
    """Color node that contains slope, offset and power data.

    slope, offset and saturation are stored internally as lists, but always
    returned as tuples to prevent index assignment from being successful. This
    protects the user from inadvertently setting a single value in the list
    to be a non-valid value, which might result in values not being floats or
    even numbers at all.

    **Class Attributes:**

        element_names : [str]
            Contains a list of XML Elements that refer to this class for use
            in parsing XML files.

    **Attributes:**

        parent : ( :class:`AscCdl` )
            The parent :class:`AscCdl` instance that created this instance.

        slope : (float, float, float)
            An rgb tuple representing the slope, which changes the slope of the
            input without shifting the black level established by the offset.
            These values must be positive. If you set this attribute with a
            single value, it will be copied over all 3 colors. Any single value
            given can be a float, int or numeric string.

            default: (1.0, 1.0, 1.0)

        offset : (float, float, float)
            An rgb tuple representing the offset, which raises or lowers the
            input brightness while holding the slope constant. If you set this
            attribute with a single value, it will be copied over all 3 colors.
            Any single value given can be a float, int or numeric string.

            default: (0.0, 0.0, 0.0)

        power : (float, float, float)
            An rgb tuple representing the power, which is the only function that
            changes the response curve of the function. Note that this has the
            opposite response to adjustments than a traditional gamma operator.
            These values must be positive. If you set this attribute with a
            single value, it will be copied over all 3 colors. Any single value
            given can be a float, int or numeric string.


            default: (1.0, 1.0, 1.0)

    """

    # XML Fields for SopNodes can be one of these names:
    element_names = ['ASC_SOP', 'SOPNode']

    def __init__(self, parent):
        super(SopNode, self).__init__()

        self._parent = parent

        self._slope = [1.0, 1.0, 1.0]
        self._offset = [0.0, 0.0, 0.0]
        self._power = [1.0, 1.0, 1.0]

    @property
    def parent(self):
        """Returns which :class:`AscCdl` created this SopNode"""
        return self._parent

    @property
    def slope(self):
        """Returns the slope as an tuple"""
        return tuple(self._slope)

    @slope.setter
    def slope(self, value):
        """Runs tests and converts slope rgb values before setting"""
        # If given as a string, the string must be convertible to a float.
        if type(value) == str:
            try:
                value = float(value)
            except ValueError:
                raise TypeError(
                    'Error setting slope with value: "{value}". '
                    'Value is not a number.'.format(
                        value=value
                    )
                )
        # If given as a single number, that number must be positive
        if type(value) in [float, int]:
            if value < 0:
                raise ValueError(
                    'Error setting slope with value: "{value}". '
                    'Values must not be negative'.format(
                        value=value
                    )
                )
            else:
                self._slope = [float(value)] * 3
        # If given as a list or tuple, each value must be convertible to a
        # float, and the list or tuple must have 3 values inside of it.
        # Those values must be positive
        elif type(value) in [list, tuple]:
            try:
                assert len(value) == 3
            except AssertionError:
                raise ValueError(
                    'Error setting slope with value: "{value}". '
                    'Slope values given as a list or tuple must have 3 '
                    'elements, one for each color.'.format(
                        value=value
                    )
                )

            value = list(value)

            for i in xrange(len(value)):
                try:
                    value[i] = float(value[i])
                except ValueError:
                    raise TypeError(
                        'Error setting slope with value: "{value}". '
                        'Value is not a number.'.format(
                            value=value[i]
                        )
                    )
                try:
                    assert value[i] >= 0.0
                except AssertionError:
                    raise ValueError(
                        'Error setting slope with value: "{value}". '
                        'Values must not be negative'.format(
                            value=value[i]
                        )
                    )

            self._slope = value
        else:
            raise TypeError(
                'Slope cannot be set directly with objects of type: "{type}". '
                'Value given: "{value}".'.format(
                    type=type(value),
                    value=value,
                )
            )

    @property
    def offset(self):
        """Returns the offset as a tuple"""
        return tuple(self._offset)

    @offset.setter
    def offset(self, value):
        """Runs tests and converts offset rgb values before setting"""
        # If given as a string, the string must be convertible to a float.
        if type(value) == str:
            try:
                value = float(value)
            except ValueError:
                raise TypeError(
                    'Error setting offset with value: "{value}". '
                    'Value is not a number.'.format(
                        value=value
                    )
                )
        # If given as a single number, repeat 3 times for a list.
        if type(value) in [float, int]:
            self._offset = [float(value)] * 3
        # If given as a list or tuple, each value must be convertible to a
        # float, and the list or tuple must have 3 values inside of it.
        # Those values must be positive
        elif type(value) in [list, tuple]:
            try:
                assert len(value) == 3
            except AssertionError:
                raise ValueError(
                    'Error setting offset with value: "{value}". '
                    'Offset values given as a list or tuple must have 3 '
                    'elements, one for each color.'.format(
                        value=value
                    )
                )

            value = list(value)

            for i in xrange(len(value)):
                try:
                    value[i] = float(value[i])
                except ValueError:
                    raise TypeError(
                        'Error setting offset with value: "{value}". '
                        'Value is not a number.'.format(
                            value=value[i]
                        )
                    )

            self._offset = value
        else:
            raise TypeError(
                'Offset cannot be set directly with objects of type: "{type}". '
                'Value given: "{value}".'.format(
                    type=type(value),
                    value=value,
                )
            )

    @property
    def power(self):
        """Returns the power as a tuple"""
        return tuple(self._power)

    @power.setter
    def power(self, value):
        """Runs tests and converts power rgb values before setting"""
        # If given as a string, the string must be convertible to a float
        if type(value) == str:
            try:
                value = float(value)
            except ValueError:
                raise TypeError(
                    'Error setting power with value: "{value}". '
                    'Value is not a number.'.format(
                        value=value
                    )
                )
        # If given as a single number, that number must be positive
        if type(value) in [float, int]:
            if value < 0:
                raise ValueError(
                    'Error setting power with value: "{value}". '
                    'Values must not be negative'.format(
                        value=value
                    )
                )
            else:
                self._power = [float(value)] * 3
        # If given as a list or tuple, each value must be convertible to a
        # float, and the list or tuple must have 3 values inside of it.
        # Those values must be positive
        elif type(value) in [list, tuple]:
            try:
                assert len(value) == 3
            except AssertionError:
                raise ValueError(
                    'Error setting power with value: "{value}". '
                    'Power values given as a list or tuple must have 3 '
                    'elements, one for each color.'.format(
                        value=value
                    )
                )

            value = list(value)

            for i in xrange(len(value)):
                try:
                    value[i] = float(value[i])
                except ValueError:
                    raise TypeError(
                        'Error setting power with value: "{value}". '
                        'Value is not a number.'.format(
                            value=value[i]
                        )
                    )
                try:
                    assert value[i] >= 0.0
                except AssertionError:
                    raise ValueError(
                        'Error setting power with value: "{value}". '
                        'Values must not be negative'.format(
                            value=value[i]
                        )
                    )

            self._power = value
        else:
            raise TypeError(
                'Power cannot be set directly with objects of type: "{type}". '
                'Value given: "{value}".'.format(
                    type=type(value),
                    value=value,
                )
            )

# ==============================================================================
# PRIVATE FUNCTIONS
# ==============================================================================


def _sanitize(name):
    """Removes any characters in string name that aren't alnum or in '_.'"""
    import re
    # Replace any spaces with underscores
    name = name.replace(' ', '_')
    # If we start our string with an underscore or period, remove it
    if name[0] in '_.':
        name = name[1:]
    # a-z is all lowercase
    # A-Z is all uppercase
    # 0-9 is all digits
    # \. is an escaped period
    # _ is an underscore
    # Put them together, negate them by leading with an ^
    # and our compiler will mark every non alnum, non ., _ character
    pattern = re.compile(r'[^a-zA-Z0-9\._]+')
    # Then we sub them with nothing
    fixed = pattern.sub('', name)

    return fixed

# ==============================================================================
# FUNCTIONS
# ==============================================================================


def parse_ale(edl_file):
    """Parses an Avid Log Exchange (ALE) file for CDLs

    **Args:**
        file : (str)
            The filepath to the ALE EDL

    **Returns:**
        [:class:`AscCdl`]
            A list of CDL objects retrieved from the ALE

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

    with open(edl_file, 'r') as edl:
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
                    ale_indexes[field] = i
                section['column'] = False
            elif section['data']:
                cdl_data = line.split('\t')

                sat = cdl_data[ale_indexes['ASC_SAT']]
                sop = cdl_data[ale_indexes['ASC_SOP']]
                cc_id = cdl_data[ale_indexes['Scan Filename']]

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

                cdl = AscCdl(cc_id, edl_file)

                cdl.sat = sat
                cdl.slope = sop_values['slope']
                cdl.offset = sop_values['offset']
                cdl.power = sop_values['power']

                cdls.append(cdl)

    return cdls

# ==============================================================================


def parse_cc(cdl_file):
    """Parses a .cc file for ASC CDL information

    **Args:**
        file : (str)
            The filepath to the CC

    **Returns:**
        [:class:`AscCdl`]
            A list of CDL objects retrieved from the CC

    **Raises:**
        N/A

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

    We'll check to see if each of these elements exist, and override the AscCdl
    defaults if we find them.

    """
    root = ElementTree.parse(cdl_file).getroot()

    cdls = []

    if not root.tag == 'ColorCorrection':
        # This is not a CC file...
        raise ValueError('CC parsed but no ColorCorrection found')

    try:
        cc_id = root.attrib['id']
    except KeyError:
        raise ValueError('No id found on ColorCorrection')

    cdl = AscCdl(cc_id, cdl_file)
    # Neither the SOP nor the Sat node actually HAVE to exist, it literally
    # could just be an id and that's it.
    sop = root.find('SOPNode')
    sat = root.find('SatNode')

    # We make a specific comparison against None, because etree creates errors
    # otherwise (future behavior is changing)
    if sop is not None:
        desc = sop.find('Description')
        slope = sop.find('Slope')
        offset = sop.find('Offset')
        power = sop.find('Power')

        if desc is not None:
            cdl.metadata['desc'] = desc.text
        if slope is not None:
            cdl.slope = slope.text.split()
        if offset is not None:
            cdl.offset = offset.text.split()
        if power is not None:
            cdl.power = power.text.split()
    if sat is not None:
        sat_value = sat.find('Saturation')

        if sat_value is not None:
            cdl.sat = sat_value.text

    cdls.append(cdl)

    return cdls

# ==============================================================================


def parse_cdl(cdl_file):
    """Parses a space separated .cdl file for ASC CDL information.

    **Args:**
        file : (str)
            The filepath to the CDL

    **Returns:**
        [:class:`AscCdl`]
            A list with only the single CDL object retrieved from the SS CDL

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
    # Although we only parse one cdl file, we still want to return a list
    cdls = []

    with open(cdl_file, 'r') as cdl_f:
        # We only need to read the first line
        line = cdl_f.readline()
        line = line.split()

        # The filename without extension will become the id
        filename = os.path.basename(cdl_file).split('.')[0]

        slope = [line[0], line[1], line[2]]
        offset = [line[3], line[4], line[5]]
        power = [line[6], line[7], line[8]]

        sat = line[9]

        cdl = AscCdl(filename, cdl_file)

        cdl.slope = slope
        cdl.offset = offset
        cdl.power = power
        cdl.sat = sat

        cdls.append(cdl)

    return cdls

# ==============================================================================


def parse_flex(edl_file):
    """Parses a DaVinci FLEx telecine EDL for ASC CDL information.

    **Args:**
        file : (str)
            The filepath to the FLEx EDL

    **Returns:**
        [:class:`AscCdl`]
            A list of CDL objects retrieved from the FLEx

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

    with open(edl_file, 'r') as edl:
        lines = edl.readlines()

        filename = os.path.basename(edl_file).split('.')[0]

        title = None
        # Metadata will store, in order, the various scene, take, reel fields
        # it finds.
        metadata = []

        sop = {}
        sat = None

        def build_cdl(line_id, edl_path, sop_dict, sat_value, title_line):
            """Builds and returns a cdl if sop/sat values found"""
            cdl = AscCdl(line_id, edl_path)
            if title_line:
                cdl.metadata['desc'] = title_line
            if sop_dict:
                # If it finds the 701 line, it will have all three
                cdl.slope = sop_dict['slope']
                cdl.offset = sop_dict['offset']
                cdl.power = sop_dict['power']
            if sat_value:
                cdl.sat = sat_value

            return cdl

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
                    cdl = build_cdl(cc_id, edl_file, sop, sat, title)
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
                sat = float(line.split()[-1])

    # We need to dump the last record to the cdl list
    metadata = [i for i in metadata if i != '']
    if metadata:
        cc_id = '_'.join(metadata)
    else:
        field = title if title else filename
        cc_id = field + str(len(cdls) + 1).rjust(3, '0')

    # If we found values at all:
    if sop or sat:
        cdl = build_cdl(cc_id, edl_file, sop, sat, title)
        cdls.append(cdl)

    return cdls

# ==============================================================================


def write_cc(cdl):
    """Writes the AscCdl to a .cc file"""

    xml = CC_XML.format(
        id=cdl.cc_id,
        slopeR=cdl.slope[0],
        slopeG=cdl.slope[1],
        slopeB=cdl.slope[2],
        offsetR=cdl.offset[0],
        offsetG=cdl.offset[1],
        offsetB=cdl.offset[2],
        powerR=cdl.power[0],
        powerG=cdl.power[1],
        powerB=cdl.power[2],
        sat=cdl.sat
    )

    with open(cdl.file_out, 'wb') as cdl_f:
        cdl_f.write(enc(xml))

# ==============================================================================


def write_cdl(cdl):
    """Writes the AscCdl to a space separated .cdl file"""

    values = list(cdl.slope)
    values.extend(cdl.offset)
    values.extend(cdl.power)
    values.append(cdl.sat)
    values = [str(i) for i in values]

    ss_cdl = ' '.join(values)

    with open(cdl.file_out, 'wb') as cdl_f:
        cdl_f.write(enc(ss_cdl))

# ==============================================================================
# MAIN
# ==============================================================================

# These globals need to be after the parse/write functions but before the
# parse_args.

INPUT_FORMATS = {
    'ale': parse_ale,
    'cc': parse_cc,
    'cdl': parse_cdl,
    'flex': parse_flex,
}

OUTPUT_FORMATS = {
    'cc': write_cc,
    'cdl': write_cdl,
}

# ==============================================================================


def parse_args():
    """Uses argparse to parse command line arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "input_file",
        help="the file to be converted"
    )
    parser.add_argument(
        "-i",
        "--input",
        help="specify the filetype to convert from. Use when CDLConvert "
             "cannot determine the filetype automatically. Supported input "
             "formats are: "
             "{inputs}".format(inputs=str(INPUT_FORMATS.keys()))
    )
    parser.add_argument(
        "-o",
        "--output",
        help="specify the filetype to convert to, comma separated lists are "
             "accepted. Defaults to a .cc XML. Supported output formats are: "
             "{outputs}".format(outputs=str(OUTPUT_FORMATS.keys()))
    )

    args = parser.parse_args()

    if args.input:
        if args.input.lower() not in INPUT_FORMATS:
            raise ValueError(
                "The input format: {input} is not supported".format(
                    input=args.input
                )
            )
        else:
            args.input = args.input.lower()

    if args.output:
        # This might be a string separated list of output types.
        # We'll split it, check each against the supported types, convert
        # them to lowercase if not already, and place the resulting list back
        # into args.output
        #
        # TODO: Define and add a new argparse type as described in:
        # http://stackoverflow.com/questions/9978880/python-argument-parser-list-of-list-or-tuple-of-tuples
        output_types = args.output.split(',')
        for i in xrange(len(output_types)):
            if output_types[i].lower() not in OUTPUT_FORMATS.keys():
                raise ValueError(
                    "The output format: {output} is not supported".format(
                        output=output_types[i]
                    )
                )
            else:
                output_types[i] = output_types[i].lower()
        args.output = output_types
    else:
        args.output = ['cc', ]

    return args

# ==============================================================================


def main():
    """Will figure out input and destination filetypes, then convert"""
    args = parse_args()

    filepath = os.path.abspath(args.input_file)

    if not args.input:
        filetype_in = os.path.basename(filepath).split('.')[-1].lower()
    else:
        filetype_in = args.input

    cdls = INPUT_FORMATS[filetype_in](filepath)

    if cdls:
        for cdl in cdls:
            for ext in args.output:
                cdl.determine_dest(ext)
                print(
                    "Writing cdl {id} to {path}".format(
                        id=cdl.cc_id,
                        path=cdl.file_out
                    )
                )
                OUTPUT_FORMATS[ext](cdl)

if __name__ == '__main__':  # pragma: no cover
    try:
        main()
    except Exception as err:  # pylint: disable=W0703
        print('Unexpected error encountered:')
        print(err)
        raw_input('Press enter key to exit')
