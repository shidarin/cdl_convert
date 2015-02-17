#!/usr/bin/env python
"""

CDL Convert Collection
======================

Contains the ColorCollection class, which acts as both
ColorCorrectionCollection and ColorDecisionList.

## Classes

    ColorCollection
        Collection format for both ColorCorrections and ColorDecisions. This
        class can export both ColorCorrectionCollection and ColorDecisionList
        formats.

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
from xml.etree import ElementTree

# cdl_convert imports

from .base import AscColorSpaceBase, AscDescBase, AscXMLBase
from . import config
from .correction import ColorCorrection
from .decision import ColorDecision

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = ['ColorCollection']

# ==============================================================================
# CLASSES
# ==============================================================================


class ColorCollection(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0902,R0904
    """Container class for ColorDecisionLists and ColorCorrectionCollections.

    Description
    ~~~~~~~~~~~

    Collections need to store children and have access to descriptions,
    input descriptions, and viewing descriptions.

    **Class Attributes:**

        members : [ :class`ColorCollection` ]
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
    def id_list(self):
        """A list of the ids of fully qualified ColorCorrection children"""
        current_ids = [i.cc.id for i in self.color_decisions if not i.is_ref]
        current_ids.extend([i.id for i in self.color_corrections])
        current_ids.sort()
        return current_ids

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
        # We need to make sure not to append a ColorDecision or ColorCorrection
        # if that id attribute already exists as a direct child or a child of a
        # ColorDecision child.
        #
        # This is only possible through the python API- assigning
        # the same ColorCorrection object to multiple ColorDecisions,
        # or clearing the member dictionary and creating a second
        # ColorCorrection with the same id, etc.
        dup = False

        if child.__class__ == ColorCorrection:
            if child.id in self.id_list:
                dup = True
            else:
                self._color_corrections.append(child)

        elif child.__class__ == ColorDecision:
            if not child.is_ref and child.cc.id in self.id_list:
                dup = True
            else:
                self._color_decisions.append(child)
        else:

            raise TypeError("Can only append ColorCorrection and "
                            "ColorDecision objects.")

        if dup:
            if config.HALT_ON_ERROR:
                raise ValueError(
                    "Attempted to put a ColorDecision with a child "
                    "ColorCorrection id that duplicates an id of a "
                    "ColorCorrection that is already a child of "
                    "this collection or a ColorDecision that is a "
                    "child of this collection."
                )
            return False
        else:
            child.parent = self
            return True

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
        elif self.is_cdl:
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
        if self.color_corrections:
            for color_correct in self.color_corrections:
                ccc_xml.append(color_correct.element)
        if self.color_decisions:
            # We'll need to extract the ColorCorrections from the
            # ColorDecisions
            for color_decision in self.color_decisions:
                if color_decision.is_ref:
                    color_correction = color_decision.cc.cc
                else:
                    color_correction = color_decision.cc

                # We do one last check to ensure that we actually have a
                # returned ColorCorrection, as ColorCorrectionRef will
                # return None if it's an unresolved reference and no
                # HALT behavior was set.
                if color_correction:
                    ccc_xml.append(color_correction.element)

        return ccc_xml

    # =========================================================================

    def build_element_cdl(self):
        """Builds a CDL XML element representing this ColorCollection"""
        cdl_xml = ElementTree.Element('ColorDecisionList')
        cdl_xml.attrib = {'xmlns': self.xmlns}
        if self.input_desc:
            input_desc = ElementTree.SubElement(cdl_xml, 'InputDescription')
            input_desc.text = self.input_desc
        if self.viewing_desc:
            viewing_desc = ElementTree.SubElement(cdl_xml, 'ViewingDescription')
            viewing_desc.text = self.viewing_desc
        for description in self.desc:
            desc = ElementTree.SubElement(cdl_xml, 'Description')
            desc.text = description
        if self.color_decisions:
            for color_decision in self.color_decisions:
                if color_decision.cc.id in self.id_list:
                    resolve = False
                else:
                    try:
                        color_correction = color_decision.cc.cc
                    except ValueError:
                        # ValueError will be raised if we can't resolve the
                        # reference. This shouldn't be a game-stopper here.
                        #
                        # We'll just add the unresolved reference
                        resolve = False
                    else:
                        resolve = True if color_correction else False

                cdl_xml.append(color_decision.build_element(resolve=resolve))

        if self.color_corrections:
            # We'll create some temporary ColorDecision instances, and place
            # the ColorCorrects inside of them.
            #
            # We need to store the ColorDecision member dictionary, so that
            # we can return it to the state it was in prior to us creating
            # these temporary ColorDecisions
            color_decisions_members = ColorDecision.members

            for color_correction in self.color_corrections:
                color_decision = ColorDecision(color_correction)
                cdl_xml.append(color_decision.element)

            # Now reset the ColorDecision member dictionary to the state it was
            # in prior to us creating temp ColorDecisions
            ColorDecision.members = color_decisions_members

        return cdl_xml

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
        from . import parse
        cc_nodes = xml_element.findall('ColorCorrection')
        if not cc_nodes:
            return False

        for cc_node in xml_element.findall('ColorCorrection'):
            cdl = parse.parse_cc(cc_node)
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
