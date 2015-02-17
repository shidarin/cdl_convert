#!/usr/bin/env python
"""

CDL Convert Decision
====================

Contains the ColorDecision class and it's unique child classes,
ColorCorrectionRef and MediaRef.

## Classes

    ColorCorrectionRef

        This class contains a reference to a ColorCorrection. The reference
        should be a reference to an existing ColorCorrection, but this is
        not enforced explicitly unless config.HALT_ON_ERROR is set and you
        try and retrieve the referenced Correction.

        Should be contained only within a ColorDecision

    ColorDecision

        A simple container format. Requires a ColorCorrection or a
        ColorCorrectionRef, and may also contain an optional MediaRef. This
        should only be contained within a ColorCollection.

        ColorDecisions are used to link a ColorCorrection with one or several
        pieces of reference media, as represented by MediaRef. A single
        ColorCorrection may be referenced and 'contained' within many different
        ColorDecisions so that a single ColorCorrection can be linked with many
        different MediaRefs

    MediaRef

        Contains a single uri path to a peice of reference media. This class
        contains many attributes and helper methods for dealing with media
        reference, which should let a user do the following and more:

            * Change refs to be absolute or relative
            * Change refs to be in a new directory
            * Determine if a ref exists on disk
            * Determine if a ref is an image sequence
            * If a directory, find all files and sequences within.

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

import os
import re
from xml.etree import ElementTree

# cdl_convert imports

from .base import AscColorSpaceBase, AscDescBase, AscXMLBase
from . import config
from .correction import ColorCorrection

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'ColorCorrectionRef',
    'ColorDecision',
    'MediaRef'
]

# ==============================================================================
# CLASSES
# ==============================================================================


class ColorCorrectionRef(AscXMLBase):
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

        members : {str: [:class`ColorCorrectionRef` ]}
            All instanced :class:`ColorCorrectionRef` are added to this
            member dictionary. Multiple :class:`ColorCorrectionRef` can
            share the same reference id, therefore for each reference id key,
            the members dictionary stores a list of
            :class:`ColorCorrectionRef` instances that share that ``id``
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
        super(ColorCorrectionRef, self).__init__()
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
        if ref_id not in ColorCorrection.members and config.HALT_ON_ERROR:
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
        if self.id in ColorCorrectionRef.members:
            ColorCorrectionRef.members[self.id].remove(self)
            # If the remaining list is empty, we'll pop it out
            if not ColorCorrectionRef.members[self.id]:
                ColorCorrectionRef.members.pop(self.id)

        # Check if this id is already registered
        if new_ref in ColorCorrectionRef.members:
            ColorCorrectionRef.members[new_ref].append(self)
        else:
            ColorCorrectionRef.members[new_ref] = [self]

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
            if config.HALT_ON_ERROR:
                raise ValueError(
                    "Cannot resolve ColorCorrectionRef with reference "
                    "id of '{id}' because no ColorCorrection with that id "
                    "can be found.".format(id=self.id)
                )
            else:
                return None

# ==============================================================================


class ColorDecision(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0903
    """Contains a media ref and a ColorCorrection or reference to CC.

    Description
    ~~~~~~~~~~~

    This class is a simple container to link a :class:`ColorCorrection` (or
    :class:`ColorCorrectionRef` ) with a :class:`MediaRef` . The
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

        members : {str: [ :class`ColorDecision` ]}
            All instanced :class:`ColorDecision` are added to this
            member dictionary. The key is the id or reference id of the
            contained :class:`ColorCorrection` or
            :class:`ColorCorrectionRef` Multiple :class:`ColorDecision`
            can , therefore for each reference id key,
            the members dictionary stores a list of
            :class:`ColorDecision` instances that share that ``id``
            value.

    **Attributes:**

        cc : (:class:`ColorCorrection` , :class:`ColorCorrectionRef`)
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
            True if contains a :class:`ColorCorrectionRef` object instead
            of a :class:`ColorCorrection`

        media_ref : (:class:`MediaRef`)
            Returns the contained :class:`MediaRef` or None.

        parent : (:class:`ColorDecisionList`)
            The parent node that contains this node.

        set_parentage()
            Sets child :class:`ColorCorrection` (or
            :class:`ColorCorrectionRef`) and :class:`MediaRef` (if
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

        if self.cc:
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
        return type(self.cc) is ColorCorrectionRef

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

    def build_element(self, resolve=False):  # pylint: disable=W0221
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

        # The resolve arg should only be applied to reference color decisions.
        #
        # Our behavior for non-reference CDs is the same as our behavior
        # for non-resolving.
        if not resolve or not self.is_ref:
            cd_xml.append(self.cc.element)
        elif resolve:
            # We're a reference and we need to be resolved
            # Note that this will raise an exception if called when a reference
            # cannot be resolve due to a non-existent ColorCorrection.
            cd_xml.append(self.cc.cc.element)

        return cd_xml

    # =========================================================================

    def parse_xml_color_correction(self, xml_element):
        """Parses a Color Decision element to find a ColorCorrection"""
        cc_elem = xml_element.find('ColorCorrection')
        if cc_elem is None:
            # Perhaps we're a ColorCorrectionRef?
            cc_elem = xml_element.find('ColorCorrectionRef')
            if cc_elem is None:
                # No ColorCorrection or CCRef? This is a bad ColorDecision
                return False
            else:
                # Parse the ColorCorrectionRef
                ref_id = cc_elem.attrib['ref']
                self.cc = ColorCorrectionRef(ref_id)  # pylint: disable=C0103
                self.cc.parent = self
        else:
            from . import parse
            # Parse the ColorCorrection
            self.cc = parse.parse_cc(cc_elem)
            self.cc.parent = self

        return True

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
                'ColorCorrectionRef node, but neither was found.'
            )

        # Grab our MediaRef (if found)
        self.parse_xml_media_ref(xml_element)

    # =========================================================================

    def parse_xml_media_ref(self, xml_element):
        """Parses a Color Decision element to find a MediaRef"""
        media_ref_elem = xml_element.find('MediaRef')
        if media_ref_elem is not None:
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
    restriction is not enforced in the python API.

    **Class Attributes:**

        members : {str: [ :class:`MediaRef` ]}
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
            if config.HALT_ON_ERROR:
                raise ValueError(
                    'Cannot determine if non-existent directory {dir} '
                    'contains an image sequence.'.format(dir=self.path)
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
        if '://' in uri:
            protocol = uri.split('://')[0]
            uri = uri.split('://')[1]
        else:
            protocol = ''

        directory = os.path.split(uri)[0]
        ref_file = os.path.split(uri)[1]

        return protocol, directory, ref_file

    # Public Methods ==========================================================

    def build_element(self):
        """Builds an ElementTree XML element representing this reference"""
        media_ref_xml = ElementTree.Element('MediaRef')
        media_ref_xml.attrib = {'ref': self.ref}

        return media_ref_xml

    # =========================================================================

    @classmethod
    def reset_members(cls):
        """Resets the class level members dictionary"""
        cls.members = {}
