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

Classes
-------

ColorCorrection
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
__version__ = "0.6"
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

# HALT_ON_ERROR is the exception handling variable for exceptions that can
# be handled silently.
# Used in the following places:
#   Slope, power and sat values can't be negative and will truncate to 0.0
#   If id given to ColorCorrection is blank, will set to number of CCs
#   When determining if a non-existent directory referenced by MediaRef
#       contains an image sequence, will just return False.
HALT_ON_ERROR = False

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'AscColorSpaceBase',
    'AscDescBase',
    'ColorCollectionBase',
    'ColorCorrection',
    'ColorDecision',
    'ColorNodeBase',
    'MediaRef',
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


class AscColorSpaceBase(object):  # pylint: disable=R0903
    """Base class for Asc XML type nodes that deal with colorspace

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

    """
    def __init__(self):
        super(AscXMLBase, self).__init__()

    # Properties ==============================================================

    @property
    def element(self):
        return self.build_element()

    @property
    def xml(self):
        # We'll take the xml_root attrib, which is ready to write, and just
        # remove the first line, which is the xml version and encoding.
        dom_string = self.xml_root.split('\n')
        return '\n'.join(dom_string[1:])

    @property
    def xml_root(self):
        xml_string = ElementTree.tostring(self.element, 'UTF-8')
        dom_xml = minidom.parseString(xml_string)
        dom_string = dom_xml.toprettyxml(indent="    ", encoding='UTF-8')
        return dom_string

    # Public Methods ==========================================================

    def build_element(self):
        """Placeholder for reference by attributes. Will return None"""
        return None

# ==============================================================================


class ColorCollectionBase(AscDescBase, AscColorSpaceBase):  # pylint: disable=R0903
    """Base class for ColorDecisionList and ColorCorrectionCollection.

    Collections need to store children and have access to descriptions,
    input descriptions, and viewing descriptions.

    Inherits desc attribute and setters from :class:`AscDescBase`

    Inherits input_desc and viewing_desc from :class:`AscColorSpaceBase`

    **Attributes:**

        input_desc : (str)
            Description of the color space, format and properties of the input
            images. Individual :class:`ColorCorrections` can override this.

        viewing_desc : (str)
            Viewing device, settings and environment. Individual
            :class:`ColorCorrections` can override this.

    """
    def __init__(self):
        super(ColorCollectionBase, self).__init__()

# ==============================================================================


