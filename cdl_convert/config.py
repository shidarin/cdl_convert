#!/usr/bin/env python
"""CDL Convert Configuration Module

Configuration management for CDL Convert

Classes:
    CDLFormat: Enum containing all supported CDL format types with type safety.
    Config: Type-safe configuration dataclass containing all global settings
        with validation.

Global Configuration:
    config: Global configuration instance providing centralized access to all
        settings via type-safe attributes (config.halt_on_error, etc.).

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

from dataclasses import dataclass
from enum import Enum

# ==============================================================================
# ENUMS
# ==============================================================================


class CDLFormat(Enum):
    """Supported CDL format types."""

    ALE = "ale"
    CC = "cc"
    CCC = "ccc"
    CDL = "cdl"
    EDL = "edl"
    FLEX = "flex"
    NK = "nk"
    OTIO = "otio"
    RCDL = "rcdl"


# ==============================================================================
# CONFIGURATION
# ==============================================================================


@dataclass
class Config:
    """Type-safe configuration for CDL Convert.

    This class contains all global configuration settings with proper type
    hints and validation.

    """

    halt_on_error: bool = False
    """If True, exceptions are raised instead of being handled with default
    behavior. Used for strict validation mode."""
    collection_formats: frozenset[CDLFormat] = frozenset(
        {
            CDLFormat.ALE,
            CDLFormat.CCC,
            CDLFormat.CDL,
            CDLFormat.EDL,
            CDLFormat.FLEX,
            CDLFormat.OTIO,
        }
    )
    """Set of formats that represent ColorCollection objects."""
    single_formats: frozenset[CDLFormat] = frozenset(
        {CDLFormat.CC, CDLFormat.NK, CDLFormat.RCDL}
    )
    """Set of formats that represent single ColorCorrection objects."""
    sop_tag_name: str = "SOPNode"
    """XML element tag name for SOP nodes. Valid values: 'SOPNode', 'ASC_SOP'.
    Default is 'SOPNode' for standard format."""
    sat_tag_name: str = "SatNode"
    """XML element tag name for Saturation nodes. Valid values: 'SatNode',
    'SATNode', 'ASC_SAT'. Default is 'SatNode' (changed from 'SATNode' in v1.0
    for consistency). Use 'SATNode' for legacy behavior."""

    def is_collection_format(self, format_type: str) -> bool:
        """Check if a format string represents a collection format.

        Args:
            format_type: Format string to check (e.g., 'ccc', 'cdl')

        Returns:
            True if the format is a collection format, False otherwise.

        """
        try:
            fmt = CDLFormat(format_type.lower())
            return fmt in self.collection_formats
        except ValueError:
            return False

    def is_single_format(self, format_type: str) -> bool:
        """Check if a format string represents a single correction format.

        Args:
            format_type: Format string to check (e.g., 'cc', 'rcdl')

        Returns:
            True if the format is a single format, False otherwise.

        """
        try:
            fmt = CDLFormat(format_type.lower())
            return fmt in self.single_formats
        except ValueError:
            return False

    def set_sop_tag_name(self, tag_name: str) -> None:
        """Set SOP tag name with validation.

        Args:
            tag_name: Tag name to use. Must be 'SOPNode' or 'ASC_SOP'.

        Raises:
            ValidationError: If tag_name is not a valid option.

        Example:
            >>> config.set_sop_tag_name("ASC_SOP")
            >>> config.set_sop_tag_name("InvalidTag")  # Raises ValidationError

        """
        # Import here to avoid circular dependency
        from cdl_convert.exceptions import ValidationError

        valid_tags = ["SOPNode", "ASC_SOP"]
        if tag_name not in valid_tags:
            raise ValidationError(
                f"Invalid SOP tag name: '{tag_name}'. "
                f"Valid options: {', '.join(valid_tags)}"
            )
        self.sop_tag_name = tag_name

    def set_sat_tag_name(self, tag_name: str) -> None:
        """Set Saturation tag name with validation.

        Args:
            tag_name: Tag name to use. Must be 'SatNode', 'SATNode', or
                'ASC_SAT'.

        Raises:
            ValidationError: If tag_name is not a valid option.

        Example:
            >>> config.set_sat_tag_name("ASC_SAT")
            >>> config.set_sat_tag_name("SATNode")  # Legacy behavior
            >>> config.set_sat_tag_name("InvalidTag")  # Raises ValidationError

        """
        # Import here to avoid circular dependency
        from cdl_convert.exceptions import ValidationError

        valid_tags = ["SatNode", "SATNode", "ASC_SAT"]
        if tag_name not in valid_tags:
            raise ValidationError(
                f"Invalid Saturation tag name: '{tag_name}'. "
                f"Valid options: {', '.join(valid_tags)}"
            )
        self.sat_tag_name = tag_name


# ==============================================================================
# GLOBAL INSTANCE
# ==============================================================================

# Global configuration instance
config = Config()

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "CDLFormat",
    "Config",
    "config",
]
