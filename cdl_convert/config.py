#!/usr/bin/env python
"""CDL Convert Configuration Module

Configuration management for CDL Convert

Classes:
    CDLFormat: Enum containing all supported CDL format types with type safety.
    Config: Type-safe configuration dataclass containing all global settings
        with validation.

Global Configuration:
    config: Global configuration instance providing centralized access to all
        settings via type-safe attributes (config.halt_on_error,
        config.input_encoding, config.output_encoding, etc.).

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

import codecs
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
    _input_encoding: str | None = None
    """Internal storage for input encoding."""

    @property
    def input_encoding(self) -> str | None:
        """Character encoding used when reading input files.

        - None (default): Auto-detect encoding for XML formats (cc, ccc, cdl) from
          XML declaration, use UTF-8 for non-XML formats (ale, flex, nk, rcdl).
        - Specified value: Override auto-detection and use this encoding for all
          input files.

        Common encodings: 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252'
        """
        return self._input_encoding

    @input_encoding.setter
    def input_encoding(self, value: str | None) -> None:
        """Set input encoding with validation.

        Args:
            value: Encoding name to use for input files, or None for auto-detection

        Raises:
            LookupError: If the encoding is not recognized by Python
        """
        if value is not None:
            # Validate that Python recognizes this encoding
            try:
                codecs.lookup(value)
            except LookupError as e:
                raise LookupError(
                    f"Unknown encoding: '{value}'. Python does not recognize this "
                    f"encoding name. Common encodings include: 'utf-8', 'latin-1', "
                    f"'iso-8859-1', 'cp1252', 'ascii'."
                ) from e
        self._input_encoding = value

    _output_encoding: str = "utf-8"
    """Internal storage for output encoding."""

    @property
    def output_encoding(self) -> str:
        """Character encoding used when writing output files. Default: utf-8.

        Common encodings: 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252'
        """
        return self._output_encoding

    @output_encoding.setter
    def output_encoding(self, value: str) -> None:
        """Set output encoding with validation.

        Args:
            value: Encoding name to use for output files

        Raises:
            LookupError: If the encoding is not recognized by Python
        """
        # Validate that Python recognizes this encoding
        try:
            codecs.lookup(value)
        except LookupError as e:
            raise LookupError(
                f"Unknown encoding: '{value}'. Python does not recognize this "
                f"encoding name. Common encodings include: 'utf-8', 'latin-1', "
                f"'iso-8859-1', 'cp1252', 'ascii'."
            ) from e
        self._output_encoding = value

    @staticmethod
    def normalize_encoding_name(encoding: str) -> str:
        """Normalize Python encoding names to IANA standard names for XML.

        Uses Python's codecs module to get the canonical encoding name, then
        maps it to the IANA-registered name suitable for XML declarations.
        Python's codecs.lookup() normalizes encoding aliases (e.g., 'latin-1',
        'latin1', 'iso-8859-1') to their canonical Python names, which we then
        convert to IANA standard names.

        Args:
            encoding: Python encoding name (e.g., 'latin-1', 'utf-8')

        Returns:
            IANA standard encoding name for XML (e.g., 'ISO-8859-1', 'UTF-8')

        Raises:
            LookupError: If the encoding is not recognized by Python

        Example:
            >>> Config.normalize_encoding_name('latin-1')
            'ISO-8859-1'
            >>> Config.normalize_encoding_name('utf-8')
            'UTF-8'

        """
        # Use Python's codecs to normalize the encoding name
        codec_info = codecs.lookup(encoding)
        python_name = codec_info.name

        # Map Python's canonical names to IANA standard names
        # Based on https://www.iana.org/assignments/character-sets/
        iana_map = {
            "iso8859-1": "ISO-8859-1",
            "iso8859-2": "ISO-8859-2",
            "iso8859-3": "ISO-8859-3",
            "iso8859-4": "ISO-8859-4",
            "iso8859-5": "ISO-8859-5",
            "iso8859-6": "ISO-8859-6",
            "iso8859-7": "ISO-8859-7",
            "iso8859-8": "ISO-8859-8",
            "iso8859-9": "ISO-8859-9",
            "iso8859-10": "ISO-8859-10",
            "iso8859-13": "ISO-8859-13",
            "iso8859-14": "ISO-8859-14",
            "iso8859-15": "ISO-8859-15",
            "iso8859-16": "ISO-8859-16",
            "utf-8": "UTF-8",
            "utf-16": "UTF-16",
            "utf-16-be": "UTF-16BE",
            "utf-16-le": "UTF-16LE",
            "utf-32": "UTF-32",
            "utf-32-be": "UTF-32BE",
            "utf-32-le": "UTF-32LE",
            "ascii": "US-ASCII",
            "cp1252": "windows-1252",
        }

        # Return IANA name if mapped, otherwise uppercase the Python name
        return iana_map.get(python_name, python_name.upper())

    @property
    def output_encoding_xml(self) -> str:
        """Get output encoding in XML standard (IANA) format for declarations.

        Returns:
            XML standard encoding name (e.g., 'UTF-8', 'ISO-8859-1')

        """
        return self.normalize_encoding_name(self.output_encoding)

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