class ColorCorrection(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0902
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

    Inherits ``desc`` attribute and setters from :class:`AscDescBase`

    Inherits ``input_desc`` and ``viewing_desc`` from
    :class:`AscColorSpaceBase`

    Inherits ``element``, ``xml`` and ``xml_root`` from :class:`AscXMLBase`

    **Class Attributes:**

        members : {str: :class`ColorCorrection`}
            All instanced :class:`ColorCorrection` are added to this member
            dictionary, with their unique id being the key and the
            :class:`ColorCorrection` being the value.

    **Attributes:**

        file_in : (str)
            Filepath used to create this CDL.

        file_out : (str)
            Filepath this CDL will be written to.

        id : (str)
            Unique XML URI to identify this CDL. Often a shot or sequence name.

            Changing this value does a check against the cls.members dictionary
            to ensure the new id is open. If it is, the key is changed to the
            new id and the id is changed.

            Note that this shadows the builtin id.

        sat_node : ( :class:`SatNode` )
            Contains a reference to a single instance of :class:`SatNode` ,
            which contains the saturation value and descriptions.

        sop_node : ( :class:`SopNode` )
            Contains a reference to a single instance of :class:`SopNode` ,
            which contains the slope, offset, power values and descriptions.

    """

    members = {}

    def __init__(self, id, cdl_file):  # pylint: disable=W0622
        """Inits an instance of a ColorCorrection"""
        super(ColorCorrection, self).__init__()

        # File Attributes
        self._files = {
            'file_in': os.path.abspath(cdl_file),
            'file_out': None
        }

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
        self.sat_node = None

        # ASC_SOP attributes
        self.sop_node = None

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
        cc = ElementTree.Element('ColorCorrection')
        cc.attrib = {'id': self.id}
        if self.input_desc:
            input_desc = ElementTree.SubElement(cc, 'InputDescription')
            input_desc.text = self.input_desc
        if self.viewing_desc:
            viewing_desc = ElementTree.SubElement(cc, 'ViewingDescription')
            viewing_desc.text = self.viewing_desc
        for description in self.desc:
            desc = ElementTree.SubElement(cc, 'Description')
            desc.text = description
        if self.sop_node:
            cc.append(self.sop_node.element)
        if self.sat_node:
            cc.append(self.sat_node.element)

        return cc

    def determine_dest(self, output):
        """Determines the destination file and sets it on the cdl"""

        directory = os.path.dirname(self.file_in)

        filename = "{id}.{ext}".format(id=self.id, ext=output)

        self._files['file_out'] = os.path.join(directory, filename)

# ==============================================================================


class ColorDecision(AscDescBase, AscColorSpaceBase):  # pylint: disable=R0903
    """Contains a media ref and a ColorCorrection or reference to CC"""
    def __init__(self):
        """Inits an instance of ColorDecision"""
        super(ColorDecision, self).__init__()

# ==============================================================================


class ColorNodeBase(AscDescBase, AscXMLBase):  # pylint: disable=R0903
    """Base class for SOP and SAT nodes.

    Inherits ``desc`` from :class:`AscDescBase`

    Inherits ``element``, ``xml`` and ``xml_root`` from :class:`AscXMLBase`

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


class MediaRef(object):
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

    """

    members = {}

    def __init__(self, ref_uri, parent=None):
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

    def _get_sequences(self):
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

# ==============================================================================


class SatNode(ColorNodeBase):
    """Color node that contains saturation data.

    **Class Attributes:**

        element_names : [str]
            Contains a list of XML Elements that refer to this class for use
            in parsing XML files.

    **Attributes:**

        parent : ( :class:`ColorCorrection` )
            The parent :class:`ColorCorrection` instance that created this
            instance.

        sat : (float)
            The saturation value (to be applied with Rec 709 coefficients) is
            stored here. Saturation is the last operation to be applied when
            applying a CDL.

            sat can be set with a float, int or numeric string.

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
        op_node.text = str(self.sat)
        return sat

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
        for i, op in enumerate([self.slope, self.offset, self.power]):
            op_node = ElementTree.SubElement(sop, fields[i])
            op_node.text = '{valueR} {valueG} {valueB}'.format(
                valueR=str(op[0]),
                valueG=str(op[1]),
                valueB=str(op[2])
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


def parse_ale(edl_file):
    """Parses an Avid Log Exchange (ALE) file for CDLs

    **Args:**
        file : (str)
            The filepath to the ALE EDL

    **Returns:**
        [:class:`ColorCorrection`]
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

                cdl = ColorCorrection(cc_id, edl_file)

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
        [:class:`ColorCorrection`]
            A list of CDL objects retrieved from the CC

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
    root = ElementTree.parse(cdl_file).getroot()

    cdls = []

    if not root.tag == 'ColorCorrection':
        # This is not a CC file...
        raise ValueError('CC parsed but no ColorCorrection found')

    try:
        cc_id = root.attrib['id']
    except KeyError:
        raise ValueError('No id found on ColorCorrection')

    cdl = ColorCorrection(cc_id, cdl_file)

    # Grab our descriptions and add them to the cdl
    cdl.parse_xml_descs(root)
    # See if we have a viewing description.
    cdl.parse_xml_viewing_desc(root)
    # See if we have an input description
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

    cdls.append(cdl)

    return cdls

# ==============================================================================


def parse_cdl(cdl_file):
    """Parses a space separated .cdl file for ASC CDL information.

    **Args:**
        file : (str)
            The filepath to the CDL

    **Returns:**
        [:class:`ColorCorrection`]
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

        cdl = ColorCorrection(filename, cdl_file)

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
        [:class:`ColorCorrection`]
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
                    cdl = build_cc(cc_id, edl_file, sop, sat, title)
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
        cdl = build_cc(cc_id, edl_file, sop, sat, title)
        cdls.append(cdl)

    return cdls

# ==============================================================================


def write_cc(cdl):
    """Writes the ColorCorrection to a .cc file"""

    xml = CC_XML.format(
        id=cdl.id,
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
                        id=cdl.id,
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
