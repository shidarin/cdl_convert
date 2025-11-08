#!/usr/bin/env python
"""CDL Convert Collection Module

This module contains the ColorCollection class, which serves as a unified
container for both ColorCorrectionCollection and ColorDecisionList formats,
providing seamless conversion between ASC CDL collection types.

Classes:
    ColorCollection: Collection container for ColorCorrections and 
        ColorDecisions with support for both CCC and CDL export formats.

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
from typing import List, Optional, Union, Any, Tuple
from xml.etree import ElementTree

# cdl_convert imports

from .base import AscColorSpaceBase, AscDescBase, AscXMLBase
from . import config
from .correction import ColorCorrection
from .decision import ColorDecision
from .exceptions import ValidationError

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = ['ColorCollection']

# ==============================================================================
# CLASSES
# ==============================================================================


class ColorCollection(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0902,R0904
    """Container class for ColorDecisionLists and ColorCorrectionCollections.

    ColorCollection stores child ColorCorrection and ColorDecision objects and 
    can export them as either ColorCorrectionCollection (.ccc) or 
    ColorDecisionList (.cdl) XML formats. It inherits description, colorspace,
    and XML functionality from base classes.

    Example:
        >>> collection = ColorCollection()
        >>> cc = ColorCorrection("shot_001")
        >>> collection.append_child(cc)
        >>> collection.set_to_ccc()
        >>> print(collection.type)  # 'ccc'

    """

    members: List['ColorCollection'] = []
    """All ColorCollection instances are tracked in this list. Used for 
    generating default filenames when no input file is set."""

    def __init__(self, input_file: Optional[Union[str, Path]] = None) -> None:
        super(ColorCollection, self).__init__()

        self._color_corrections: List[ColorCorrection] = []
        self._color_decisions: List[ColorDecision] = []
        self._file_in: Optional[Path] = Path(input_file).resolve() if input_file else None
        self._file_out: Optional[Path] = None
        self._type: str = 'ccc'
        self._xmlns: str = "urn:ASC:CDL:v1.01"

        ColorCollection.members.append(self)

    # Properties ==============================================================

    @property
    def all_children(self) -> List[Union[ColorCorrection, ColorDecision]]:
        """Return combined list of ColorCorrection and ColorDecision."""
        return self.color_corrections + self.color_decisions

    @property
    def color_corrections(self) -> List[ColorCorrection]:
        """Return list of ColorCorrection children."""
        return self._color_corrections

    @color_corrections.setter
    def color_corrections(self, values: Union[None, ColorCorrection, List[ColorCorrection], Tuple[ColorCorrection, ...], set]) -> None:
        """Set color_corrections list, ensuring all items are ColorCorrection instances."""
        self._color_corrections = self._list_setter(
            'color_corrections', ColorCorrection, values
        )

    @property
    def color_decisions(self) -> List[ColorDecision]:
        """Return list of ColorDecision children."""
        return self._color_decisions

    @color_decisions.setter
    def color_decisions(self, values: Union[None, ColorDecision, List[ColorDecision], Tuple[ColorDecision, ...], set]) -> None:
        """Set color_decisions list, ensuring all items are ColorDecision."""
        self._color_decisions = self._list_setter(
            'color_decisions', ColorDecision, values
        )

    @property
    def file_in(self) -> Optional[Path]:
        """Return absolute path to the input file."""
        return self._file_in

    @file_in.setter
    def file_in(self, value: Optional[Union[str, Path]]) -> None:
        """Set file_in to absolute path of the provided file."""
        if value:
            self._file_in = Path(value).resolve()

    @property
    def file_out(self) -> Optional[Path]:
        """Return output file path for writing this collection."""
        return self._file_out

    @property
    def id_list(self) -> List[str]:
        """Return sorted list of IDs from all ColorCorrection children."""
        current_ids = [i.cc.id for i in self.color_decisions if not i.is_ref]
        current_ids.extend([i.id for i in self.color_corrections])
        current_ids.sort()
        return current_ids

    @property
    def is_ccc(self) -> bool:
        """Return True if collection type is set to 'ccc'."""
        return self.type == 'ccc'

    @property
    def is_cdl(self) -> bool:
        """Return True if collection type is set to 'cdl'."""
        return self.type == 'cdl'

    @property
    def type(self) -> str:
        """Return collection type that determines export format."""
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        """Set collection type to 'ccc' or 'cdl'."""
        if value.lower() not in ['ccc', 'cdl']:
            raise ValidationError(
                'ColorCollection type must be set to either '
                'ccc or cdl.'
            )
        else:
            self._type = value.lower()

    @property
    def xmlns(self) -> str:
        """Return XML namespace URI for ASC CDL schema version."""
        return self._xmlns

    # Private Methods =========================================================

    @staticmethod
    def _list_setter(list_name: str, color_class: type, values: Union[None, Any, List[Any], Tuple[Any, ...], set]) -> List[Any]:
        """Set list to provided values after validating."""
        if values is None:
            return []
        elif type(values) in [list, tuple, set]:
            for color in values:
                # We need to make sure each member is of the correct class.
                if color.__class__ != color_class:
                    raise ValidationError(
                        f"ColorCollection().{list_name} cannot be set to "
                        f"provided list because not all members of that list "
                        f"are of the {color_class.__name__} class."
                    )
            return list(set(values))
        elif values.__class__ == color_class:
            # If we just got passed the correct class, we'll return it as a
            # one member list.
            return [values]
        else:
            raise ValidationError(
                f"ColorCollection().{list_name} cannot be set to item "
                f"of type '{type(values)}'. Please set {list_name} with a "
                f"list containing only members of class {color_class.__name__}."
            )

    # Public Methods ==========================================================

    def append_child(self, child: Union[ColorCorrection, ColorDecision]) -> bool:
        """Add a ColorCorrection or ColorDecision to the appropriate list.
        
        Args:
            child: ColorCorrection or ColorDecision instance to add.
            
        Returns:
            bool: True if child was added successfully, False if duplicate ID
                prevented addition.
            
        Raises:
            ValidationError: If child is not a ColorCorrection or
                ColorDecision, or if duplicate ID is found and halt_on_error
                is enabled.

        """
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

            raise ValidationError(
                "Can only append ColorCorrection and "
                "ColorDecision objects."
            )

        if dup:
            if config.config.halt_on_error:
                raise ValidationError(
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

    def append_children(self, children: List[Union[ColorCorrection, ColorDecision]]) -> None:
        """Add multiple ColorCorrection and ColorDecision objects to lists.
        
        Args:
            children: List of ColorCorrection and/or ColorDecision instances
                to add.

        """
        for child in children:
            self.append_child(child)

    # =========================================================================

    def build_element(self) -> Optional[ElementTree.Element]:
        """Build XML ElementTree Element based on current collection type.
        
        Returns:
            ElementTree.Element: CCC or CDL format XML element depending on
                type.

        """
        if self.is_ccc:
            return self.build_element_ccc()
        elif self.is_cdl:
            return self.build_element_cdl()

    # =========================================================================

    def build_element_ccc(self) -> ElementTree.Element:
        """Build ColorCorrectionCollection XML element.
        
        Returns:
            ElementTree.Element: CCC format XML element containing all
                ColorCorrections.

        """
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

    def build_element_cdl(self) -> ElementTree.Element:
        """Build ColorDecisionList XML element.
        
        Returns:
            ElementTree.Element: CDL format XML element containing all
                ColorDecisions.

        """
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

    def copy_collection(self) -> 'ColorCollection':
        """Create a copy of this collection with the same attributes.
        
        Returns:
            ColorCollection: New collection instance with copied attributes
                and child references.
            
        Note:
            Child objects are referenced, not deep copied.
        
        """
        # TODO: Add deep copy ability
        new_col = ColorCollection()
        new_col.desc = self.desc
        new_col.file_in = self.file_in if self.file_in else None
        new_col.input_desc = self.input_desc
        new_col.viewing_desc = self.viewing_desc
        new_col.type = self.type
        new_col.append_children(self.all_children)
        return new_col

    # =========================================================================

    def determine_dest(self, directory: Union[str, Path]) -> None:
        """Set output file path based on input filename or collection index.
        
        Args:
            directory: Directory path where output file will be written.

        """
        if self.file_in:
            filename = Path(self.file_in).stem
        else:
            filename = f'color_collection_{str(ColorCollection.members.index(self)).rjust(3, "0")}'

        filename = f"{filename}.{self.type}"

        self._file_out = Path(directory) / filename

    # =========================================================================

    def merge_collections(self, collections: List['ColorCollection']) -> 'ColorCollection':
        """Merge collection with others to create a new combined collection.
        
        Args:
            collections: List of ColorCollection instances to merge with.
            
        Returns:
            ColorCollection: New collection containing children from all input
                collections, with duplicates removed and attributes from this
                collection preserved.

        """
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

    def parse_xml_color_corrections(self, xml_element: ElementTree.Element) -> bool:
        """Parse XML element to find and add ColorCorrection elements.

        Args:
            xml_element: XML element to search for ColorCorrection child
                elements.

        Returns:
            bool: True if ColorCorrection elements were found and added.

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

    def parse_xml_color_decisions(self, xml_element: ElementTree.Element) -> bool:
        """Parse XML element to find and add ColorDecision elements.

        Args:
            xml_element: XML element to search for ColorDecision child
                elements.

        Returns:
            bool: True if ColorDecision elements were found and added.
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
    def reset_members(cls) -> None:
        """Clear the class-level members list."""
        cls.members = []

    # =========================================================================

    def set_parentage(self) -> None:
        """Set the parent attribute of all child objects to this collection."""
        for node in self.all_children:
            node.parent = self

    # =========================================================================

    def set_to_ccc(self) -> None:
        """Set collection type to 'ccc' for ColorCorrectionCollection."""
        self._type = 'ccc'

    # =========================================================================

    def set_to_cdl(self) -> None:
        """Set collection type to 'cdl' for ColorDecisionList format."""
        self._type = 'cdl'
