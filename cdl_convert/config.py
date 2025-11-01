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
from typing import FrozenSet

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
    RCDL = "rcdl"


# ==============================================================================
# CONFIGURATION
# ==============================================================================


@dataclass
class Config:
    """Type-safe configuration for CDL Convert.
    
    This class contains all global configuration settings with proper type
    hints and validation.
    
    Attributes:
        halt_on_error: If True, exceptions are raised instead of being handled
                      with default behavior. Used for strict validation mode.
        collection_formats: Set of formats that represent ColorCollection
            objects.
        single_formats: Set of formats that represent single ColorCorrection
            objects.

    """
    halt_on_error: bool = False
    collection_formats: FrozenSet[CDLFormat] = frozenset({
        CDLFormat.ALE,
        CDLFormat.CCC,
        CDLFormat.CDL,
        CDLFormat.EDL,
        CDLFormat.FLEX
    })
    single_formats: FrozenSet[CDLFormat] = frozenset({
        CDLFormat.CC,
        CDLFormat.RCDL
    })
    
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


# ==============================================================================
# GLOBAL INSTANCE
# ==============================================================================

# Global configuration instance
config = Config()

# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    'CDLFormat',
    'Config', 
    'config',
]