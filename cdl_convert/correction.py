#!/usr/bin/env python
"""

CDL Convert Correction
======================

Contains the ColorCorrection class, and the ColorNode child classes, SopNode
and SatNode.

## Classes

    ColorCorrection

        The backbone of cdl_convert, everything comes down to the
        ColorCorrection, which is the main interface for interacting with the
        10 ASC CDL numbers. Contains a SatNode and a SopNode.

    SatNode

        Container node with the Sat value, including all the setter behavior.

    SopNode

        Container node for the Slope, Offset and Power values, including all
        the setter behavior.

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

from decimal import Decimal
import os
import re
from xml.etree import ElementTree

# cdl_convert imports

from .base import AscColorSpaceBase, AscDescBase, AscXMLBase, ColorNodeBase
from . import config

# Python 3 compatibility

try:
    xrange
except NameError:  # pragma: no cover
    xrange = range  # pylint: disable=W0622, C0103

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'ColorCorrection',
    'SatNode',
    'SopNode',
]

# ==============================================================================
# CLASSES
# ==============================================================================


class ColorCorrection(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0902,R0904
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

        members : {str: :class`ColorCorrection` }
            All instanced :class:`ColorCorrection` are added to this member
            dictionary, with their unique id being the key and the
            :class:`ColorCorrection` being the value.

    **Attributes:**

        desc : [str]
            Since all Asc nodes which can contain a single description, can
            actually contain an infinite number of descriptions, the desc
            attribute is a list, allowing us to store every single description
            found during parsing.

            Setting desc directly will cause the value given to append to the
            end of the list, but desc can also be replaced by passing it a list
            or tuple. Desc can be emptied by passing it None, [] or ().

            Inherited from :class:`AscDescBase` .

        element : (<xml.etree.ElementTree.Element>)
            etree style Element representing the node. Inherited from
            :class:`AscXMLBase` .

        file_in : (str)
            Filepath used to create this :class:`ColorCorrection` .

        file_out : (str)
            Filepath this :class:`ColorCorrection` will be written to.

        has_sat : (bool)
            Returns True if SOP values are set

        has_sop : (bool)
            Returns True if SOP values are set

        id : (str)
            Unique XML URI to identify this CDL. Often a shot or sequence name.

            Changing this value does a check against the cls.members dictionary
            to ensure the new id is open. If it is, the key is changed to the
            new id and the id is changed.

            Note that this shadows the builtin id.

        input_desc : (str)
            Description of the color space, format and properties of the input
            images. Inherited from :class:`AscColorSpaceBase` .

        parent : (:class:`ColorCollection`)
            The parent node that contains this node.

        sat_node : ( :class:`SatNode` )
            Contains a reference to a single instance of :class:`SatNode` ,
            which contains the saturation value and descriptions.

        sop_node : ( :class:`SopNode` )
            Contains a reference to a single instance of :class:`SopNode` ,
            which contains the slope, offset, power values and descriptions.

        viewing_desc : (str)
            Viewing device, settings and environment. Inherited from
            :class:`AscColorSpaceBase` .

        xml : (str)
            A nicely formatted XML string representing the node. Inherited from
            :class:`AscXMLBase`.

        xml_root : (str)
            A nicely formatted XML, ready to write to file string representing
            the node. Formatted as an XML root, it includes the xml version and
            encoding tags on the first line. Inherited from
            :class:`AscXMLBase`.

    **Public Methods:**

        build_element()
            Builds an ElementTree XML Element for this node and all nodes it
            contains. ``element``, ``xml``, and ``xml_root`` attributes use
            this to build the XML. This function is identical to calling the
            ``element`` attribute. Overrides inherited placeholder method
            from :class:`AscXMLBase` .

        determine_dest()
            When provided an output extension, determines the destination
            filename to be written to based on ``file_in`` & ``id``.

        parse_xml_descs()
            Parses an ElementTree Element for any Description tags and appends
            any text they contain to the ``desc``. Inherited from
            :class:`AscDescBase`

        parse_xml_input_desc()
            Parses an ElementTree Element to find & add an InputDescription.
            If none is found, ``input_desc`` will remain set to ``None``.
            Inherited from :class:`AscColorSpaceBase`

        parse_xml_viewing_desc()
            Parses an ElementTree Element to find & add a ViewingDescription.
            If none is found, ``viewing_desc`` will remain set to ``None``.
            Inherited from :class:`AscColorSpaceBase`

        reset_members()
            Resets the class level members list.

    """

    members = {}

    def __init__(self, id, input_file=None):  # pylint: disable=W0622
        """Inits an instance of a ColorCorrection"""
        super(ColorCorrection, self).__init__()

        # File Attributes
        self._file_in = os.path.abspath(input_file) if input_file else None
        self._file_out = None

        # If we're under a ColorCorrectionCollection or ColorDecision node:
        self.parent = None

        # The id is really the only required part of a ColorCorrection node
        # Each ID should be unique
        id = _sanitize(id)
        if id in ColorCorrection.members.keys():
            if config.HALT_ON_ERROR:
                raise ValueError(
                    'Error initiating id to "{id}". This id is already a '
                    'registered id.'.format(
                        id=id
                    )
                )
            else:
                id = '{id}{num:0>3}'.format(
                    id=id,
                    num=len(
                        [cc for cc in ColorCorrection.members
                         if cc.startswith(id)]
                    )
                )
        elif not id:
            if config.HALT_ON_ERROR:
                raise ValueError('Blank id given to ColorCorrection.')
            else:
                id = str(len(ColorCorrection.members) + 1).rjust(3, '0')
        self._id = id

        # Register with member dictionary
        ColorCorrection.members[self._id] = self

        # ASC_SAT attribute
        self._sat_node = None

        # ASC_SOP attributes
        self._sop_node = None

    # Properties ==============================================================

    @property
    def file_in(self):
        """Returns the absolute filepath to the input file"""
        return self._file_in

    @file_in.setter
    def file_in(self, value):
        """Sets the file_in to the absolute path of file"""
        if value:
            self._file_in = os.path.abspath(value)

    @property
    def file_out(self):
        """Returns a theoretical absolute filepath based on output ext"""
        return self._file_out

    @property
    def has_sat(self):
        """Returns True if SOP values are set"""
        if self._sat_node:
            return True
        else:
            return False

    @property
    def has_sop(self):
        """Returns True if SOP values are set"""
        if self._sop_node:
            return True
        else:
            return False

    @property
    def id(self):  # pylint: disable=C0103
        """Returns unique color correction id field"""
        return self._id

    @id.setter
    def id(self, value):  # pylint: disable=C0103
        """Before setting make sure new id is unique"""
        self._set_id(value)

    @property
    def offset(self):
        """Returns list of RGB offset values"""
        return self.sop_node.offset

    @offset.setter
    def offset(self, offset_rgb):
        """Runs tests and converts offset rgb values before setting"""
        self.sop_node.offset = offset_rgb

    @property
    def power(self):
        """Returns list of RGB power values"""
        return self.sop_node.power

    @power.setter
    def power(self, power_rgb):
        """Runs tests and converts power rgb values before setting"""
        self.sop_node.power = power_rgb

    @property
    def sat_node(self):
        """Initializes a SatNode if one doesn't already exist"""
        if not self._sat_node:
            self._sat_node = SatNode(self)
        return self._sat_node

    @property
    def slope(self):
        """Returns list of RGB slope values"""
        return self.sop_node.slope

    @slope.setter
    def slope(self, slope_rgb):
        """Runs tests and converts slope rgb values before setting"""
        self.sop_node.slope = slope_rgb

    @property
    def sop_node(self):
        """Initializes a SopNode if one doesn't already exist"""
        if not self._sop_node:
            self._sop_node = SopNode(self)
        return self._sop_node

    @property
    def sat(self):
        """Returns value for saturation"""
        return self.sat_node.sat

    @sat.setter
    def sat(self, sat_value):
        """Makes sure provided sat value is a positive"""
        self.sat_node.sat = sat_value

    # Private Methods =========================================================

    def _set_id(self, new_id):
        """Changes the id field if the new id is unique"""
        cc_id = _sanitize(new_id)
        # Check if this id is already registered
        if cc_id in ColorCorrection.members.keys():
            raise ValueError(
                'Error setting the id to "{cc_id}". This id is already a '
                'registered id.'.format(
                    cc_id=cc_id
                )
            )
        else:
            # Clear the current id from the dictionary
            ColorCorrection.members.pop(self._id)
            self._id = cc_id
            # Register the new id with the dictionary
            ColorCorrection.members[self._id] = self

    # Public Methods ==========================================================

    def build_element(self):
        """Builds an ElementTree XML element representing this CC"""
        cc_xml = ElementTree.Element('ColorCorrection')
        cc_xml.attrib = {'id': self.id}
        if self.input_desc:
            input_desc = ElementTree.SubElement(cc_xml, 'InputDescription')
            input_desc.text = self.input_desc
        if self.viewing_desc:
            viewing_desc = ElementTree.SubElement(cc_xml, 'ViewingDescription')
            viewing_desc.text = self.viewing_desc
        for description in self.desc:
            desc = ElementTree.SubElement(cc_xml, 'Description')
            desc.text = description
        # We need to make sure we call the private attributes here, since
        # we don't want to trigger a virgin sop or sat being initialized.
        if self._sop_node:
            cc_xml.append(self.sop_node.element)
        if self._sat_node:
            cc_xml.append(self.sat_node.element)

        return cc_xml

    # =========================================================================

    def determine_dest(self, output, directory):
        """Determines the destination file and sets it on the color correct"""

        filename = "{id}.{ext}".format(id=self.id, ext=output)

        self._file_out = os.path.join(directory, filename)

    # =========================================================================

    @classmethod
    def reset_members(cls):
        """Resets the class level members dictionary"""
        cls.members = {}

