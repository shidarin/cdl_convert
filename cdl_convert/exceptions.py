#!/usr/bin/env python
"""CDL Convert Exceptions Module

Exception classes for CDL Convert operations.

Exception Classes:
    CDLConvertError: Base exception class providing common interface for all
        CDL Convert operations.

    FormatError: Specialized exception for unsupported format detection and
        compatibility issues.

    ParseError: Comprehensive parsing exception with context about file 
        structure issues, malformed data, and specific parsing failures
        with line numbers and element information where available.

    ValidationError: Advanced validation exception providing detailed information
        about value validation failures, acceptable ranges, and specific
        validation rules that were violated.

Example Usage:
    >>> from cdl_convert import ColorCorrection, ValidationError, ParseError
    >>> 
    >>> # Validation error handling
    >>> try:
    ...     cc = ColorCorrection("test")
    ...     cc.slope = [-1.0, 1.0, 1.0]  # Invalid negative slope
    ... except ValidationError as e:
    ...     print(f"Validation failed: {e}")
    ...     # Error with context about which value failed and why
    >>> 
    >>> # Parsing error handling
    >>> try:
    ...     from cdl_convert import parse_file
    ...     from pathlib import Path
    ...     collection = parse_file(Path("malformed.xml"))
    ... except ParseError as e:
    ...     print(f"Parse error: {e}")
    ...     # Context about parsing failure location and cause
    >>> 
    >>> # Exception chaining for debugging
    >>> try:
    ...     # Some operation that might fail
    ...     pass
    ... except ValidationError as e:
    ...     raise FormatError(f"Format validation failed: {e}") from e

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
# EXPORTS
# ==============================================================================

__all__ = [
    'CDLConvertError',
    'ParseError',
    'ValidationError',
    'FormatError',
    'OTIOAdapterError',
]

# ==============================================================================
# EXCEPTIONS
# ==============================================================================


class CDLConvertError(Exception):
    """Base exception for CDL Convert operations.
    
    This is the base class for all CDL Convert specific exceptions.
    It provides a common interface for handling errors that occur
    during CDL file processing, parsing, validation, and conversion.

    """
    pass

class FormatError(CDLConvertError, ValueError):
    """Raised when unsupported format is encountered.
    
    This exception is raised when attempting to work with unsupported
    file formats or when format detection fails. It helps identify
    issues with file format compatibility and supported operations.
    
    Inherits from ValueError for backward compatibility.

    """
    pass

class ParseError(CDLConvertError, ValueError):
    """Raised when parsing CDL files fails.
    
    This exception is raised when there are issues parsing CDL files,
    such as malformed XML, missing required elements, or invalid file
    structure. It includes context about what went wrong during parsing.
    
    Inherits from ValueError for backward compatibility.

    """
    pass


class ValidationError(CDLConvertError, ValueError, TypeError):
    """Raised when CDL values fail validation.
    
    This exception is raised when CDL color correction values fail
    validation checks, such as negative slope values, invalid ranges,
    or incorrect data types. It provides detailed information about
    which values failed validation and why.
    
    Inherits from ValueError and TypeError for backward compatibility.
    
    """
    pass


class OTIOAdapterError(CDLConvertError):
    """Raised when OpenTimelineIO adapter operations fail.
    
    This exception is raised when there are issues with OpenTimelineIO
    adapter availability, installation, or parsing operations. It provides
    clear error messages with installation instructions for missing adapters.
    
    """
    pass

