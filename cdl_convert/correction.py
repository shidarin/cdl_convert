#!/usr/bin/env python
"""CDL Convert Color Correction Module

This module contains the core ColorCorrection class and supporting node classes
that form the backbone of CDL Convert. 

Classes:
    ColorValues: Dataclass for structured color correction data.

    ColorCorrection: The primary interface for ASC CDL color corrections.
        Contains SopNode and SatNode for organized value management.

    SatNode: Type-safe container for saturation values.

    SopNode: Type-safe container for slope, offset, and power values with
        RGB tuple management and validation

Example Usage:
    >>> from pathlib import Path
    >>> from decimal import Decimal
    >>> from cdl_convert import ColorCorrection, ColorValues
    >>> 
    >>> cc = ColorCorrection("shot_001", input_file=Path("input.ale"))
    >>> cc.slope = [1.2, 1.1, 1.0]
    >>> cc.sat = 0.9
    >>> 
    >>> # Use the ColorValues dataclass
    >>> values = cc.get_color_values()
    >>> print(f"Is unity: {values.is_unity()}")
    >>> 
    >>> # Enhanced error handling
    >>> try:
    ...     cc.slope = [-1.0, 1.0, 1.0]  # Negative slope
    ... except ValidationError as e:
    ...     print(f"Validation error: {e}")

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

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import re
from typing import Dict, List, Optional, Union, Tuple, Any
from xml.etree import ElementTree

# cdl_convert imports

from .base import AscColorSpaceBase, AscDescBase, AscXMLBase, ColorNodeBase
from . import config
from .exceptions import ValidationError



# ==============================================================================
# DATACLASSES
# ==============================================================================


@dataclass
class ColorValues:
    """Container for ASC CDL color correction values with validation.
    
    This dataclass provides a structured way to store and validate the 10
    ASC CDL color correction numbers. Values are automatically validated during
    initialization to ensure they conform to CDL requirements.
    
    Attributes:
        slope (Tuple[Decimal, Decimal, Decimal]): RGB slope values. Must be 
            non-negative. Defaults to (1.0, 1.0, 1.0) for unity.
        offset (Tuple[Decimal, Decimal, Decimal]): RGB offset values. Can be 
            negative. Defaults to (0.0, 0.0, 0.0) for unity.
        power (Tuple[Decimal, Decimal, Decimal]): RGB power values. Must be 
            non-negative. Defaults to (1.0, 1.0, 1.0) for unity.
        saturation (Decimal): Saturation value. Must be non-negative. 
            Defaults to 1.0 for unity.

    Example:
        >>> # Create with default unity values
        >>> values = ColorValues()
        >>> print(values.is_unity())  # True
        
        >>> # Create with custom values
        >>> from decimal import Decimal
        >>> values = ColorValues(
        ...     slope=(Decimal('1.2'), Decimal('1.1'), Decimal('1.0')),
        ...     saturation=Decimal('0.9')
        ... )
        >>> print(f"Slope: {values.slope}")
        
        >>> # Validation occurs automatically during initialization
        >>> try:
        ...     ColorValues(slope=(-1.0, 1.0, 1.0))  # Negative slope
        ... except ValidationError as e:
        ...     print(f"Validation error: {e}")

    Raises:
        ValidationError: If any values fail validation during initialization.
            This includes negative slope/power values, incorrect tuple lengths,
            or invalid data types.

    """
    slope: Tuple[Decimal, Decimal, Decimal] = (Decimal('1.0'), Decimal('1.0'), Decimal('1.0'))
    offset: Tuple[Decimal, Decimal, Decimal] = (Decimal('0.0'), Decimal('0.0'), Decimal('0.0'))
    power: Tuple[Decimal, Decimal, Decimal] = (Decimal('1.0'), Decimal('1.0'), Decimal('1.0'))
    saturation: Decimal = Decimal('1.0')
    
    def __post_init__(self) -> None:
        """Validate values after initialization."""
        self._validate_values()
    
    def _validate_values(self) -> None:
        """Validate all color correction values according to CDL requirements.
        
        Checks that RGB tuples contain exactly 3 values, that slope and power
        values are non-negative, and that saturation is non-negative.
        Validation behavior depends on the global halt_on_error configuration
        setting.
        
        Raises:
            ValidationError: If any values fail validation checks, including
                incorrect tuple lengths, negative slope/power values, or
                negative saturation values (when halt_on_error is enabled).

        """
        # Validate RGB tuples have exactly 3 values
        for name, values in [('slope', self.slope), ('offset', self.offset), ('power', self.power)]:
            if len(values) != 3:
                raise ValidationError(
                    f'Invalid {name} values: expected 3 RGB values, got {len(values)}. '
                    f'Provided values: {values}. '
                    f'{name.title()} must specify exactly 3 values for Red, Green, and Blue channels.'
                )
        
        # Validate that slope and power values are non-negative
        for name, values in [('slope', self.slope), ('power', self.power)]:
            for i, value in enumerate(values):
                if value < 0:
                    if config.config.halt_on_error:
                        channel = ['Red', 'Green', 'Blue'][i]
                        raise ValidationError(
                            f'Invalid {name} value for {channel} channel: {value}. '
                            f'{name.title()} values must be non-negative (>= 0).'
                        )
        
        # Validate saturation is non-negative
        if self.saturation < 0:
            if config.config.halt_on_error:
                raise ValidationError(
                    f'Invalid saturation value: {self.saturation}. '
                    f'Saturation must be non-negative (>= 0).'
                )
    
    def to_unity(self) -> 'ColorValues':
        """Return a new ColorValues instance with unity/identity values.
        
        Unity values represent no color correction applied:
        slope=1.0, offset=0.0, power=1.0, saturation=1.0.
        
        Returns:
            ColorValues: A new instance with all values set to unity defaults.
                
        Example:
            >>> unity = ColorValues().to_unity()
            >>> print(unity.slope)
            >>> print(unity.is_unity())  # True

        """
        return ColorValues()
    
    def is_unity(self) -> bool:
        """Check if all values are at unity/identity (no correction applied).
        
        Unity values represent no color correction: slope=1.0, offset=0.0,
        power=1.0, saturation=1.0. This is useful for determining if a
        ColorCorrection actually applies any changes.
        
        Returns:
            bool: True if all values are at unity (no correction applied),
                False if any values differ from unity defaults.
                
        Example:
            >>> unity_values = ColorValues()
            >>> print(unity_values.is_unity())  # True
            
            >>> modified_values = ColorValues(saturation=Decimal('0.8'))
            >>> print(modified_values.is_unity())  # False

        """
        unity = self.to_unity()
        return (self.slope == unity.slope and 
                self.offset == unity.offset and 
                self.power == unity.power and 
                self.saturation == unity.saturation)


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'ColorCorrection',
    'ColorValues',
    'SatNode',
    'SopNode',
]

# ==============================================================================
# CLASSES
# ==============================================================================


class ColorCorrection(AscDescBase, AscColorSpaceBase, AscXMLBase):  # pylint: disable=R0902,R0904
    """Container for ASC CDL color correction values and metadata.

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

    Class Attributes:
        members (Dict[str, ColorCorrection]): All ColorCorrection instances
            indexed by their unique ID.

    Attributes:
        desc (List[str]): List of description strings. Inherited from 
            AscDescBase.
        element (Optional[ElementTree.Element]): XML Element representation. 
            Inherited from AscXMLBase.
        file_in (Optional[Path]): Input file path.
        file_out (Optional[Path]): Output file path.
        has_sat (bool): True if saturation node exists.
        has_sop (bool): True if SOP node exists.
        id (str): Unique identifier for this color correction.
        input_desc (Optional[str]): Input colorspace description. Inherited 
            from AscColorSpaceBase.
        parent (Optional[Any]): Parent ColorCollection or ColorDecision.
        sat_node (SatNode): Saturation node containing saturation value.
        sop_node (SopNode): SOP node containing slope, offset, power values.
        viewing_desc (Optional[str]): Viewing environment description. 
            Inherited from AscColorSpaceBase.
        xml (str): Formatted XML string. Inherited from AscXMLBase.
        xml_root (str): XML string with declaration. Inherited from AscXMLBase.

    Example:
        >>> cc = ColorCorrection("shot_001")
        >>> cc.slope = [1.2, 1.1, 1.0]
        >>> cc.sat = 0.9
        >>> print(cc.id)  # "shot_001"

    """

    members: Dict[str, 'ColorCorrection'] = {}

    def __init__(self, id: str, input_file: Optional[Union[str, Path]] = None) -> None:  # pylint: disable=W0622
        """Initialize ColorCorrection with unique ID and optional input file.
        
        The ID must be unique among all ColorCorrection instances. If a
        duplicate ID is provided, behavior depends on the halt_on_error
        configuration setting.
        
        Args:
            id (str): Unique identifier for this color correction. Often a shot
                or sequence name. Will be sanitized to remove invalid
                characters.
            input_file (Optional[Union[str, Path]]): Optional path to the input
                file used to create this ColorCorrection. Can be string or
                Path.
                
        Raises:
            ValidationError: If ID is empty or duplicate (when halt_on_error is
                enabled).

        """
        super(ColorCorrection, self).__init__()

        # File Attributes
        self._file_in: Optional[Path] = Path(input_file).resolve() if input_file else None
        self._file_out: Optional[Path] = None

        # If we're under a ColorCorrectionCollection or ColorDecision node:
        self.parent: Optional[Any] = None

        # The id is really the only required part of a ColorCorrection node
        # Each ID should be unique
        id = _sanitize(id)
        if id in ColorCorrection.members.keys():
            if config.config.halt_on_error:
                existing_ids = list(ColorCorrection.members.keys())
                raise ValidationError(
                    f'Duplicate ColorCorrection ID: "{id}" is already registered. '
                    f'Each ColorCorrection must have a unique ID.'
                )
            else:
                id = f'{id}{len([cc for cc in ColorCorrection.members if cc.startswith(id)]):0>3}'
        elif not id:
            if config.config.halt_on_error:
                raise ValidationError(
                    'Empty ColorCorrection ID provided. '
                    'ColorCorrections require a non-empty ID for identification.'
                )
            else:
                id = str(len(ColorCorrection.members) + 1).rjust(3, '0')
        self._id = id

        # Register with member dictionary
        ColorCorrection.members[self._id] = self

        # ASC_SAT attribute
        self._sat_node: Optional['SatNode'] = None

        # ASC_SOP attributes
        self._sop_node: Optional['SopNode'] = None

    # Properties ==============================================================

    @property
    def file_in(self) -> Optional[Path]:
        """Return absolute path to the input file.
        
        Returns:
            Optional[Path]: Absolute path to input file, or None if no
                file was specified.

        """
        return self._file_in

    @file_in.setter
    def file_in(self, value: Optional[Union[str, Path]]) -> None:
        """Set input file path, converting to absolute path.
        
        Args:
            value (Optional[Union[str, Path]]): File path as string or Path
                object. Will be converted to absolute path. None clears the
                file path.

        """
        if value:
            self._file_in = Path(value).resolve()

    @property
    def file_out(self) -> Optional[Path]:
        """Return output file path for writing this ColorCorrection.
        
        Returns:
            Optional[Path]: Path where this ColorCorrection will be written,
                or None if no output path has been set.

        """
        return self._file_out

    @property
    def has_sat(self) -> bool:
        """Return True if saturation node has been created.
        
        Returns:
            bool: True if a SatNode instance exists, False otherwise.

        """
        if self._sat_node:
            return True
        else:
            return False

    @property
    def has_sop(self) -> bool:
        """Return True if SOP (slope/offset/power) node has been created.
        
        Returns:
            bool: True if a SopNode instance exists, False otherwise.

        """
        if self._sop_node:
            return True
        else:
            return False

    @property
    def id(self) -> str:  # pylint: disable=C0103
        """Return unique identifier for this color correction.
        
        Returns:
            str: Unique ID string, often a shot or sequence name.

        """
        return self._id

    @id.setter
    def id(self, value: str) -> None:  # pylint: disable=C0103
        """Set unique identifier after checking for duplicates.
        
        Args:
            value (str): New ID string. Must be unique among all
                ColorCorrections.
                
        Raises:
            ValidationError: If the new ID already exists in the members
                dictionary.

        """
        self._set_id(value)

    @property
    def offset(self) -> Tuple[Decimal, Decimal, Decimal]:
        """Return RGB offset values from the SOP node.
        
        Offset values raise or lower input brightness while holding slope
        constant.
        
        Returns:
            Tuple[Decimal, Decimal, Decimal]: RGB offset values as (R, G, B)
                tuple.

        """
        return self.sop_node.offset

    @offset.setter
    def offset(self, offset_rgb: Union[Decimal, float, int, str, List[Union[Decimal, float, int, str]], Tuple[Union[Decimal, float, int, str], ...]]) -> None:
        """Set RGB offset values after validation and conversion.
        
        Args:
            offset_rgb: Single numeric value (applied to all RGB channels) or
                list/tuple of 3 numeric values for individual RGB channels.
                Accepts Decimal, float, int, or numeric string types.

        """
        self.sop_node.offset = offset_rgb

    @property
    def power(self) -> Tuple[Decimal, Decimal, Decimal]:
        """Return RGB power values from the SOP node.
        
        Power values change the response curve of the function. Note that this
        has the opposite response to adjustments than a traditional gamma
        operator.
        
        Returns:
            Tuple[Decimal, Decimal, Decimal]: RGB power values as (R, G, B)
                tuple.

        """
        return self.sop_node.power

    @power.setter
    def power(self, power_rgb: Union[Decimal, float, int, str, List[Union[Decimal, float, int, str]], Tuple[Union[Decimal, float, int, str], ...]]) -> None:
        """Set RGB power values after validation and conversion.
        
        Args:
            power_rgb: Single numeric value (applied to all RGB channels) or
                list/tuple of 3 numeric values for individual RGB channels.
                Accepts Decimal, float, int, or numeric string types.
                Values must be non-negative.

        """
        self.sop_node.power = power_rgb

    @property
    def sat_node(self) -> 'SatNode':
        """Return SatNode instance, creating one if it doesn't exist.
        
        Returns:
            SatNode: The saturation node containing saturation value and
                descriptions.

        """
        if not self._sat_node:
            self._sat_node = SatNode(self)
        return self._sat_node

    @property
    def slope(self) -> Tuple[Decimal, Decimal, Decimal]:
        """Return RGB slope values from the SOP node.
        
        Slope values change the slope of the input without shifting the black
        level established by the offset.
        
        Returns:
            Tuple[Decimal, Decimal, Decimal]: RGB slope values as (R, G, B)
                tuple.

        """
        return self.sop_node.slope

    @slope.setter
    def slope(self, slope_rgb: Union[Decimal, float, int, str, List[Union[Decimal, float, int, str]], Tuple[Union[Decimal, float, int, str], ...]]) -> None:
        """Set RGB slope values after validation and conversion.
        
        Args:
            slope_rgb: Single numeric value (applied to all RGB channels) or
                list/tuple of 3 numeric values for individual RGB channels.
                Accepts Decimal, float, int, or numeric string types.
                Values must be non-negative.

        """
        self.sop_node.slope = slope_rgb

    @property
    def sop_node(self) -> 'SopNode':
        """Return SopNode instance, creating one if it doesn't exist.
        
        Returns:
            SopNode: The SOP node containing slope, offset, and power values.
        """
        if not self._sop_node:
            self._sop_node = SopNode(self)
        return self._sop_node

    @property
    def sat(self) -> Decimal:
        """Return saturation value from the saturation node.
        
        Returns:
            Decimal

        """
        return self.sat_node.sat

    @sat.setter
    def sat(self, sat_value: Union[Decimal, float, int, str]) -> None:
        """Set saturation value after validation and conversion.
        
        Args:
            sat_value: Saturation value as Decimal, float, int, or numeric
                string. Must be non-negative.

        """
        self.sat_node.sat = sat_value

    # Private Methods =========================================================

    def _set_id(self, new_id: str) -> None:
        """Change ID after verifying the new ID is unique.
        
        Args:
            new_id (str): New ID string to set.
            
        Raises:
            ValidationError: If the new ID already exists in the members
                dictionary.

        """
        cc_id = _sanitize(new_id)
        # Check if this id is already registered
        if cc_id in ColorCorrection.members.keys():
            existing_ids = list(ColorCorrection.members.keys())
            raise ValidationError(
                f'Cannot change ID to "{cc_id}": ID already exists. '
                f'Each ColorCorrection must have a unique ID. '
                f'Current ID: "{self._id}".'
            )
        else:
            # Clear the current id from the dictionary
            ColorCorrection.members.pop(self._id)
            self._id = cc_id
            # Register the new id with the dictionary
            ColorCorrection.members[self._id] = self

    # Public Methods ==========================================================

    def get_color_values(self) -> ColorValues:
        """Get all color correction values as a ColorValues dataclass.
        
        Provides a convenient way to access all color correction values in a
        structured format with validation and utility methods.
        
        Returns:
            ColorValues: Dataclass instance containing current slope, offset,
                power, and saturation values.
                
        """
        return ColorValues(
            slope=self.slope,
            offset=self.offset, 
            power=self.power,
            saturation=self.sat
        )
    
    def set_color_values(self, values: ColorValues) -> None:
        """Set all color correction values from a ColorValues dataclass.
        
        Provides a convenient way to set all color correction values at once
        from a validated ColorValues instance.
        
        Args:
            values (ColorValues): ColorValues dataclass instance containing
                the slope, offset, power, and saturation values to set.
                
        Raises:
            ValidationError: If any values in the ColorValues instance fail
                validation (e.g., negative slope values).
                
        Example:
            >>> from decimal import Decimal
            >>> cc = ColorCorrection("test_id")
            >>> values = ColorValues(
            ...     slope=(Decimal('1.2'), Decimal('1.1'), Decimal('1.0')),
            ...     saturation=Decimal('0.9')
            ... )
            >>> cc.set_color_values(values)
            >>> print(cc.slope)

        """
        self.slope = values.slope
        self.offset = values.offset
        self.power = values.power
        self.sat = values.saturation
    
    def is_unity(self) -> bool:
        """Check if this color correction represents unity/identity values.
        
        Unity values represent no color correction applied. This is useful for
        determining if a ColorCorrection actually modifies the image.
        
        Returns:
            bool: True if all values are at unity (slope=1.0, offset=0.0,
                power=1.0, saturation=1.0), False otherwise.

        """
        return self.get_color_values().is_unity()

    def build_element(self) -> ElementTree.Element:
        """Build XML ElementTree Element representing this ColorCorrection.
        
        Creates a ColorCorrection XML element with ID attribute and includes
        any input/viewing descriptions, general descriptions, and
        SOP/SAT nodes.
        
        Returns:
            ElementTree.Element: XML element representing this ColorCorrection.

        """
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

    def determine_dest(self, output: str, directory: Union[str, Path]) -> None:
        """Set output file path based on ID and output format.
        
        Constructs the output filename using the ColorCorrection ID and the
        specified output format extension.
        
        Args:
            output (str): File extension for output format (e.g., 'cc', 'ccc').
            directory (Union[str, Path]): Directory path where output file
                will be written.

        """

        filename = f"{self.id}.{output}"

        self._file_out = Path(directory) / filename

    # =========================================================================

    @classmethod
    def reset_members(cls) -> None:
        """Clear the class-level members dictionary.
        
        Removes all ColorCorrection instances from the members dictionary.
        Useful for testing or when starting with a clean state.

        """
        cls.members = {}

# ==============================================================================


class SatNode(ColorNodeBase):
    """Container for saturation value and descriptions.

    The SatNode stores the saturation value which is the last operation
    applied in the CDL color correction process.

    Class Attributes:
        element_names (List[str]): XML element names that map to this class
            during parsing ('ASC_SAT', 'SATNode', 'SatNode').

    Attributes:
        desc (List[str]): List of description strings. Inherited from
            AscDescBase.
        element (Optional[ElementTree.Element]): XML Element representation. 
            Inherited from AscXMLBase.
        parent (ColorCorrection): Parent ColorCorrection instance that
            created this node.
        sat (Decimal): Saturation value applied with Rec 709 coefficients.
            Must be non-negative. Defaults to 1.0 for unity/no correction.
        xml (str): Formatted XML string representation. Inherited from
            AscXMLBase.
        xml_root (str): XML string with declaration header. Inherited from
            AscXMLBase.

    Example:
        >>> cc = ColorCorrection("test")
        >>> cc.sat = 0.8
        >>> print(cc.sat_node.sat)  # Decimal('0.8')
        >>> print(cc.sat_node.parent.id)

    """

    # XML Fields for SopNodes can be one of these names:
    element_names: List[str] = ['ASC_SAT', 'SATNode', 'SatNode']

    def __init__(self, parent: 'ColorCorrection') -> None:
        super(SatNode, self).__init__()

        self._parent: 'ColorCorrection' = parent
        self._sat: Decimal = Decimal('1.0')

    # Properties ==============================================================

    @property
    def parent(self) -> 'ColorCorrection':
        """Return parent ColorCorrection instance that created this SatNode.
        
        Returns:
            ColorCorrection: The ColorCorrection instance that owns this
                SatNode.

        """
        return self._parent

    @property
    def sat(self) -> Decimal:
        """Return saturation value.
        
        Returns:
            Decimal: Saturation value applied with Rec 709 coefficients.

        """
        return self._sat

    @sat.setter
    def sat(self, value: Union[Decimal, float, int, str]) -> None:
        """Set saturation value after validation and conversion.
        
        Args:
            value (Union[Decimal, float, int, str]): Saturation value as
                numeric type or numeric string. Must be non-negative.
                
        Raises:
            ValidationError: If value is not numeric or fails validation
                checks.

        """
        # If given as a string, the string must be convertible to a Decimal
        if type(value) in [Decimal, float, int, str]:
            try:
                value = self._check_single_value(value, 'saturation')
            except (TypeError, ValueError):
                raise
            else:
                self._sat = Decimal(value)
        else:
            raise ValidationError(
                f'Invalid saturation value type: {type(value).__name__}. '
                f'Provided value: "{value}". '
                f'Saturation must be a numeric value (int, float, str, or Decimal).'
            )

    # Public Methods ==========================================================

    def build_element(self) -> ElementTree.Element:
        """Build XML ElementTree Element representing this SatNode.
        
        Creates a SATNode XML element containing any descriptions and the
        saturation value.
        
        Returns:
            ElementTree.Element: XML element representing this SatNode.

        """
        sat = ElementTree.Element('SATNode')
        for description in self.desc:
            desc = ElementTree.SubElement(sat, 'Description')
            desc.text = description
        op_node = ElementTree.SubElement(sat, 'Saturation')
        op_node.text = _de_exponent(self.sat)
        return sat

# ==============================================================================


class SopNode(ColorNodeBase):
    """Container for slope, offset, and power values.

    The SopNode stores the slope, offset, and power values that form the core
    of the CDL color correction. Values are stored internally as lists but
    returned as tuples to prevent direct index modification and maintain
    data integrity.

    Class Attributes:
        element_names (List[str]): XML element names that map to this class
            during parsing ('ASC_SOP', 'SOPNode', 'SopNode').

    Attributes:
        desc (List[str]): List of description strings. Inherited from
            AscDescBase.
        element (Optional[ElementTree.Element]): XML Element representation. 
            Inherited from AscXMLBase.
        parent (ColorCorrection): Parent ColorCorrection instance that created
            this node.
        slope (Tuple[Decimal, Decimal, Decimal]): RGB slope values that change
            the slope of the input without shifting the black level established
            by offset. Must be non-negative. Default: (1.0, 1.0, 1.0).
        offset (Tuple[Decimal, Decimal, Decimal]): RGB offset values that raise
            or lower input brightness while holding slope constant. Can be
            negative. Default: (0.0, 0.0, 0.0).
        power (Tuple[Decimal, Decimal, Decimal]): RGB power values that change
            the response curve. Note this has opposite response to traditional
            gamma. Must be non-negative. Default: (1.0, 1.0, 1.0).
        xml (str): Formatted XML string representation. Inherited from
            AscXMLBase.
        xml_root (str): XML string with declaration header. Inherited from
            AscXMLBase.

    Example:
        >>> cc = ColorCorrection("test")
        >>> cc.slope = [1.2, 1.1, 1.0]
        >>> print(cc.sop_node.slope)
        >>> cc.offset = 0.1  # Applied to all RGB channels
        >>> print(cc.sop_node.offset)

    """

    # XML Fields for SopNodes can be one of these names:
    element_names: List[str] = ['ASC_SOP', 'SOPNode', 'SopNode']

    def __init__(self, parent: 'ColorCorrection') -> None:
        super(SopNode, self).__init__()

        self._parent: 'ColorCorrection' = parent

        self._slope: List[Decimal] = [Decimal('1.0')] * 3
        self._offset: List[Decimal] = [Decimal('0.0')] * 3
        self._power: List[Decimal] = [Decimal('1.0')] * 3

    # Properties ==============================================================

    @property
    def parent(self) -> 'ColorCorrection':
        """Return parent ColorCorrection instance that created this SopNode.
        
        Returns:
            ColorCorrection: The ColorCorrection instance that owns this
                SopNode.

        """
        return self._parent

    @property
    def slope(self) -> Tuple[Decimal, Decimal, Decimal]:
        """Return RGB slope values as tuple.
        
        Returns:
            Tuple[Decimal, Decimal, Decimal]: RGB slope values as (R, G, B)
                tuple. Values change input slope without shifting black level.

        """
        return tuple(self._slope)

    @slope.setter
    def slope(self, value: Union[Decimal, float, int, str, List[Union[Decimal, float, int, str]], Tuple[Union[Decimal, float, int, str], ...]]) -> None:
        """Set RGB slope values after validation and conversion.
        
        Args:
            value: Single numeric value (applied to all RGB channels) or
                list/tuple of 3 numeric values for individual RGB channels.
                Accepts Decimal, float, int, or numeric string types.
                Values must be non-negative.
        """
        value = self._check_setter_value(value, 'slope')
        self._slope = value

    @property
    def offset(self) -> Tuple[Decimal, Decimal, Decimal]:
        """Return RGB offset values as tuple.
        
        Returns:
            Tuple[Decimal, Decimal, Decimal]: RGB offset values as (R, G, B)
                tuple. Values raise or lower input brightness while holding
                slope constant.

        """
        return tuple(self._offset)

    @offset.setter
    def offset(self, value: Union[Decimal, float, int, str, List[Union[Decimal, float, int, str]], Tuple[Union[Decimal, float, int, str], ...]]) -> None:
        """Set RGB offset values after validation and conversion.
        
        Args:
            value: Single numeric value (applied to all RGB channels) or
                list/tuple of 3 numeric values for individual RGB channels.
                Accepts Decimal, float, int, or numeric string types.
                Can be negative.

        """
        value = self._check_setter_value(value, 'offset', True)
        self._offset = value

    @property
    def power(self) -> Tuple[Decimal, Decimal, Decimal]:
        """Return RGB power values as tuple.
        
        Returns:
            Tuple[Decimal, Decimal, Decimal]: RGB power values as (R, G, B)
                tuple. Values change response curve with opposite behavior to
                traditional gamma.
        """
        return tuple(self._power)

    @power.setter
    def power(self, value: Union[Decimal, float, int, str, List[Union[Decimal, float, int, str]], Tuple[Union[Decimal, float, int, str], ...]]) -> None:
        """Set RGB power values after validation and conversion.
        
        Args:
            value: Single numeric value (applied to all RGB channels) or
                list/tuple of 3 numeric values for individual RGB channels.
                Accepts Decimal, float, int, or numeric string types.
                Values must be non-negative.

        """
        value = self._check_setter_value(value, 'power')
        self._power = value

    # Private Methods =========================================================

    def _check_rgb_values(self, values: Union[List[Union[Decimal, str, float, int]], Tuple[Union[Decimal, str, float, int], ...]], name: str, negative_allow: bool = False) -> List[Decimal]:
        """Validate list or tuple containing exactly 3 RGB values.

        Ensures the provided values list contains exactly 3 numeric values and
        validates each value according to CDL requirements.

        Args:
            values (Union[List, Tuple]): List or tuple of 3 numeric values to
                validate.
            name (str): Type of values being checked (slope, offset, power).
            negative_allow (bool): Whether to allow negative values.
                Defaults to False.

        Returns:
            List[Decimal]: List of 3 validated values converted to Decimal
                type.

        Raises:
            ValidationError: If list length is not 3 or any values fail
                validation.

        """
        if len(values) != 3:
            raise ValidationError(
                f'Invalid {name} values: expected 3 RGB values, got {len(values)}. '
                f'Provided values: {values}. '
                f'{name.title()} must specify exactly 3 values for Red, Green, and Blue channels.'
            )

        values = list(values)

        for i in range(len(values)):
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

    def _check_setter_value(self, value: Union[Decimal, float, int, str, List[Union[Decimal, float, int, str]], Tuple[Union[Decimal, float, int, str], ...]], name: str, negative_allow: bool = False) -> List[Decimal]:
        """Validate and convert single value or RGB list for property setting.

        Handles both single values (applied to all RGB channels) and RGB
            lists/tuples.
        Coordinates validation between single value and RGB list validation
            methods.

        Args:
            value: Single numeric value (applied to all RGB channels) or
                list/tuple of 3 numeric values for individual RGB channels.
            name (str): Type of values being checked (slope, offset, power).
            negative_allow (bool): Whether to allow negative values. Defaults
                to False.

        Returns:
            List[Decimal]: List of 3 validated Decimal values ready for
                assignment.

        Raises:
            ValidationError: If value type is invalid or validation fails.

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
            raise ValidationError(
                f'Invalid {name} value type: {type(value).__name__}. '
                f'Provided value: "{value}". '
                f'{name.title()} must be a numeric value or list of 3 numeric values. '
                f'Supported types: int, float, str, Decimal, list, or tuple.'
            )

        return set_value

    # Public Methods ==========================================================

    def build_element(self) -> ElementTree.Element:
        """Build XML ElementTree Element representing this SopNode.
        
        Creates a SOPNode XML element containing any descriptions and the
        slope, offset, and power values formatted as space-separated strings.
        
        Returns:
            ElementTree.Element: XML element representing this SopNode.

        """
        sop = ElementTree.Element('SOPNode')
        fields = ['Slope', 'Offset', 'Power']
        for description in self.desc:
            desc = ElementTree.SubElement(sop, 'Description')
            desc.text = description
        for i, grade in enumerate([self.slope, self.offset, self.power]):
            op_node = ElementTree.SubElement(sop, fields[i])
            op_node.text = f'{_de_exponent(grade[0])} {_de_exponent(grade[1])} {_de_exponent(grade[2])}'
        return sop