# ==============================================================================


class SatNode(ColorNodeBase):
    """Color node that contains saturation data.

    **Class Attributes:**

        element_names : [str]
            Contains a list of XML Elements that refer to this class for use
            in parsing XML files.

    **Attributes:**

        desc : [str]
            Since all Asc nodes which can contain a single description, can
            actually contain an infinite number of descriptions, the desc
            attribute is a list, allowing us to store every single description
            found during parsing.

            Setting desc directly will cause the value given to append to the
            end of the list, but desc can also be replaced by passing it a list
            or tuple. Desc can be emptied by passing it None, [] or ().

            Inherited from :class:`AscDescBase` .

        element : (<xml.etree.ElementTree.Element>)
            etree style Element representing the node. Inherited from
            :class:`AscXMLBase` .

        parent : ( :class:`ColorCorrection` )
            The parent :class:`ColorCorrection` instance that created this
            instance.

        sat : (Decimal)
            The saturation value (to be applied with Rec 709 coefficients) is
            stored here. Saturation is the last operation to be applied when
            applying a CDL.

            sat can be set with a Decimal, float, int or numeric string.

        xml : (str)
            A nicely formatted XML string representing the node. Inherited from
            :class:`AscXMLBase`.

        xml_root : (str)
            A nicely formatted XML, ready to write to file string representing
            the node. Formatted as an XML root, it includes the xml version and
            encoding tags on the first line. Inherited from
            :class:`AscXMLBase`.

    **Public Methods:**

        build_element()
            Builds an ElementTree XML Element for this node and all nodes it
            contains. ``element``, ``xml``, and ``xml_root`` attributes use
            this to build the XML. This function is identical to calling the
            ``element`` attribute. Overrides inherited placeholder method
            from :class:`AscXMLBase` .

        parse_xml_descs()
            Parses an ElementTree Element for any Description tags and appends
            any text they contain to the ``desc``. Inherited from
            :class:`AscDescBase`

    """

    # XML Fields for SopNodes can be one of these names:
    element_names = ['ASC_SAT', 'SATNode', 'SatNode']

    def __init__(self, parent):
        super(SatNode, self).__init__()

        self._parent = parent
        self._sat = Decimal('1.0')

    # Properties ==============================================================

    @property
    def parent(self):
        """Returns which :class:`ColorCorrection` created this SatNode"""
        return self._parent

    @property
    def sat(self):
        """Returns the protected sat attribute"""
        return self._sat

    @sat.setter
    def sat(self, value):
        """Runs checks and converts saturation value before setting"""
        # If given as a string, the string must be convertible to a Decimal
        if type(value) in [Decimal, float, int, str]:
            try:
                value = self._check_single_value(value, 'saturation')
            except (TypeError, ValueError):
                raise
            else:
                self._sat = Decimal(value)
        else:
            raise TypeError(
                'Saturation cannot be set directly with objects of type: '
                '"{type}". Value given: "{value}".'.format(
                    type=type(value),
                    value=value,
                )
            )

    # Public Methods ==========================================================

    def build_element(self):
        """Builds an ElementTree XML Element representing this SatNode"""
        sat = ElementTree.Element('SatNode')
        for description in self.desc:
            desc = ElementTree.SubElement(sat, 'Description')
            desc.text = description
        op_node = ElementTree.SubElement(sat, 'Saturation')
        op_node.text = _de_exponent(self.sat)
        return sat

