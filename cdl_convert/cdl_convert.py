#!/usr/bin/env python
"""

CDL Convert
==========

Converts between common ASC CDL (http://en.wikipedia.org/wiki/ASC_CDL)
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

cdl_convert
Copyright (c) 2014 Sean Wallitsch
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

from __future__ import print_function

from argparse import ArgumentParser
from ast import literal_eval
from xml.dom import minidom
import os
import re
import sys
from xml.etree import ElementTree

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
__version__ = "0.6.1"
__maintainer__ = "Sean Wallitsch"
__email__ = "shidarin@alphamatte.com"
__status__ = "Development"

# INPUT_FORMATS and OUTPUT_FORMATS are globals but located in the MAIN section
# of the file, as they are dispatcher dictionaries that require the functions
# to be parsed by python before the dictionary can be built.

if sys.version_info[0] >= 3:  # pragma: no cover
    enc = lambda x: bytes(x, 'UTF-8')  # pylint: disable=C0103
else:  # pragma: no cover
    enc = lambda x: x  # pylint: disable=C0103

# HALT_ON_ERROR is the exception handling variable for exceptions that can
# be handled silently.
#
# If we begin to get more config options, this will be moved into a singleton
# config class.
#
# Used in the following places:
#   Slope, power and sat values can't be negative and will truncate to 0.0
#   If id given to ColorCorrection is blank, will set to number of CCs
#   When determining if a non-existent directory referenced by MediaRef
#       contains an image sequence, will just return False.
#   If attempting to retrieve a referenced ColorCorrection whose id doesn't
#       exist.
#   If attempting to set a ColorCorrectionReference to a ColorCorrection whose
#       id doesn't exist. (Other than first creation)
HALT_ON_ERROR = False

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'AscColorSpaceBase',
    'AscDescBase',
    'AscXMLBase',
    'ColorCollection',
    'ColorCorrection',
    'ColorCorrectionReference',
    'ColorDecision',
    'ColorNodeBase',
    'MediaRef',
    'SatNode',
    'SopNode',
    'parse_ale',
    'parse_cc',
    'parse_ccc',
    'parse_rnh_cdl',
    'parse_flex',
    'reset_all',
    'sanity_check',
    'write_cc',
    'write_ccc',
    'write_rnh_cdl',
]

# ==============================================================================
# CLASSES
# ==============================================================================


class AscColorSpaceBase(object):  # pylint: disable=R0903
    """Base class for Asc XML type nodes that deal with colorspace

    Description
    ~~~~~~~~~~~

    This class is meant to be inherited by any node type that used viewing and
    input colorspace descriptions.

    This class doesn't do a lot right now, as we don't have any specific
    controls on how to set or retrieve these fields. In the future however,
    we'll parse incoming descriptions to try and resolve input colorspace and
    viewing colorspace.

    **Attributes:**

        input_desc : (str)
            Description of the color space, format and properties of the input
            images. Individual :class:`ColorCorrections` can override this.

        viewing_desc : (str)
            Viewing device, settings and environment. Individual
            :class:`ColorCorrections` can override this.

    **Public Methods:**

        parse_xml_input_desc()
            Parses an ElementTree Element to find & add an InputDescription.
            If none is found, ``input_desc`` will remain set to ``None``.

        parse_xml_viewing_desc()
            Parses an ElementTree Element to find & add a ViewingDescription.
            If none is found, ``viewing_desc`` will remain set to ``None``.

    """
    def __init__(self):
        # For multiple inheritance support.
        super(AscColorSpaceBase, self).__init__()

        self.input_desc = None
        self.viewing_desc = None

    # Public Methods ==========================================================

    def parse_xml_input_desc(self, xml_element):
        """Parses an ElementTree element to find & add an input description

        **Args:**
            xml_element : (``xml.etree.ElementTree.Element``)
                The element to parse for an Input Description element. If
                found, set our ``input_desc``

        **Returns:**
            (bool)
                True if found InputDescription Fields (even if blank)

        **Raises:**
            None

        """
        # If the text field is empty, this will return None, which is the
        # default value of viewing_desc and input_desc anyway.
        try:
            self.input_desc = xml_element.find('InputDescription').text
            return True
        except AttributeError:
            # We don't have an InputDescription and that's ok.
            return False

    # =========================================================================

    def parse_xml_viewing_desc(self, xml_element):
        """Parses an ElementTree element to find & add a viewing description

        **Args:**
            xml_element : (``xml.etree.ElementTree.Element``)
                The element to parse for a Viewing Description element. If
                found, set our ``viewing_desc``

        **Returns:**
            (bool)
                True if found InputDescription Fields (even if blank)

        **Raises:**
            None

        """
        # If the text field is empty, this will return None, which is the
        # default value of viewing_desc and input_desc anyway.
        try:
            self.viewing_desc = xml_element.find('ViewingDescription').text
            return True
        except AttributeError:
            # We don't have a ViewingDescription and that's ok.
            return False

# ==============================================================================


class AscDescBase(object):  # pylint: disable=R0903
    """Base class for most Asc XML type nodes, allows for infinite desc

    Description
    ~~~~~~~~~~~

    This class is meant to be inherited by any node type that uses description
    fields.

    **Attributes:**

        desc : [str]
            Since all Asc nodes which can contain a single description, can
            actually contain an infinite number of descriptions, the desc
            attribute is a list, allowing us to store every single description
            found during parsing.

            Setting desc directly will cause the value given to append to the
            end of the list, but desc can also be replaced by passing it a list
            or tuple. Desc can be emptied by passing it None, [] or ().

    **Public Methods:**

        parse_xml_descs()
            Parses an ElementTree Element for any Description tags and appends
            any text they contain to the ``desc``.

    """
    def __init__(self):
        super(AscDescBase, self).__init__()
        self._desc = []

    # Properties ==============================================================

    @property
    def desc(self):
        """Returns the list of descriptions"""
        return self._desc

    @desc.setter
    def desc(self, value):
        """Adds an entry to the descriptions"""
        if value is None:
            self._desc = []
        elif type(value) in [list, tuple]:
            self._desc = list(value)
        else:
            self._desc.append(value)

    # Public Methods ==========================================================

    def parse_xml_descs(self, xml_element):
        """Parses an ElementTree element to find & add any descriptions

        **Args:**
            xml_element : (``xml.etree.ElementTree.Element``)
                The element to parse for Description elements. Any found
                will be appended to the end of ``desc``

        **Returns:**
            None

        **Raises:**
            None

        """
        for desc_entry in xml_element.findall('Description'):
            if desc_entry.text:  # Don't attend if text returns none
                self.desc.append(desc_entry.text)

# ==============================================================================


class AscXMLBase(object):
    """Base class for nodes which can be converted to XML Elements

    Description
    ~~~~~~~~~~~

    This class contains several convenience attributes which can be used
    to retrieve ElementTree Elements, or nicely formatted strings.

    **Attributes:**

        element : (<xml.etree.ElementTree.Element>)
            etree style Element representing the node.

        xml : (str)
            A nicely formatted XML string representing the node.

        xml_root : (str)
            A nicely formatted XML, ready to write to file string representing
            the node. Formatted as an XML root, it includes the xml version and
            encoding tags on the first line.

    **Public Methods:**

        build_element()
            A placeholder method to be overriden by inheriting classes, calling
            it will always return None.

    """
    def __init__(self):
        super(AscXMLBase, self).__init__()

    # Properties ==============================================================

    @property
    def element(self):
        """etree style Element representing the node."""
        return self.build_element()

    @property
    def xml(self):
        """A nicely formatted XML string representing the node"""
        # We'll take the xml_root attrib, which is ready to write, and just
        # remove the first line, which is the xml version and encoding.
        dom_string = self.xml_root.split(enc('\n'))
        return enc('\n').join(dom_string[1:])

    @property
    def xml_root(self):
        """A nicely formatted XML string with a root element ready to write"""
        xml_string = ElementTree.tostring(self.element, 'UTF-8')
        dom_xml = minidom.parseString(xml_string)
        dom_string = dom_xml.toprettyxml(indent="    ", encoding='UTF-8')
        # Fix for ugly dom formatting prior to 2.7, taken from:
        # http://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
        if sys.version_info[0] < 3 and sys.version_info[1] < 7:  # pragma: no cover pylint: disable=E0012
            text_re = re.compile(r'>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
            dom_string = text_re.sub(r'>\g<1></', dom_string)
        return dom_string

    # Public Methods ==========================================================

    def build_element(self):  # pragma: no cover pylint: disable=R0201
        """Placeholder for reference by attributes. Will return None"""
        return None

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

        members : {str: :class`ColorCorrection`}
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
            raise ValueError(
                'Error initiating id to "{id}". This id is already a '
                'registered id.'.format(
                    id=id
                )
            )
        elif not id:
            if HALT_ON_ERROR:
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
        """Returns float value for saturation"""
        return self.sat_node.sat

    @sat.setter
    def sat(self, sat_value):
        """Makes sure provided sat value is a positive float"""
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


class ColorCorrectionReference(AscXMLBase):
    """Reference marker to a full color correction

    Description
    ~~~~~~~~~~~

    This is a fairly basic class that simply contains a reference to a full
    :class:`ColorCorrection` . The ``id`` attribute must match the
    ``id`` attribute in order for this class to function fully.

    When writing to a format that allows empty references (like ``cdl``),
    the reference can write correctly without breaking. However, if writing to
    a format that does not support reference objects at all (like ``ccc``),
    attempting to write an empty reference will result in a ``ValueError`` (if
    ``HALT_ON_ERROR`` is set to ``True``, or simply skip past the reference
    entirely.

    **Class Attributes:**

        members : {str: [:class`ColorCorrectionReference`]}
            All instanced :class:`ColorCorrectionReference` are added to this
            member dictionary. Multiple :class:`ColorCorrectionReference` can
            share the same reference id, therefore for each reference id key,
            the members dictionary stores a list of
            :class:`ColorCorrectionReference` instances that share that ``id``
            value.

    **Attributes:**

        cc : (:class:`ColorCorrection`)
            If the stored reference resolves to an existing
            :class:`ColorCorrection`, this attribute will return that node
            using the ``resolve_reference`` method. This attribute is the same
            as calling that method.

        parent : (:class:`ColorDecision`)
            The parent :class:`ColorDecision` that contains this node.

        id : (str)
            The :class:`ColorCorrection` id that this reference refers to. If
            ``HALT_ON_ERROR`` is set to ``True``, will raise a ``ValueError``
            if set to a :class:`ColorCorrection` ``id`` value that doesn't
            yet exist.

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

        reset_members()
            Resets the class level members list.

        resolve_reference()
            Attempts to return the :class:`ColorCorrection` that this
            reference is supposed to refer to.

            If ``HALT_ON_ERROR`` is set to ``True``, resolving a bad reference
            will raise a ``ValueError`` exception. If not set, it will simply
            return None.

            Otherwise (if the ``id`` attribute matches a known
            :class:`ColorCorrection` ``id``, the :class:`ColorCorrection` will
            be returned.

    """

    members = {}

    def __init__(self, id):  # pylint: disable=W0622
        super(ColorCorrectionReference, self).__init__()
        self._id = None
        # Bypass cc id existence checks on first set by calling private
        # method directly.
        self._set_id(id)

        # While all ColorCorrectionReferences should be under a
        # ColorDecision node, we won't strictly enforce that a
        # parent must exist.
        self.parent = None

    # Properties ==============================================================

    @property
    def cc(self):  # pylint: disable=C0103
        """Returns the referenced ColorCorrection"""
        return self.resolve_reference()

    @property
    def id(self):  # pylint: disable=C0103
        """Returns the reference id"""
        return self._id

    @id.setter
    def id(self, ref_id):  # pylint: disable=C0103
        """Sets the reference id"""
        if ref_id not in ColorCorrection.members and HALT_ON_ERROR:
            raise ValueError(
                "Reference id '{id}' does not match any existing "
                "ColorCorrection id in ColorCorrection.members "
                "dictionary.".format(
                    id=ref_id
                )
            )

        self._set_id(ref_id)

    # Private Methods =========================================================

    def _set_id(self, new_ref):
        """Changes the id field and updates members dictionary"""
        # The only time it won't be in here is if this is the first time
        # we set it.
        if self.id in ColorCorrectionReference.members:
            ColorCorrectionReference.members[self.id].remove(self)
            # If the remaining list is empty, we'll pop it out
            if not ColorCorrectionReference.members[self.id]:
                ColorCorrectionReference.members.pop(self.id)

        # Check if this id is already registered
        if new_ref in ColorCorrectionReference.members:
            ColorCorrectionReference.members[new_ref].append(self)
        else:
            ColorCorrectionReference.members[new_ref] = [self]

        self._id = new_ref

    # Public Methods ==========================================================

    def build_element(self):
        """Builds an ElementTree XML element representing this reference"""
        cc_ref_xml = ElementTree.Element('ColorCorrectionRef')
        cc_ref_xml.attrib = {'ref': self.id}

        return cc_ref_xml

    # =========================================================================

    @classmethod
    def reset_members(cls):
        """Resets the member list"""
        cls.members = {}

    # =========================================================================

    def resolve_reference(self):
        """Returns the ColorCorrection this reference points to"""
        if self.id in ColorCorrection.members:
            return ColorCorrection.members[self.id]
        else:
            if HALT_ON_ERROR:
                raise ValueError(
                    "Cannot resolve ColorCorrectionReference with reference "
                    "id of '{id}' because no ColorCorrection with that id "
                    "can be found.".format(
                        id=self.id
                    )
                )
            else:
                return None

# ==============================================================================


class ColorDecision(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0903
    """Contains a media ref and a ColorCorrection or reference to CC.

    Description
    ~~~~~~~~~~~

    This class is a simple container to link a :class:`ColorCorrection` (or
    :class:`ColorCorrectionReference` ) with a :class:`MediaRef` . The
    :class:`MediaRef` is optional, the ColorCorrection is not. The
    ColorCorrection does not need to be provided at initialization time
    however, as :class:`ColorDecision` provides an XML element parser
    for deriving one.

    The primary purpose of a ColorDecision node is to associate a
    ColorCorrection node with one or more items of Media Reference.

    Along with Media Reference, a ColorDecision can contain the normal
    type of input, viewer and description metadata.

    Additional, it is the only node that can contain ColorCorrectionRef
    nodes, which link the same ColorCorrection to many different
    ColorDecisions (and thus, many different items of media reference)

    An example containing a ColorCorrection node:
    ::
        <ColorDecision>
            <MediaRef ref="http://www.theasc.com/foasc-logo2.png"/>
            <ColorCorrection id="ascpromo">
                <SOPNode>
                    <Description>get me outta here</Description>
                    <Slope>0.9 1.1 1.0</Slope>
                    <Offset>0.1 -0.01 0.0</Offset>
                    <Power>1.0 0.99 1.0</Power>
                </SOPNode>
            </ColorCorrection>
        </ColorDecision>

    But it can also contain just a reference:
    ::
        <ColorDecision>
            <MediaRef ref="best/project/ever/jim.0100.dpx"/>
            <ColorCorrectionRef ref="xf45.x628"/>
        </ColorDecision>

    **Class Attributes:**

        members : {str: [:class`ColorDecision`]}
            All instanced :class:`ColorDecision` are added to this
            member dictionary. The key is the id or reference id of the
            contained :class:`ColorCorrection` or
            :class:`ColorCorrectionReference` Multiple :class:`ColorDecision`
            can , therefore for each reference id key,
            the members dictionary stores a list of
            :class:`ColorDecision` instances that share that ``id``
            value.

    **Attributes:**

        cc : (:class:`ColorCorrection` | :class:`ColorCorrectionReference`)
            Returns the contained ColorCorrection, even if it's a reference.

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

        input_desc : (str)
            Description of the color space, format and properties of the input
            images. Inherited from :class:`AscColorSpaceBase` .

        is_ref : (bool)
            True if contains a :class:`ColorCorrectionReference` object instead
            of a :class:`ColorCorrection`

        media_ref : (:class:`MediaRef`)
            Returns the contained :class:`MediaRef` or None.

        parent : (:class:`ColorDecisionList`)
            The parent node that contains this node.

        set_parentage()
            Sets child :class:`ColorCorrection` (or
            :class:`ColorCorrectionReference`) and :class:`MediaRef` (if
            present) ``parent`` attribute to point to this instance.

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

        parse_xml_color_correction()
            Parses a ColorDecision ElementTree Element for a ColorCorrection
            Element or a ColorCorrectionRef Element.

        parse_xml_color_decision()
            Parses a ColorDecision ElementTree Element for metadata,
            then calls parsers for ColorCorrection and MediaRef.

        parse_xml_descs()
            Parses an ElementTree Element for any Description tags and appends
            any text they contain to the ``desc``. Inherited from
            :class:`AscDescBase`

        parse_xml_input_desc()
            Parses an ElementTree Element to find & add an InputDescription.
            If none is found, ``input_desc`` will remain set to ``None``.
            Inherited from :class:`AscColorSpaceBase`

        parse_xml_media_ref()
            Parses an ColorDecision Element for a MediaRef Element.

        parse_xml_viewing_desc()
            Parses an ElementTree Element to find & add a ViewingDescription.
            If none is found, ``viewing_desc`` will remain set to ``None``.
            Inherited from :class:`AscColorSpaceBase`

        reset_members()
            Resets the class level members list.

    """

    members = {}

    def __init__(self, color_correct=None, media=None):
        """Inits an instance of ColorDecision"""
        super(ColorDecision, self).__init__()
        self.parent = None
        self._cc = None
        self._set_cc(color_correct)
        self._media_ref = media

        self.set_parentage()

    # Properties ==============================================================

    @property
    def cc(self):  # pylint: disable=C0103
        """Returns the contained CC or CC Ref"""
        return self._cc

    @cc.setter
    def cc(self, new_cc):  # pylint: disable=C0103
        """Sets the contained cc, updates dictionary and parentage"""
        self._set_cc(new_cc)

    @property
    def is_ref(self):
        """True if our cc is a reference cc"""
        return type(self.cc) is ColorCorrectionReference

    @property
    def media_ref(self):
        """Returns Media Ref (if we have one) or none"""
        return self._media_ref

    @media_ref.setter
    def media_ref(self, new_media_ref):
        """Sets media ref and updates parentage"""
        self._media_ref = new_media_ref
        if new_media_ref:
            new_media_ref.parent = self

    # Private Methods =========================================================

    def _set_cc(self, new_cc):
        """Sets cc to new_cc and updates members dictionary"""
        if self.cc:
            # If we have a cc, we've already been added to the member's list,
            # and need to update membership.
            if self.cc.id in ColorDecision.members:
                ColorDecision.members[self.cc.id].remove(self)
                # If the remaining list is empty, we'll pop it out
                if not ColorDecision.members[self.cc.id]:
                    ColorDecision.members.pop(self.cc.id)

        if new_cc:
            # It's possible to have new_cc be None, in which case we won't
            # assign this ColorDecision to the member dictionary.
            #
            # Check if this id is already registered
            if new_cc.id in ColorDecision.members:
                ColorDecision.members[new_cc.id].append(self)
            else:
                ColorDecision.members[new_cc.id] = [self]

            new_cc.parent = self

        self._cc = new_cc

    # Public Methods ==========================================================

    def build_element(self):
        """Builds an ElementTree XML element representing this CC"""
        cd_xml = ElementTree.Element('ColorDecision')
        if self.input_desc:
            input_desc = ElementTree.SubElement(cd_xml, 'InputDescription')
            input_desc.text = self.input_desc
        if self.viewing_desc:
            viewing_desc = ElementTree.SubElement(cd_xml, 'ViewingDescription')
            viewing_desc.text = self.viewing_desc
        for description in self.desc:
            desc = ElementTree.SubElement(cd_xml, 'Description')
            desc.text = description
        # Customary for the Media Ref element to go first (if there is one)
        if self.media_ref:
            cd_xml.append(self.media_ref.element)

        cd_xml.append(self.cc.element)

        return cd_xml

    # =========================================================================

    def parse_xml_color_correction(self, xml_element):
        """Parses a Color Decision element to find a ColorCorrection"""
        cc_elem = xml_element.find('ColorCorrection')
        if not cc_elem:
            # Perhaps we're a ColorCorrectionRef?
            cc_elem = xml_element.find('ColorCorrectionRef')
            if not cc_elem:
                # No ColorCorrection or CCRef? This is a bad ColorDecision
                return False
            else:
                # Parse the ColorCorrectionRef
                ref_id = cc_elem.attrib['ref']
                self.cc = ColorCorrectionReference(ref_id)
                self.cc.parent = self
        else:
            # Parse the ColorCorrection
            self.cc = parse_cc(cc_elem)
            self.cc.parent = self

    # =========================================================================

    def parse_xml_color_decision(self, xml_element):
        """Parses a Color Decision element and builds a :class:`ColorDecision`

        **Args:**
            input_file : (<ElementTree.Element>)
                The ``ElementTree.Element`` object of the ColorDecision

        **Returns:**
            None

        **Raises:**
            ValueError:
                Bad XML formatting can raise ValueError is missing required
                elements.

        """
        # Grab our descriptions and add them to the cd.
        self.parse_xml_descs(xml_element)
        # See if we have a viewing description.
        self.parse_xml_viewing_desc(xml_element)
        # See if we have an input description.
        self.parse_xml_input_desc(xml_element)

        # Grab our ColorCorrection
        if not self.parse_xml_color_correction(xml_element):
            raise ValueError(
                'ColorDecisions require at least one ColorCorrection or '
                'ColorCorrectionReference node, but neither was found.'
            )

        # Grab our MediaRef (if found)
        self.parse_xml_media_ref(xml_element)

    # =========================================================================

    def parse_xml_media_ref(self, xml_element):
        """Parses a Color Decision element to find a MediaRef"""
        media_ref_elem = xml_element.find('MediaRef')
        if media_ref_elem:
            ref_uri = media_ref_elem.attrib['ref']
            self.media_ref = MediaRef(ref_uri=ref_uri)

    # =========================================================================

    @classmethod
    def reset_members(cls):
        """Resets the member list"""
        cls.members = {}

    # =========================================================================

    def set_parentage(self):
        """Sets the parent of all child nodes to point to this instance"""
        self.cc.parent = self
        if self.media_ref:  # Media ref objects are optional
            self.media_ref.parent = self

# ==============================================================================


class ColorCollection(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0902,R0904
    """Container class for ColorDecisionLists and ColorCorrectionCollections.

    Description
    ~~~~~~~~~~~

    Collections need to store children and have access to descriptions,
    input descriptions, and viewing descriptions.

    **Class Attributes:**

        members : [ :class`ColorCollection`]
            All instanced :class:`ColorCollection` are added to this member
            list. Unlike the :class:`ColorCorrection` member's dictionary,
            :class:`ColorCollection` do not need any unique values to exist.

            This is currently only used for determining an id value when
            exporting and no file_in attribute is set.

    **Attributes:**

        all_children : (:class:`ColorCorrection`, :class:`ColorDecision`)
            A tuple of all the children of this collection, both
            Corrections and Decisions.

        color_corrections : (:class:`ColorCorrection`)
            All the :class:`ColorCorrection` children are listed here.

        color_decisions : (:class:`ColorDecision`)
            All the :class:`ColorDecision` children are listed here.

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
            Filepath used to create this :class:`ColorCollection` .

        file_out : (str)
            Filepath this :class:`ColorCollection` will be written to.

        input_desc : (str)
            Description of the color space, format and properties of the input
            images. Inherited from :class:`AscColorSpaceBase` .

        is_ccc : (bool)
            True if this collection currently represents ``.ccc``.

        is_cdl : (bool)
            True if this collection currently represents ``.cdl``.

        type : (str)
            Either ``ccc`` or ``cdl``, represents the type of collection
            this class currently will export by default.

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

        xmlns : (str)
            Describes the version of the ASC XML Schema that cdl_convert writes
            out to files following the full schema (``.ccc`` and ``.cdl``)

    **Public Methods:**

        append_child()
            Appends the given object, either a :class:`ColorCorrection` or a
            :class:`ColorDecision` , to the respective attribute list, either
            ``color_corrections`` or ``color_decision`` depending on the class
            of the object passed in.

        append_children()
            Given a list, will iterate through and append each element of that
            list to the correct child list, using the ``append_child()``
            method.

        build_element()
            Builds an ElementTree XML Element for this node and all nodes it
            contains. ``element``, ``xml``, and ``xml_root`` attributes use
            this to build the XML. This function is identical to calling the
            ``element`` attribute. Overrides inherited placeholder method
            from :class:`AscXMLBase` .

            Here on :class:`ColorCollection` , this is a pointer to
            ``build_element_ccc()`` or ``build_element_cdl()`` depending on
            which type the :class:`ColorCollection` is currently set to.

        build_element_ccc()
            Builds a CCC style XML tree representing this
            :class:`ColorCollection` instance.

        build_element_cdl()
            Builds a CDL style XML tree representing this
            :class:`ColorCollection` instance.

        copy_collection()
            Creates and returns an exact new instance that's an exact copy of
            the current instance. Note that references to the child instances
            will be copied, but that the child instances themselves will
            not be.

        merge_collections()
            Merges all members of a list containing :class:`ColorCollection`
            and the instance this is called on to return a new
            :class:`ColorCollection` that is primarily a copy of this instance,
            but contains all children and description elements from the given
            collections. `input_desc`, `viewing_desc`, `file_in`, and `type`
            will be set to the values of the parent instance.

        parse_xml_color_corrections()
            Parses an ElementTree element to find & add all ColorCorrection.

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

        set_parentage()
            Sets all child :class:`ColorCorrection` and :class:`ColorDecision`
            ``parent`` attribute to point to this instance.

        set_to_ccc()
            Switches the ``type`` of this collection to export a ``ccc`` style
            xml collection by default.

        set_to_cdl()
            Switches the ``type`` of this collection to export a ``cdl`` style
            xml collection by default.

    """

    members = []

    def __init__(self, input_file=None):
        super(ColorCollection, self).__init__()

        self._color_corrections = []
        self._color_decisions = []
        self._file_in = os.path.abspath(input_file) if input_file else None
        self._file_out = None
        self._type = 'ccc'
        self._xmlns = "urn:ASC:CDL:v1.01"

        ColorCollection.members.append(self)

    # Properties ==============================================================

    @property
    def all_children(self):
        """Returns a list of both color_corrections and color_decisions"""
        return self.color_corrections + self.color_decisions

    @property
    def color_corrections(self):
        """Returns the list of child ColorCorrections"""
        return self._color_corrections

    @color_corrections.setter
    def color_corrections(self, values):
        """Makes sure color_corrections is only set with ColorCorrection"""
        self._color_corrections = self._list_setter(
            'color_corrections', ColorCorrection, values
        )

    @property
    def color_decisions(self):
        """Returns the list of child ColorDecisions"""
        return self._color_decisions

    @color_decisions.setter
    def color_decisions(self, values):
        """Makes sure color_decisions is only set with ColorDecision"""
        self._color_decisions = self._list_setter(
            'color_decisions', ColorDecision, values
        )

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
    def is_ccc(self):
        """True if this collection currently represents .ccc"""
        return self.type == 'ccc'

    @property
    def is_cdl(self):
        """True if this collection currently represents .cdl"""
        return self.type == 'cdl'

    @property
    def type(self):
        """Describes the type of ColorCollection this class will export"""
        return self._type

    @type.setter
    def type(self, value):
        """Checks if type is either cdl or ccc"""
        if value.lower() not in ['ccc', 'cdl']:
            raise ValueError('ColorCollection type must be set to either '
                             'ccc or cdl.')
        else:
            self._type = value.lower()

    @property
    def xmlns(self):
        """Describes the version of the XML schema written by cdl_convert"""
        return self._xmlns

    # Private Methods =========================================================

    @staticmethod
    def _list_setter(list_name, color_class, values):
        """Sets a list to provided values but first checks membership"""
        if values is None:
            return []
        elif type(values) in [list, tuple, set]:
            for color in values:
                # We need to make sure each member is of the correct class.
                if color.__class__ != color_class:
                    raise TypeError(
                        "ColorCollection().{list_name} cannot be set to "
                        "provided list because not all members of that list "
                        "are of the {class_name} class.".format(
                            list_name=list_name,
                            class_name=color_class.__name__
                        )
                    )
            return list(set(values))
        elif values.__class__ == color_class:
            # If we just got passed the correct class, we'll return it as a
            # one member list.
            return [values]
        else:
            raise TypeError(
                "ColorCollection().{list_name} cannot be set to item "
                "of type '{type}'. Please set {list_name} with a "
                "list containing only members of class {class_name}.".format(
                    list_name=list_name,
                    type=type(values),
                    class_name=color_class.__name__
                )
            )

    # Public Methods ==========================================================

    def append_child(self, child):
        """Appends a given child to the correct list of children"""
        if child.__class__ == ColorCorrection:
            self._color_corrections.append(child)
        elif child.__class__ == ColorDecision:
            self._color_decisions.append(child)
        else:
            raise TypeError("Can only append ColorCorrection and "
                            "ColorDecision objects.")

        child.parent = self

    # =========================================================================

    def append_children(self, children):
        """Appends an entire list to the correctly list of children"""
        for child in children:
            self.append_child(child)

    # =========================================================================

    def build_element(self):
        """Builds an ElementTree XML element representing for ColorCollection"""
        if self.is_ccc:
            return self.build_element_ccc()
        elif self.is_cdl:  # pragma: no cover
            return self.build_element_cdl()

    # =========================================================================

    def build_element_ccc(self):
        """Builds a CCC XML element representing this ColorCollection"""
        ccc_xml = ElementTree.Element('ColorCorrectionCollection')
        ccc_xml.attrib = {'xmlns': self.xmlns}
        if self.input_desc:
            input_desc = ElementTree.SubElement(ccc_xml, 'InputDescription')
            input_desc.text = self.input_desc
        if self.viewing_desc:
            viewing_desc = ElementTree.SubElement(ccc_xml, 'ViewingDescription')
            viewing_desc.text = self.viewing_desc
        for description in self.desc:
            desc = ElementTree.SubElement(ccc_xml, 'Description')
            desc.text = description
        for color_correct in self.color_corrections:
            ccc_xml.append(color_correct.element)

        return ccc_xml

    # =========================================================================

    def build_element_cdl(self):  # pragma: no cover
        """Builds a CDL XML element representing this ColorCollection"""
        return None

    # =========================================================================

    def copy_collection(self):
        """Creates and returns a copy of this collection"""
        new_col = ColorCollection()
        new_col.desc = self.desc
        new_col.file_in = self.file_in if self.file_in else None
        new_col.input_desc = self.input_desc
        new_col.viewing_desc = self.viewing_desc
        new_col.type = self.type
        new_col.append_children(self.all_children)
        return new_col

    # =========================================================================

    def determine_dest(self, directory):
        """Determines the destination file and sets it on the cdl"""
        if self.file_in:
            filename = os.path.splitext(os.path.basename(self.file_in))[0]
        else:
            filename = 'color_collection_{id}'.format(
                id=str(ColorCollection.members.index(self)).rjust(3, '0')
            )

        filename = "{file_in}.{ext}".format(file_in=filename, ext=self.type)

        self._file_out = os.path.join(directory, filename)

    # =========================================================================

    def merge_collections(self, collections):
        """Merges multiple collections together and returns a new one"""
        new_col = self.copy_collection()

        # We need to move all the children into one big list, so that
        # we can move it into a set to eliminate duplicates.
        children = new_col.all_children
        # Now that all of new_col's children are in the children list,
        # let's clear out the new_col lists.
        # We'll repopulate them with the full lists after adding
        # all the additional children.
        new_col.color_corrections = []
        new_col.color_decisions = []

        for col in collections:
            if col == self:  # Don't add ourselves
                continue
            new_col.desc.extend(col.desc)
            children.extend(col.all_children)

        new_col.append_children(children)

        # Remove duplicates
        new_col.color_corrections = set(new_col.color_corrections)
        new_col.color_decisions = set(new_col.color_decisions)

        return new_col

    # =========================================================================

    def parse_xml_color_corrections(self, xml_element):
        """Parses an ElementTree element to find & add all ColorCorrection.

        **Args:**
            xml_element : (``xml.etree.ElementTree.Element``)
                The element to parse for multiple ColorCorrection elements. If
                found, append to our ``color_corrections``.

        **Returns:**
            (bool)
                True if found ColorCorrections.

        **Raises:**
            None

        """
        cc_nodes = xml_element.findall('ColorCorrection')
        if not cc_nodes:
            return False

        for cc_node in xml_element.findall('ColorCorrection'):
            cdl = parse_cc(cc_node)
            cdl.parent = self
            self._color_corrections.append(cdl)

        return True

    # =========================================================================

    def parse_xml_color_decisions(self, xml_element):
        """Parses an ElementTree element to find & add all ColorDecisions.

        **Args:**
            xml_element : (``xml.etree.ElementTree.Element``)
                The element to parse for multiple ColorDecision elements. If
                found, append to our ``color_decisions``.

        **Returns:**
            (bool)
                True if found ColorCorrections.

        **Raises:**
            None

        """
        cd_nodes = xml_element.findall('ColorDecision')
        if not cd_nodes:
            return False

        for cd_node in xml_element.findall('ColorDecision'):
            color_decision = ColorDecision()
            color_decision.parse_xml_color_decision(cd_node)
            color_decision.parent = self
            self._color_decisions.append(color_decision)

        return True

    # =========================================================================

    @classmethod
    def reset_members(cls):
        """Resets the member list"""
        cls.members = []

    # =========================================================================

    def set_parentage(self):
        """Sets the parent of all child nodes to point to this instance"""
        for node in self.all_children:
            node.parent = self

    # =========================================================================

    def set_to_ccc(self):
        """Switches the type of the ColorCollection to export .ccc style xml"""
        self._type = 'ccc'

    # =========================================================================

    def set_to_cdl(self):
        """Switches the type of the ColorCollection to export .cdl style xml"""
        self._type = 'cdl'

# ==============================================================================


class ColorNodeBase(AscDescBase, AscXMLBase):  # pylint: disable=R0903
    """Base class for SOP and SAT nodes.

    Description
    ~~~~~~~~~~~

    This class is meant only to be inherited by :class:`SopNode` and
    :class:`SatNode` and should not be used outside of those classes.

    It inherits from both :class:`AscDescBase` and :class:`AscXMLBase` giving
    the child classes both ``desc`` and ``xml`` related functionality.

    This class is also home to a private function which helps :class:`SopNode`
    and :class:`SatNode` perform type and value checks on incoming values.

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
    def __init__(self):
        super(ColorNodeBase, self).__init__()

    # Private Methods =========================================================

    @staticmethod
    def _check_single_value(value, name, negative_allow=False):
        """Checks given value for legitimacy.

        **Args:**
            value : (str, float, int)
                Any numeric value to be checked.

            name : (str)
                The type of value being checked: slope, offset, etc.

            negative_allow=False : (bool)
                If false, do not allow negative values.

        **Returns:**
            (float)
                If value passes all tests, returns value as float.

        **Raises:**
            TypeError:
                If value given is not a number.

            ValueError:
                If negative is False, raised if value given is negative.

        """
        # If given as a string, the string must be convertible to a float
        if type(value) == str:
            try:
                value = float(value)
            except ValueError:
                raise TypeError(
                    'Error setting {name} with value: "{value}". '
                    'Value is not a number.'.format(
                        name=name,
                        value=value
                    )
                )
        # If given as a single number, that number must be positive
        if type(value) in [float, int] and not negative_allow:
            if value < 0:
                if HALT_ON_ERROR:
                    raise ValueError(
                        'Error setting {name} with value: "{value}". '
                        'Values must not be negative'.format(
                            name=name,
                            value=value
                        )
                    )
                else:
                    value = 0

        return float(value)

# ==============================================================================


class MediaRef(AscXMLBase):
    """A directory of files or a single file used for grade reference

    Description
    ~~~~~~~~~~~

    :class:`MediaRef` is a container for an image path that should be
    referenced in regards to the color correction being performed. What that
    reference means must be further clarified, either through communication or
    Description fields.

    Requires a ``ref_uri`` and an optional ``parent`` to instantiate.

    An XML URI is usually a filepath to a directory or file, sometimes
    proceeded by a protocol (such as ``http://``). **Note that many of the**
    **functions and methods described below do not function properly when**
    **given a URI with a protocol in front.**

    The parent of a :class:`MediaRef` should typically be a
    :class:`ColorDecision` , and in fact the CDL specification states that
    no other container is allowed to contain a :class:`MediaRef`. That
    restriction is not enforced here, but writers for ``.ccc`` and ``.cc`` will
    only pass through :class:`MediaRef` as Description entries.

    **Class Attributes:**

        members : {str: [:class:`MediaRef`]}
            All instances of :class:`MediaRef` are added to this class level
            members dictionary, with the key being the full reference URI.
            Since it's possible that multiple :class:`MediaRef` point to the
            same reference URI, the value returned is a list of
            :class:`MediaRef` that all have a value of that same URI.

            When you change a single :class:`MediaRef` ref attribute, it
            removes itself from the old key's list, and adds itself to the
            new key's list. The old key is removed from the dictionary if this
            :class:`MediaRef` was the last member.

    **Attributes:**

        directory : (str)
            The directory portion of the URI, without the protocol or filename.

        element : (<xml.etree.ElementTree.Element>)
            etree style Element representing the node. Inherited from
            :class:`AscXMLBase` .

        exists : (bool)
            True if the path is present in the file system.

        filename : (str)
            The filename portion of the URI, without any protocol or directory.

        is_abs : (bool)
            True if ``directory`` is an absolute reference.

        is_dir : (bool)
            True if ``path`` points to a directory with no filename portion.

        is_seq : (bool)
            True if ``path`` points to an image sequence or a directory of
            image sequences. Image sequences are determined by files ending
            in a dot or underscore, followed by an integer, followed by the
            file extension. If the filename reference given already has pound
            padding or %d indication padding, this will also return true.

            Valid image sequences:
                - TCM100X_20140215.0001.exr
                - Bobs Big_Score_2.jpg
                - 2383-279873.67267_32t7634.63278623781638218763.exr
                - 104fl.x034.######.dpx
                - 104fl.x034_%06d.dpx

        parent : (:class:`ColorDecision`)
            The parent that contains this :class:`MediaRef` object. This should
            normally be a :class:`ColorDecision` , but that is not enforced.

        path : (str)
            The directory joined with the filename via os.path.join(), if
            there is no filename, path is identical to ``directory``. If there
            is no protocol, ``path`` is identicial to ``ref``.

        protocol : (str)
            The URI protocol section of the URI, if any. This is the section
            that proceeds the '://' of any URI. If there is no '://' in the
            given URI, this is empty.

        ref : (str)
            The full URI reference which includes the protocol, directory and
            filename. If there is no protocol and no filename, ``ref`` is
            identical to ``directory``.

        seq : (str)
            If ``is_seq`` finds that the filename or directory refers to one or
            more image sequences, ``seq`` will return the first found sequence
            in  the form of filename.####.ext (or filename_####.ext if the
            sequence has an ``_`` in front of the frame numbers).
            *Note that there may be more than one image sequence if* ``ref``
            *points to a directory*. To get a list of all image sequences
            found, use ``seqs``.

            Only if a reference was given to us already in the form of ``%d``
            padding will ``seq`` and ``seqs`` return a sequence filename with
            ``%d`` padding.

        seqs : [str]
            Returns all found sequences in a list. If ``ref`` points to a
            filename, this list will only contain one sequence. If ``ref``
            points to a directory, all sequences found in that directory will
            be in this list.

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

        reset_members()
            Resets the class level members list.

    """

    members = {}

    def __init__(self, ref_uri, parent=None):
        super(MediaRef, self).__init__()
        self._protocol, self._dir, self._filename = self._split_uri(ref_uri)
        self.parent = parent

        # If we're a directory, we can contain one or more sequences, but we
        # won't do the work to figure that out until is_seq, seq, and seqs are
        # called for.
        self._is_seq = None
        self._sequences = None

        # Add this instance to the member dictionary.
        self._change_membership()

    # Properties ==============================================================

    @property
    def directory(self):
        """Returns the directory the uri points to"""
        return self._dir

    @directory.setter
    def directory(self, value):
        """Checks directory for type and resets cached properties"""
        if type(value) is str:
            old_ref = self.ref
            self._dir = value
            self._change_membership(old_ref=old_ref)
            self._reset_cached_properties()
        else:
            raise TypeError(
                'Directory must be set with a string, not {type}'.format(
                    type=type(value)
                )
            )

    @property
    def exists(self):
        """Convenience property for os.path.exists"""
        return os.path.exists(self.path)

    @property
    def filename(self):
        """Returns the filename the uri points to, if any"""
        return self._filename

    @filename.setter
    def filename(self, value):
        """Checks filename for type and resets cached properties"""
        if type(value) is str:
            old_ref = self.ref
            self._filename = value
            self._change_membership(old_ref=old_ref)
            self._reset_cached_properties()
        else:
            raise TypeError(
                'Filename must be set with a string, not {type}'.format(
                    type=type(value)
                )
            )

    @property
    def is_abs(self):
        """Returns True if path is an absolute path"""
        return os.path.abspath(self.path)

    @property
    def is_dir(self):
        """Returns True if path points to a directory"""
        return os.path.isdir(self.path)

    @property
    def is_seq(self):
        """Returns True if path is to an image sequence"""
        if self._is_seq is None:
            self._get_sequences()
        return self._is_seq

    @property
    def path(self):
        """Returns the path without any uri protocol"""
        return os.path.join(self._dir, self._filename)

    @property
    def protocol(self):
        """Returns the protocol of the uri, if any"""
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        """Checks protocol for type and resets cached properties"""
        if type(value) is str:
            # If :// was appended we'll remove it.
            if value.endswith('://'):
                value = value[:-3]
            old_ref = self.ref
            self._protocol = value
            self._change_membership(old_ref=old_ref)
            # We probably don't need to reset the cached properties, but we
            # will just to be safe.
            self._reset_cached_properties()
        else:
            raise TypeError(
                'Protocol must be set with a string, not {type}'.format(
                    type=type(value)
                )
            )

    @property
    def ref(self):
        """Returns the reference uri"""
        if self._protocol:
            prefix = "{proto}://".format(proto=self._protocol)
        else:
            prefix = ''
        return prefix + self.path

    @ref.setter
    def ref(self, uri):
        """Sets the reference uri and resets all cached properties"""
        if type(uri) is str:
            old_ref = self.ref
            self._protocol, self._dir, self._filename = self._split_uri(uri)
            self._change_membership(old_ref=old_ref)
            self._reset_cached_properties()
        else:
            raise TypeError(
                'URI must be set with a string, not {type}'.format(
                    type=type(uri)
                )
            )

    @property
    def seq(self):
        """Returns first found sequence with frames as # padding"""
        if self._is_seq is None:
            self._get_sequences()
        elif not self._is_seq:
            return None

        return self._sequences[0]

    @property
    def seqs(self):
        """Returns all found sequences with frames as # padding"""
        if self._is_seq is None:
            self._get_sequences()
        elif not self._is_seq:
            return []

        return self._sequences

    # Private Methods =========================================================

    def _change_membership(self, old_ref=None):
        """Change which ref uri this instance is under in the class dict.

        We remove ourselves from the list returned by the key of old_ref
        in the member dictionary, then append ourselves to the list of the
        new ref key. If the ref isn't already in the dictionary, we'll be
        creating a new list with ourselves as the only member.

        **Args:**

            old_ref=None : (str)
                The previous uri reference of the instance. We'll look in the
                class level member dictionary for this uri as a key, then
                remove ourselves. If old_ref isn't a key, or we're not in the
                list it returns, we'll just move on.

        Returns:
            None

        Raises:
            N/A

        """
        if old_ref:
            try:
                MediaRef.members[old_ref].remove(self)
            except (KeyError, ValueError):
                # Either the key doesn't exist or we're not in the list.
                # Either way, it doesn't matter to us.
                pass
            else:
                # Now that we're removed, we need to see if the list is empty,
                # and if so, delete the key ref.
                if not MediaRef.members[old_ref]:
                    del MediaRef.members[old_ref]
        try:
            MediaRef.members[self.ref].append(self)
        except KeyError:
            MediaRef.members[self.ref] = [self]

    # =========================================================================

    def _get_sequences(self):  # pylint: disable=R0912
        """Determines if the media ref is pointing to an image sequence"""
        re_exp = r'(^[ \w_.-]+[_.])([0-9]+)(\.[a-zA-Z0-9]{3}$)'
        re_exp_percent = r'(^[ \w_.-]+[_.])(%[0-9]+d)(\.[a-zA-Z0-9]{3}$)'
        match = re.compile(re_exp)

        if self.is_dir and not self.exists:
            # It doesn't exist, so we can't tell if it's a sequence
            if HALT_ON_ERROR:
                raise ValueError(
                    'Cannot determine if non-existent directory {dir} '
                    'contains an image sequence.'.format(
                        dir=self.path,
                    )
                )
            else:
                self._is_seq = False
                self._sequences = []
        elif self.is_dir and self.exists:
            file_list = os.listdir(self.path)
            files = [f for f in file_list if match.search(f)]
            if not files:
                self._is_seq = False
                self._sequences = []
            else:
                seqs = []
                for image in files:
                    found = match.search(image)
                    padding = '#' * len(found.group(2))
                    filename = found.group(1) + padding + found.group(3)
                    if filename not in seqs:
                        seqs.append(filename)
                self._is_seq = True
                self._sequences = seqs
        else:
            found = match.search(self.filename)
            if found:
                padding = '#' * len(found.group(2))
                self._is_seq = True
                self._sequences = [found.group(1) + padding + found.group(3)]
            else:
                # We'll finally check for %d style padding
                match = re.compile(re_exp_percent)
                found = match.search(self.filename)
                if found:
                    self._is_seq = True
                    self._sequences = [self.filename]
                else:
                    self._is_seq = False
                    self._sequences = []

    # =========================================================================

    def _reset_cached_properties(self):
        """Resets cached attributes back to init values"""
        self._is_seq = None
        self._sequences = None

    # =========================================================================

    @staticmethod
    def _split_uri(uri):
        """Splits uri into protocol, base and filename"""
        if ':' in uri:
            protocol = uri.split('://')[0]
            uri = uri.split('://')[1]
        else:
            protocol = ''

        directory = os.path.split(uri)[0]
        ref_file = os.path.split(uri)[1]

        return protocol, directory, ref_file

    # Public Methods ==========================================================

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

        sat : (float)
            The saturation value (to be applied with Rec 709 coefficients) is
            stored here. Saturation is the last operation to be applied when
            applying a CDL.

            sat can be set with a float, int or numeric string.

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
        self._sat = 1.0

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
        # If given as a string, the string must be convertible to a float
        if type(value) in [float, int, str]:
            try:
                value = self._check_single_value(value, 'saturation')
            except (TypeError, ValueError):
                raise
            else:
                self._sat = value
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
        sat = ElementTree.Element('SATNode')
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
    to be a non-valid value, which might result in values not being floats or
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
            An rgb tuple representing the power, which is the only function
            that changes the response curve of the function. Note that this has
            the opposite response to adjustments than a traditional gamma
            operator. These values must be positive. If you set this attribute
            with a single value, it will be copied over all 3 colors. Any
            single value given can be a float, int or numeric string.

            default: (1.0, 1.0, 1.0)

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

        self._slope = [1.0, 1.0, 1.0]
        self._offset = [0.0, 0.0, 0.0]
        self._power = [1.0, 1.0, 1.0]

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
            value : [(str, float, int)]
                A list of three numeric values to be checked.

            name : (str)
                The type of values being checked: slope, offset, etc.

            negative_allow=False : (bool)
                If false, do not allow negative values.

        **Returns:**
            [float, float, float]
                If all values pass all tests, returns values as a list of
                floats.

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
            value : [(str, float, int)] or (str, float, int)
                A list of three (or one) numeric values to be checked.

            name : (str)
                The type of values being checked: slope, offset, etc.

            negative_allow=False : (bool)
                If false, do not allow negative values.

        **Returns:**
            [float, float, float]
                If all values pass all tests, returns values as a list of
                floats.

        **Raises:**
            TypeError:
                If a value given is not a number.

            ValueError:
                If length of list or tuple is not 3 or if negative is False,
                raised if value given is negative.

        """
        if type(value) in [float, int, str]:
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
    """Translates scientific notation into float strings"""
    notation = str(notation)
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


def _sanitize(name):
    """Removes any characters in string name that aren't alnum or in '_.'"""
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

                cdl = ColorCorrection(cc_id, input_file)

                cdl.sat = sat
                cdl.slope = sop_values['slope']
                cdl.offset = sop_values['offset']
                cdl.power = sop_values['power']

                cdls.append(cdl)

    ccc = ColorCollection()
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

    cdl = ColorCorrection(cc_id)
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
        sop_xml = find_required(root, SopNode.element_names)
    except ValueError:
        sop_xml = None
    try:
        sat_xml = find_required(root, SatNode.element_names)
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

    ccc = ColorCollection()
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

    cdl = ColorCollection()
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

        cdl = ColorCorrection(filename, input_file)

        cdl.slope = slope
        cdl.offset = offset
        cdl.power = power
        cdl.sat = sat

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
            col_cor = ColorCorrection(line_id, edl_path)
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
        cdl = build_cc(cc_id, input_file, sop, sat, title)
        cdls.append(cdl)

    ccc = ColorCollection()
    ccc.file_in = input_file
    ccc.append_children(cdls)

    return ccc

# ==============================================================================


def reset_all():
    """Resets all class level member lists and dictionaries"""
    ColorCorrection.reset_members()
    ColorCorrectionReference.reset_members()
    ColorDecision.reset_members()
    ColorCollection.reset_members()
    MediaRef.reset_members()

# ==============================================================================


def sanity_check(colcor):
    """Checks values on :class:`ColorCorrection` for sanity.

    **Args:**
        colcor : (:class:`ColorCorrection`)
            The :class:`ColorCorrection` to check for sane values.

    **Returns:**
        (bool)
            Returns True if all values are sane.

    **Raises:**
        N/A

    Will print a warning to stdout if any values exceed normal limits.
    Normal limits are defined as:

    For Slope, Power and Saturation:
        Any value over 3 or under 0.1

    For Offset:
        Any value over 1 or under -1

    Note that depending on the desired look for a shot or sequence, it's
    possible that a single ColorCorrection element might have very odd
    looking values and still achieve a correct look.

    """
    sane_values = True

    def _check_value(value, minmax, value_type):
        """Checks if a value falls outside of min or max"""
        if value <= minmax[0] or value >= minmax[1]:
            print(
                'The ColorCorrection "{id}" was given a {type} value of '
                '"{value}", which might be incorrect.'.format(
                    id=colcor.id,
                    type=value_type,
                    value=value
                )
            )
            return False
        else:
            return True

    if colcor.has_sop:
        for i in xrange(3):
            slope = _check_value(colcor.slope[i], (0.1, 3.0), 'Slope')
            offset = _check_value(colcor.offset[i], (-1.0, 1.0), 'Offset')
            power = _check_value(colcor.power[i], (0.1, 3.0), 'Power')
            if not slope or not offset or not power:
                sane_values = False

    if colcor.has_sat:
        if not _check_value(colcor.sat, (0.1, 3.0), 'Saturation'):
            sane_values = False

    return sane_values

# ==============================================================================


def write_cc(cdl):
    """Writes the ColorCorrection to a .cc file"""
    with open(cdl.file_out, 'wb') as cdl_f:
        cdl_f.write(cdl.xml_root)

# ==============================================================================


def write_ccc(cdl):
    """Writes the ColorCollection to a .ccc file"""
    cdl.set_to_ccc()
    with open(cdl.file_out, 'wb') as cdl_f:
        cdl_f.write(cdl.xml_root)

# ==============================================================================


def write_rnh_cdl(cdl):
    """Writes the ColorCorrection to a space separated .cdl file"""

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
    'ccc': parse_ccc,
    'cc': parse_cc,
    'cdl': parse_rnh_cdl,
    'flex': parse_flex,
}

OUTPUT_FORMATS = {
    'cc': write_cc,
    'ccc': write_ccc,
    'cdl': write_rnh_cdl,
}

COLLECTION_FORMATS = ['ale', 'ccc', 'flex']
SINGLE_FORMATS = ['cc', 'cdl']

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
             "cannot determine the filetype automatically. Supported input "  # pylint: disable=C0330
             "formats are: "  # pylint: disable=C0330
             "{inputs}".format(inputs=str(INPUT_FORMATS.keys()))  # pylint: disable=C0330
    )
    parser.add_argument(
        "-o",
        "--output",
        help="specify the filetype to convert to, comma separated lists are "
             "accepted. Defaults to a .cc XML. Supported output formats are: "  # pylint: disable=C0330
             "{outputs}".format(outputs=str(OUTPUT_FORMATS.keys()))  # pylint: disable=C0330
    )
    parser.add_argument(
        "-d",
        "--destination",
        help="specify an output directory to save converted files to. If not "
             "provided will default to ./converted/"  # pylint: disable=C0330
    )
    parser.add_argument(
        "--halt",
        action='store_true',
        help="turns off exception handling default behavior. Turn this on if "
             "you want the conversion process to fail and not continue,"  # pylint: disable=C0330
             "rather than relying on default behavior for bad values. Examples "  # pylint: disable=C0330
             "are clipping negative values to 0.0 for Slope, Power and "  # pylint: disable=C0330
             "Saturation, and automatically generating a new id for a "  # pylint: disable=C0330
             "ColorCorrect if no or a bad id is given."  # pylint: disable=C0330
    )
    parser.add_argument(
        "--no-output",
        action='store_true',
        help="parses all incoming files but no files will be written. Use this "
             "in conjunction with '--halt' and '--check' to try and "  # pylint: disable=C0330
             "track down any oddities observed in the CDLs."  # pylint: disable=C0330
    )
    parser.add_argument(
        "--check",
        action='store_true',
        help="checks all ColorCorrects that were parsed for odd values. Odd "
             "values are any values over 3 or under 0.1 for Slope, Power "  # pylint: disable=C0330
             "and Saturation. For offset, any value over 1 and under -1 is "  # pylint: disable=C0330
             "flagged. Note that depending on the look, these still might "  # pylint: disable=C0330
             "be correct values."  # pylint: disable=C0330
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

    if not args.destination:
        args.destination = './converted/'

    if args.halt:
        global HALT_ON_ERROR  # pylint: disable=W0603
        HALT_ON_ERROR = True

    return args

# ==============================================================================


def main():  # pylint: disable=R0912
    """Will figure out input and destination filetypes, then convert"""
    args = parse_args()

    if args.no_output:
        print("Dry run initiated, no files will be written.")

    filepath = os.path.abspath(args.input_file)
    destination_dir = os.path.abspath(args.destination)

    if not os.path.exists(destination_dir):
        print(
            "Destination directory {dir} does not exist.".format(
                dir=destination_dir
            )
        )
        if not args.no_output:
            print("Creating destination directory.")
            os.makedirs(destination_dir)
        else:
            print("--no-output argument provided. Skipping directory creation")

    if not args.input:
        filetype_in = os.path.basename(filepath).split('.')[-1].lower()
    else:
        filetype_in = args.input

    color_decisions = INPUT_FORMATS[filetype_in](filepath)

    def write_single_file(cdl, ext):
        """Writes a single color correction file"""
        cdl.determine_dest(ext, destination_dir)
        print(
            "Writing cdl {id} to {path}".format(
                id=cdl.id,
                path=cdl.file_out
            )
        )
        if not args.no_output:
            OUTPUT_FORMATS[ext](cdl)

    def write_collection_file(col, ext):
        """Writes a collection file"""
        col.type = ext
        col.determine_dest(destination_dir)
        print(
            "Writing collection to {path}".format(
                path=col.file_out
            )
        )
        if not args.no_output:
            OUTPUT_FORMATS[ext](col)

    if color_decisions:
        # Sanity Check
        if args.check:
            if filetype_in in COLLECTION_FORMATS:
                for color_correct in color_decisions.color_corrections:
                    sanity_check(color_correct)
            else:
                sanity_check(color_decisions)

        # Writing
        for ext in args.output:
            if ext in SINGLE_FORMATS:
                if filetype_in in COLLECTION_FORMATS:
                    for color_correct in color_decisions.color_corrections:
                        write_single_file(color_correct, ext)
                else:
                    write_single_file(color_decisions, ext)
            else:
                if filetype_in in COLLECTION_FORMATS:
                    # If we read a collection type, color_decisions is
                    # already a ColorCollection.
                    write_collection_file(color_decisions, ext)
                else:
                    # If we read a single, non-collection file, we need to
                    # create a collection for exporting.
                    #
                    # Since we only read a single file, we can safely use that
                    # filepath as the input_file.
                    #
                    # If we read a group of files, we would want to default to
                    # the generic collection naming.
                    collection = ColorCollection(input_file=filepath)
                    collection.append_child(color_decisions)
                    write_collection_file(collection, ext)

if __name__ == '__main__':  # pragma: no cover
    try:
        main()
    except Exception as err:  # pylint: disable=W0703
        import traceback
        print('Unexpected error encountered:')
        print(err)
        print(traceback.format_exc())
        raw_input('Press enter key to exit')