# ==============================================================================
# PRIVATE FUNCTIONS
# ==============================================================================


def _de_exponent(notation: Union[Decimal, str, int, float]) -> str:
    """Convert scientific notation to non-normalized decimal string.

    Converts numeric values that may be in scientific notation (e.g., 1.5e-3)
    to regular decimal string format (e.g., 0.0015). Unlike standard Decimal
    quantization methods, this function handles all cases reliably.

    Args:
        notation (Union[Decimal, str, int, float]): Numeric value that may or
            may not be in scientific notation format.

    Returns:
        str: Numeric value as string without scientific notation formatting.
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
        value = value.removeprefix('-')
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


def _sanitize(name: str) -> str:
    """Remove invalid characters from name string for use as CDL ID.

    Sanitizes strings to be valid CDL identifiers by replacing spaces with
    underscores, removing leading underscores/periods, and filtering out
    invalid characters. Only alphanumeric characters, underscores, periods,
    and hyphens are preserved.

    Args:
        name (str): String to sanitize for use as CDL identifier.

    Returns:
        str: Sanitized name string safe for use as CDL ID, or original
            string if it was empty.
            
    """
    if not name:
        # If not name, it's probably an empty string, but let's throw back
        # exactly what we got.
        return name
    # Replace any spaces with underscores
    name = name.replace(' ', '_')
    # If we start our string with an underscore or period, remove it
    name = name.removeprefix('_').removeprefix('.')
    # a-z is all lowercase
    # A-Z is all uppercase
    # 0-9 is all digits
    # \. is an escaped period
    # _ is an underscore
    # Put them together, negate them by leading with an ^
    # and our sub will mark every non alnum, non ., _ character
    return re.sub(r'[^a-zA-Z0-9\._-]+', '', name)

    return fixed