# ==============================================================================


class SopNode(ColorNodeBase):
    """Color node that contains slope, offset and power data.

    Description
    ~~~~~~~~~~~

    Slope, offset and saturation are stored internally as lists, but always
    returned as tuples to prevent index assignment from being successful. This
    protects the user from inadvertently setting a single value in the list
    to be a non-valid value, which might result in values not being Decimals or
    even numbers at all.

    **Class Attributes:**

        element_names : [str]
            Contains a list of XML Elements that refer to this class for use
            in parsing XML files.

    **Attributes:**

        desc : [str]
            Since all Asc nodes which can contain a single description, can
            actually contain an infinite number of descriptions, the desc
            attribute is a list, allowing us to store every single description
            found during parsing.

            Setting desc directly will cause the value given to append to the
            end of the list, but desc can also be replaced by passing it a list
            or tuple. Desc can be emptied by passing it None, [] or ().

            Inherited from :class:`AscDescBase` .

        element : (<xml.etree.ElementTree.Element>)
            etree style Element representing the node. Inherited from
            :class:`AscXMLBase` .

        parent : ( :class:`ColorCorrection` )
            The parent :class:`ColorCorrection` instance that created this
            instance.

        slope : (Decimal, Decimal, Decimal)
            An rgb tuple representing the slope, which changes the slope of the
            input without shifting the black level established by the offset.
            These values must be positive. If you set this attribute with a
            single value, it will be copied over all 3 colors. Any single value
            given can be a Decimal, float, int or numeric string.

            default: (Decimal('1.0'), Decimal('1.0'), Decimal('1.0'))

        offset : (Decimal, Decimal, Decimal)
            An rgb tuple representing the offset, which raises or lowers the
            input brightness while holding the slope constant. If you set this
            attribute with a single value, it will be copied over all 3 colors.
            Any single value given can be a Decimal, float, int or numeric
            string.

            default: (Decimal('0.0'), Decimal('0.0'), Decimal('0.0'))

        power : (Decimal, Decimal, Decimal)
            An rgb tuple representing the power, which is the only function
            that changes the response curve of the function. Note that this has
            the opposite response to adjustments than a traditional gamma
            operator. These values must be positive. If you set this attribute
            with a single value, it will be copied over all 3 colors. Any
            single value given can be a Decimal, float, int or numeric string.

            default: (Decimal('1.0'), Decimal('1.0'), Decimal('1.0'))

        xml : (str)
            A nicely formatted XML string representing the node. Inherited from
            :class:`AscXMLBase`.

        xml_root : (str)
            A nicely formatted XML, ready to write to file string representing
            the node. Formatted as an XML root, it includes the xml version and
            encoding tags on the first line. Inherited from
            :class:`AscXMLBase`.

    **Public Methods:**

        build_element()
            Builds an ElementTree XML Element for this node and all nodes it
            contains. ``element``, ``xml``, and ``xml_root`` attributes use
            this to build the XML. This function is identical to calling the
            ``element`` attribute. Overrides inherited placeholder method
            from :class:`AscXMLBase` .

        parse_xml_descs()
            Parses an ElementTree Element for any Description tags and appends
            any text they contain to the ``desc``. Inherited from
            :class:`AscDescBase`

    """

    # XML Fields for SopNodes can be one of these names:
    element_names = ['ASC_SOP', 'SOPNode', 'SopNode']

    def __init__(self, parent):
        super(SopNode, self).__init__()

        self._parent = parent

        self._slope = [Decimal('1.0')] * 3
        self._offset = [Decimal('0.0')] * 3
        self._power = [Decimal('1.0')] * 3

    # Properties ==============================================================

    @property
    def parent(self):
        """Returns which :class:`ColorCorrection` created this SopNode"""
        return self._parent

    @property
    def slope(self):
        """Returns the slope as an tuple"""
        return tuple(self._slope)

    @slope.setter
    def slope(self, value):
        """Runs tests and converts slope rgb values before setting"""
        value = self._check_setter_value(value, 'slope')
        self._slope = value

    @property
    def offset(self):
        """Returns the offset as a tuple"""
        return tuple(self._offset)

    @offset.setter
    def offset(self, value):
        """Runs tests and converts offset rgb values before setting"""
        value = self._check_setter_value(value, 'offset', True)
        self._offset = value

    @property
    def power(self):
        """Returns the power as a tuple"""
        return tuple(self._power)

    @power.setter
    def power(self, value):
        """Runs tests and converts power rgb values before setting"""
        value = self._check_setter_value(value, 'power')
        self._power = value

    # Private Methods =========================================================

    def _check_rgb_values(self, values, name, negative_allow=False):
        """Checks a list or tuple containing 3 values for legitimacy

        **Args:**
            value : [(Decimal|str|float|int)]
                A list of three numeric values to be checked.

            name : (str)
                The type of values being checked: slope, offset, etc.

            negative_allow=False : (bool)
                If false, do not allow negative values.

        **Returns:**
            [Decimal, Decimal, Decimal]
                If all values pass all tests, returns values as a list of
                Decimals.

        **Raises:**
            TypeError:
                If a value given is not a number.

            ValueError:
                If length of list or tuple is not 3 or if negative is False,
                raised if value given is negative.

        """
        try:
            assert len(values) == 3
        except AssertionError:
            raise ValueError(
                'Error setting {name} with value: "{values}". '
                '{name_upper} values given as a list or tuple must have 3 '
                'elements, one for each color.'.format(
                    name=name,
                    name_upper=name.title(),
                    values=values
                )
            )

        values = list(values)

        for i in xrange(len(values)):
            try:
                values[i] = self._check_single_value(
                    values[i],
                    name,
                    negative_allow
                )
            except (TypeError, ValueError):
                raise

        return values

    # =========================================================================

    def _check_setter_value(self, value, name, negative_allow=False):
        """Exception handling wrapper handling setting values

        Ties together _check_single_value and _check_rgb_values

        **Args:**
            value : [(Decimal|str|float|int)]
                A list of three (or one) numeric values to be checked.

            name : (str)
                The type of values being checked: slope, offset, etc.

            negative_allow=False : (bool)
                If false, do not allow negative values.

        **Returns:**
            [Decimal, Decimal, Decimal]
                If all values pass all tests, returns values as a list of
                Decimals.

        **Raises:**
            TypeError:
                If a value given is not a number.

            ValueError:
                If length of list or tuple is not 3 or if negative is False,
                raised if value given is negative.

        """
        if type(value) in [Decimal, float, int, str]:
            try:
                value = self._check_single_value(value, name, negative_allow)
            except (TypeError, ValueError):
                raise
            else:
                set_value = [value] * 3
        elif type(value) in [list, tuple]:
            try:
                value = self._check_rgb_values(value, name, negative_allow)
            except (TypeError, ValueError):
                raise
            else:
                set_value = value
        else:
            raise TypeError(
                '{name} cannot be set directly with objects of type: "{type}".'
                ' Value given: "{value}".'.format(
                    name=name.title(),
                    type=type(value),
                    value=value,
                )
            )

        return set_value

    # Public Methods ==========================================================

    def build_element(self):
        """Builds an ElementTree XML Element representing this SopNode"""
        sop = ElementTree.Element('SOPNode')
        fields = ['Slope', 'Offset', 'Power']
        for description in self.desc:
            desc = ElementTree.SubElement(sop, 'Description')
            desc.text = description
        for i, grade in enumerate([self.slope, self.offset, self.power]):
            op_node = ElementTree.SubElement(sop, fields[i])
            op_node.text = '{valueR} {valueG} {valueB}'.format(
                valueR=_de_exponent(grade[0]),
                valueG=_de_exponent(grade[1]),
                valueB=_de_exponent(grade[2])
            )
        return sop

