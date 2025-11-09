#!/usr/bin/env python
"""CDL Convert Utilities Module

This module provides utility functions for color correction validation,
numeric conversion, and data processing.

Public Functions:
    sanity_check(ColorCorrection) -> None: Validation function that
        checks color correction values against reasonable ranges.

    to_decimal(Union[str, int, float, Decimal], str) -> Decimal:
        Numeric conversion function with error handling.

Example Usage:
    >>> from decimal import Decimal
    >>> from cdl_convert import ColorCorrection, sanity_check, to_decimal
    >>>
    >>> # Type-safe numeric conversion
    >>> slope_value = to_decimal("1.2", "slope")
    >>> print(f"Converted value: {slope_value}")  # Decimal("1.2")
    >>>
    >>> # Enhanced validation with detailed reporting
    >>> cc = ColorCorrection("test_shot")
    >>> cc.slope = [2.5, 1.0, 0.8]  # Potentially unusual values
    >>> sanity_check(cc)  # Provides warnings
    >>>
    >>> try:
    ...     invalid_value = to_decimal("not_a_number", "saturation")
    ... except ValidationError as e:
    ...     print(f"Conversion error: {e}")

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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Imports

from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

# cdl_convert Imports
from cdl_convert.exceptions import ValidationError

# Avoid circular imports
if TYPE_CHECKING:
    from cdl_convert.correction import ColorCorrection

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "sanity_check",
    "to_decimal",
]

# ==============================================================================
# PUBLIC FUNCTIONS
# ==============================================================================


def sanity_check(colcor: "ColorCorrection") -> bool:
    """Check ColorCorrection values against reasonable ranges.

    Validates CDL parameter values against typical ranges used in color
    correction workflows. Prints warnings to stdout for values that fall
    outside normal ranges, but does not prevent their use since extreme
    values may be intentional for creative looks.

    Validation ranges:
    - Slope, Power, Saturation: 0.1 to 3.0
    - Offset: -1.0 to 1.0

    Args:
        colcor (ColorCorrection): ColorCorrection instance to validate.

    Returns:
        bool: True if all values are within normal ranges, False if any
            values triggered warnings.

    Example:
        >>> cc = ColorCorrection("test")
        >>> cc.slope = [2.5, 1.0, 0.8]  # High red slope
        >>> is_sane = sanity_check(cc)  # Prints warning for 2.5 slope
        >>> print(is_sane)  # False

    """
    sane_values = True

    def _check_value(value, minmax, value_type):
        """Check if value falls outside acceptable range and print warning.

        Args:
            value: Numeric value to check (converted to float for comparison).
            minmax: Tuple of (min, max) acceptable values.
            value_type: String description of value type for warning message.

        Returns:
            bool: True if value is within range, False if outside range.

        """
        value = float(value)  # Decimal doesn't always compare correctly
        if value <= minmax[0] or value >= minmax[1]:
            print(
                f'The ColorCorrection "{colcor.id}" was given a {value_type} value of '
                f'"{value}", which might be incorrect.'
            )
            return False
        else:
            return True

    if colcor.has_sop:
        for i in range(3):
            slope = _check_value(colcor.slope[i], (0.1, 3.0), "Slope")
            offset = _check_value(colcor.offset[i], (-1.0, 1.0), "Offset")
            power = _check_value(colcor.power[i], (0.1, 3.0), "Power")
            if not slope or not offset or not power:
                sane_values = False

    if colcor.has_sat:
        if not _check_value(colcor.sat, (0.1, 3.0), "Saturation"):
            sane_values = False

    return sane_values


# ==============================================================================


def to_decimal(
    value: Decimal | str | float | int, name: str = "Value"
) -> Decimal:
    """Convert numeric value to Decimal with validation and error handling.

    Converts various numeric types to Decimal format with appropriate
    formatting for CDL values. Handles type conversion, string parsing,
    and ensures proper decimal representation for color correction values.

    Conversion behavior:
    - float: Converted to string then Decimal to avoid precision issues
    - int: Appended with '.0' for proper decimal format
    - str: Validated and parsed, '.0' added if no decimal point
    - Decimal: Returned as-is

    Args:
        value (Union[Decimal, str, float, int]): Numeric value to convert.
        name (str): Descriptive name for the value type (e.g., 'slope',
            'offset') used in error messages.

    Returns:
        Decimal: Converted value as Decimal instance.

    Raises:
        ValidationError: If value cannot be converted to a valid number
            or is an unsupported type.

    Example:
        >>> slope_val = to_decimal(1.2, "slope")
        >>> print(slope_val)  # Decimal('1.2')
        >>> offset_val = to_decimal("0.5", "offset")
        >>> print(offset_val)  # Decimal('0.5')

    """
    # Use match statement for type-based conversion
    match value:
        case _ if isinstance(value, float):
            # Rather than mess about with float -> Decimal conversion,
            # it suits our accuracy needs just fine to go straight to string.
            value = str(value)
        case _ if isinstance(value, int) and not isinstance(value, bool):
            # If we're giving an int, we need to add a '.0' behind it.
            # Note: bool is a subclass of int, so we exclude it
            value = str(value) + ".0"
        case _ if isinstance(value, Decimal):
            return value
        case _ if isinstance(value, str):
            if "." not in value:
                value = value.strip()
                value += ".0"

            try:
                value = Decimal(value)
            except (InvalidOperation, ValueError) as e:
                raise ValidationError(
                    f'Invalid numeric value for {name}: "{value}". '
                    f"The provided string cannot be converted to a number."
                ) from e
        case _:
            raise ValidationError(
                f"Invalid {name} value type: {type(value).__name__}. "
                f'Provided value: "{value}". '
                f"{name.title()} must be a numeric value (int, float, str, or Decimal)."
            )

    return Decimal(value)
