#!/usr/bin/env python
"""

CDL Convert Base
================

Contains base classes containing methods and attributes shared between many
CDL classes. The classes listed here should only be used for inheritance by
more fully realized classes.

## Classes

    AscColorSpaceBase

        Contains attributes and methods for input colorspace description and
        viewing colorspace descriptions. Methods are parse methods for
        parsing an ElementTree element and retrieving the Input Description
        and Viewing Description if present.

    AscDescBase

        Contains attributes and methods for generic description entries.
        Methods are parse methods for parsing an ElementTree element and
        retrieving all Description entries within.

        The ``desc`` attribute has specific setting behavior as follows:
            * If set with `None`, ``desc`` will be set to an empty list.
            * If set with a list or tuple, ``desc`` will become a list of that
                list or tuple.
            * If set with a straight value (such as a string) that value is
                appended to the end of the current ``desc`` list.

    AscXMLBase

        Base class for nodes which need to be represented as ElementTree
        XML Elements. This class contains several attributes and methods to
        facilitate this:

            * An ``element`` attribute which will return the
                ElementTree Element
            * An ``xml`` attribute which returns the built element as a
                pretty formatted string.
            * An ``xml_root`` attribute which returns the same built element
                as above, but with the required XML header. This XML string
                is ready to be printed.

        All of these attributes depend on the ``build_element`` method, which
        must be overridden by classes which inherit this class if the above
        attributes are to work. The ``build_element`` must return an
        ElementTree Element.

    ColorNodeBase

        A base class for Sop and Sat nodes, some basic color value checking
        functionality is included here.

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
import re
import sys
from xml.dom import minidom
from xml.etree import ElementTree

# cdl_convert Imports
from . import config
from .utils import to_decimal

# ==============================================================================
# GLOBALS
# ==============================================================================

if sys.version_info[0] >= 3:  # pragma: no cover
    enc = lambda x: bytes(x, 'UTF-8')  # pylint: disable=C0103
else:  # pragma: no cover
    enc = lambda x: x  # pylint: disable=C0103

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
            A placeholder method to be overridden by inheriting classes,
            calling it will always return None.

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
            value : (Decimal|str|float|int)
                Any numeric value to be checked.

            name : (str)
                The type of value being checked: slope, offset, etc.

            negative_allow=False : (bool)
                If false, do not allow negative values.

        **Returns:**
            (Decimal)
                If value passes all tests, returns value as Decimal.

        **Raises:**
            TypeError:
                If value given is not a number.

            ValueError:
                If negative is False, raised if value given is negative.

        """
        value = to_decimal(value, name)
        # If given as a single number, that number must be positive
        if not negative_allow:
            if value < 0:
                if config.HALT_ON_ERROR:
                    raise ValueError(
                        'Error setting {name} with value: "{value}". '
                        'Values must not be negative'.format(
                            name=name,
                            value=value
                        )
                    )
                else:
                    value = Decimal('0.0')

        return value