# ==============================================================================
# PRIVATE FUNCTIONS
# ==============================================================================


def _de_exponent(notation):
    """Translates scientific notation into non-normalized strings

     Unlike the methods to quantize a Decimal found on the Decimal FAQ, this
    always works.

    Args:
        notation : (Decimal|str|int|float)
            Any numeric value that may or may not be normalized.

    Raises:
        N/A

    Returns:
        (str)
            Returns a quantized value without any scientific notation.

    """
    notation = str(notation).lower()
    if 'e' not in notation:
        return notation

    notation = notation.split('e')
    # Grab the exponent value
    digits = int(notation[-1])
    # Grab the value we'll be adding 0s to
    value = notation[0]

    if value.startswith('-'):
        negative = '-'
        value = value[1:]
    else:
        negative = ''

    value = value.replace('.', '')

    if digits < 0:
        new_value = negative + '0.0' + '0' * (abs(digits) - 2) + value
    else:
        zeros = len(value)
        new_value = negative + value + '0' * (abs(digits) - zeros) + '0.0'
    return new_value

# ==============================================================================


def _sanitize(name):
    """Removes any characters in string name that aren't alnum or in '_.

    Any spaces will be replaced with underscores. If a name starts with an
    underscore or a period it's removed.

    Only alphanumeric characters, or underscores and periods, are allowed.

    Args:
        name : (str)
            The name to be sanitized.

    Raises:
        N/A

    Returns:
        (str)
            Sanitized name.

    """
    if not name:
        # If not name, it's probably an empty string, but let's throw back
        # exactly what we got.
        return name
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
