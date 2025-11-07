#!/usr/bin/env python
"""CDL Convert Base Classes Module

This module provides foundational base classes that implement common functionality
shared across CDL Convert components. The classes listed here should only be used
for inheritance by more specialized classes.

Classes:
    AscColorSpaceBase: Base class for ASC XML nodes handling colorspace
        metadata with type hints and enhanced validation. Provides standardized
        input and viewing colorspace description management.

    AscDescBase: Type-safe base class for ASC XML nodes supporting multiple
        descriptions with enhanced list management. Handles unlimited 
        description elements per ASC CDL specifications.

    AscXMLBase: Base class for XML element generation.

    ColorNodeBase: Base class for color correction nodes (SOP/SAT).

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
from decimal import Decimal
import re
from typing import List, Optional, Union, Any
from xml.dom import minidom
from xml.etree import ElementTree

# Secure XML parsing
import defusedxml
defusedxml.defuse_stdlib()

# cdl_convert Imports
from . import config
from .exceptions import ValidationError
from .utils import to_decimal

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'AscColorSpaceBase',
    'AscDescBase',
    'AscXMLBase',
    'ColorNodeBase'
]

# ==============================================================================
# CLASSES
# ==============================================================================


class AscColorSpaceBase(object):  # pylint: disable=R0903
    """Base class for ASC XML type nodes that deal with colorspace.

    This class is meant to be inherited by any node type that uses viewing and
    input colorspace descriptions. It provides standardized handling of
    colorspace metadata according to ASC CDL specifications.

    Attributes:
        input_desc (Optional[str]): Description of the color space, format and 
            properties of the input images. Individual ColorCorrections can 
            override this. Defaults to None.
        viewing_desc (Optional[str]): Viewing device, settings and environment. 
            Individual ColorCorrections can override this. Defaults to None.

    Example:
        >>> class MyColorNode(AscColorSpaceBase):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.input_desc = "Rec.709 Linear"
        ...         self.viewing_desc = "sRGB Display"

    """
    def __init__(self) -> None:
        # For multiple inheritance support.
        super(AscColorSpaceBase, self).__init__()

        self.input_desc: Optional[str] = None
        self.viewing_desc: Optional[str] = None

    # Public Methods ==========================================================

    def parse_xml_input_desc(self, xml_element: ElementTree.Element) -> bool:
        """Parse an ElementTree element to find and add an input description.

        Args:
            xml_element (ElementTree.Element): The XML element to parse for an 
                InputDescription element. If found, sets the input_desc
                attribute.

        Returns:
            bool: True if InputDescription element was found (even if blank),

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

    def parse_xml_viewing_desc(self, xml_element: ElementTree.Element) -> bool:
        """Parse an ElementTree element to find and add a viewing description.

        Args:
            xml_element (ElementTree.Element): The XML element to parse for a 
                ViewingDescription element. If found, sets the viewing_desc
                attribute.

        Returns:
            bool: True if ViewingDescription element was found (even if blank),
                False otherwise.

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
    """Base class for ASC XML type nodes that support multiple descriptions.

    This class is meant to be inherited by any node type that uses description
    fields. It provides standardized handling of multiple description elements
    as specified in the ASC CDL schema.

    Attributes:
        desc (List[str]): List of description strings. Since ASC nodes can
            contain multiple description elements, this attribute stores all
            descriptions found during parsing. Setting desc directly will:
            - Append single values to the end of the list
            - Replace the list when given a list or tuple
            - Empty the list when given None, [], or ()

    Example:
        >>> node = AscDescBase()
        >>> node.desc = "First description"
        >>> node.desc = "Second description"  
        >>> print(node.desc)
        ['First description', 'Second description']
        >>> node.desc = ["New list", "of descriptions"]
        >>> print(node.desc)
        ['New list', 'of descriptions']
        >>> node.desc = None  # Clear descriptions
        >>> print(node.desc)
        []

    """
    def __init__(self) -> None:
        super(AscDescBase, self).__init__()
        self._desc: List[str] = []

    # Properties ==============================================================

    @property
    def desc(self) -> List[str]:
        """Returns the list of descriptions"""
        return self._desc

    @desc.setter
    def desc(self, value: Union[None, str, List[str], tuple]) -> None:
        """Adds an entry to the descriptions"""
        if value is None:
            self._desc = []
        elif type(value) in [list, tuple]:
            self._desc = list(value)
        else:
            self._desc.append(value)

    # Public Methods ==========================================================

    def parse_xml_descs(self, xml_element: ElementTree.Element) -> None:
        """Parse an ElementTree element to find and add any descriptions.

        Args:
            xml_element (ElementTree.Element): The XML element to parse for 
                Description elements. Any found will be appended to the desc
                list.

        Example:
            >>> import xml.etree.ElementTree as ET
            >>> node = AscDescBase()
            >>> xml = ET.fromstring('''
            ... <root>
            ...     <Description>First description</Description>
            ...     <Description>Second description</Description>
            ... </root>
            ... ''')
            >>> node.parse_xml_descs(xml)
            >>> print(node.desc)
            ['First description', 'Second description']
        """
        for desc_entry in xml_element.findall('Description'):
            if desc_entry.text:  # Don't attend if text returns none
                self.desc.append(desc_entry.text)

# ==============================================================================


class AscXMLBase(object):
    """Base class for nodes which can be converted to XML Elements.

    This class provides convenience attributes and methods for converting
    CDL objects to XML representations. 

    Attributes:
        element (Optional[ElementTree.Element]): ElementTree Element 
            representing the node. 
        xml (str): A nicely formatted XML string representing the node,
            without XML declaration header.
        xml_root (str): A nicely formatted XML string with XML declaration
            header, ready to write to file.

    Example:
        >>> class MyNode(AscXMLBase):
        ...     def build_element(self):
        ...         import xml.etree.ElementTree as ET
        ...         return ET.Element('MyNode')
        >>> node = MyNode()
        >>> print(node.xml)  # Pretty-formatted XML without header
        >>> print(node.xml_root)  # With XML declaration

    Note:
        Subclasses must override build_element() to return a valid
        ElementTree.Element for the XML-related attributes to work.

    """
    def __init__(self) -> None:
        super(AscXMLBase, self).__init__()

    # Properties ==============================================================

    @property
    def element(self) -> Optional[ElementTree.Element]:
        """etree style Element representing the node."""
        return self.build_element()

    @property
    def xml(self) -> str:
        """A nicely formatted XML string representing the node"""
        # We'll take the xml_root attrib, which is ready to write, and just
        # remove the first line, which is the xml version and encoding.
        dom_string = self.xml_root.split('\n')
        return '\n'.join(dom_string[1:])

    @property
    def xml_root(self) -> str:
        """A nicely formatted XML string with a root element ready to write"""
        xml_string = ElementTree.tostring(self.element, 'UTF-8')
        dom_xml = minidom.parseString(xml_string)
        dom_string = dom_xml.toprettyxml(indent="    ", encoding='UTF-8')
        return dom_string.decode('utf-8')

    # Public Methods ==========================================================

    def build_element(self) -> Optional[ElementTree.Element]:  # pragma: no cover pylint: disable=R0201
        """Build an ElementTree Element representing this node.
        
        This is a placeholder method that must be overridden by inheriting
        classes to provide actual XML element construction.
        
        Returns:
            Optional[ElementTree.Element]: None in base implementation.
                Subclasses should return a valid ElementTree.Element.

        """
        return None

# ==============================================================================


class ColorNodeBase(AscDescBase, AscXMLBase):  # pylint: disable=R0903
    """Base class for SOP and SAT color correction nodes.

    This class is meant only to be inherited by SopNode and SatNode classes
    and should not be used directly. It combines description and XML
    functionality while providing value validation methods for color
    correction parameters.

    Attributes:
        desc (List[str]): List of description strings. Inherited from
            AscDescBase.
        element (Optional[ElementTree.Element]): XML Element representation. 
            Inherited from AscXMLBase.
        xml (str): Formatted XML string. Inherited from AscXMLBase.
        xml_root (str): XML string with declaration header. Inherited from
            AscXMLBase.

    Example:
        >>> # This class is not used directly, but through SopNode/SatNode
        >>> from cdl_convert import ColorCorrection
        >>> cc = ColorCorrection("test_id")
        >>> cc.slope = [1.2, 1.1, 1.0]  # Uses SopNode internally
        >>> print(cc.sop_node.xml)  # XML representation

    """
    def __init__(self) -> None:
        super(ColorNodeBase, self).__init__()

    # Private Methods =========================================================

    @staticmethod
    def _check_single_value(value: Union[Decimal, str, float, int], name: str, negative_allow: bool = False) -> Decimal:
        """Check and validate a single numeric value for color correction.

        Args:
            value (Union[Decimal, str, float, int]): The numeric value to
                validate. Can be any numeric type or string representation.
            name (str): The type of value being checked (e.g., 'slope',
                'offset', 'power', 'saturation'). Used in error messages.
            negative_allow (bool, optional): Whether to allow negative values. 
                Defaults to False.

        Returns:
            Decimal: The validated value converted to Decimal type.

        Raises:
            ValidationError: If the value fails validation checks. Includes:
                - Non-numeric values when numeric is required
                - Negative values when negative_allow is False
                - Invalid string representations of numbers

        Example:
            >>> # Valid usage (internal method)
            >>> value = ColorNodeBase._check_single_value(1.5, 'slope')
            >>> print(value)  # Decimal('1.5')
            
            >>> # This would raise ValidationError for negative slope
            >>> try:
            ...     ColorNodeBase._check_single_value(-0.5, 'slope')
            ... except ValidationError as e:
            ...     print(f"Validation failed: {e}")
        """
        value = to_decimal(value, name)
        # If given as a single number, that number must be positive
        if not negative_allow:
            if value < 0:
                if config.config.halt_on_error:
                    raise ValidationError(
                        f'Invalid {name} value: "{value}". '
                        f'{name.title()} values must be non-negative (>= 0).'
                    )
                else:
                    value = Decimal('0.0')

        return value
