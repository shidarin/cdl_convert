#!/usr/bin/env python
"""
Tests the exceptions module of cdl_convert
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Imports
import os
import sys
import unittest

# Grab our test's path and append the cdl_convert root directory
sys.path.append('/'.join(os.path.realpath(__file__).split('/')[:-2]))

import cdl_convert
from cdl_convert.exceptions import (
    CDLConvertError,
    ParseError,
    ValidationError,
    FormatError
)

# ==============================================================================
# TEST CLASSES
# ==============================================================================


class TestCDLConvertError(unittest.TestCase):
    """Tests the CDLConvertError base exception class"""

    def test_inheritance(self):
        """Tests that CDLConvertError inherits from Exception"""
        self.assertTrue(issubclass(CDLConvertError, Exception))

    def test_instantiation(self):
        """Tests that CDLConvertError can be instantiated"""
        error = CDLConvertError("Test error message")
        self.assertIsInstance(error, CDLConvertError)
        self.assertEqual(str(error), "Test error message")

    def test_raise_and_catch(self):
        """Tests that CDLConvertError can be raised and caught"""
        with self.assertRaises(CDLConvertError):
            raise CDLConvertError("Test error")


class TestParseError(unittest.TestCase):
    """Tests the ParseError exception class"""

    def test_inheritance(self):
        """Tests that ParseError inherits from CDLConvertError and ValueError"""
        self.assertTrue(issubclass(ParseError, CDLConvertError))
        self.assertTrue(issubclass(ParseError, ValueError))

    def test_instantiation(self):
        """Tests that ParseError can be instantiated"""
        error = ParseError("Parse failed")
        self.assertIsInstance(error, ParseError)
        self.assertEqual(str(error), "Parse failed")

    def test_raise_and_catch(self):
        """Tests that ParseError can be raised and caught"""
        with self.assertRaises(ParseError):
            raise ParseError("Parse error")

    def test_catch_as_base_class(self):
        """Tests that ParseError can be caught as CDLConvertError"""
        with self.assertRaises(CDLConvertError):
            raise ParseError("Parse error")


class TestValidationError(unittest.TestCase):
    """Tests the ValidationError exception class"""

    def test_inheritance(self):
        """Tests that ValidationError inherits from CDLConvertError, ValueError, and TypeError"""
        self.assertTrue(issubclass(ValidationError, CDLConvertError))
        self.assertTrue(issubclass(ValidationError, ValueError))
        self.assertTrue(issubclass(ValidationError, TypeError))

    def test_instantiation(self):
        """Tests that ValidationError can be instantiated"""
        error = ValidationError("Validation failed")
        self.assertIsInstance(error, ValidationError)
        self.assertEqual(str(error), "Validation failed")

    def test_raise_and_catch(self):
        """Tests that ValidationError can be raised and caught"""
        with self.assertRaises(ValidationError):
            raise ValidationError("Validation error")

    def test_catch_as_base_class(self):
        """Tests that ValidationError can be caught as CDLConvertError"""
        with self.assertRaises(CDLConvertError):
            raise ValidationError("Validation error")


class TestFormatError(unittest.TestCase):
    """Tests the FormatError exception class"""

    def test_inheritance(self):
        """Tests that FormatError inherits from CDLConvertError and ValueError"""
        self.assertTrue(issubclass(FormatError, CDLConvertError))
        self.assertTrue(issubclass(FormatError, ValueError))

    def test_instantiation(self):
        """Tests that FormatError can be instantiated"""
        error = FormatError("Unsupported format")
        self.assertIsInstance(error, FormatError)
        self.assertEqual(str(error), "Unsupported format")

    def test_raise_and_catch(self):
        """Tests that FormatError can be raised and caught"""
        with self.assertRaises(FormatError):
            raise FormatError("Format error")

    def test_catch_as_base_class(self):
        """Tests that FormatError can be caught as CDLConvertError"""
        with self.assertRaises(CDLConvertError):
            raise FormatError("Format error")


class TestExceptionChaining(unittest.TestCase):
    """Tests exception chaining functionality"""

    def test_parse_error_chaining(self):
        """Tests that ParseError can be chained from other exceptions"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ParseError("Parse failed") from e
        except ParseError as pe:
            self.assertIsInstance(pe.__cause__, ValueError)
            self.assertEqual(str(pe.__cause__), "Original error")

    def test_validation_error_chaining(self):
        """Tests that ValidationError can be chained from other exceptions"""
        try:
            try:
                raise TypeError("Type mismatch")
            except TypeError as e:
                raise ValidationError("Validation failed") from e
        except ValidationError as ve:
            self.assertIsInstance(ve.__cause__, TypeError)
            self.assertEqual(str(ve.__cause__), "Type mismatch")

    def test_cdlconvert_error_chaining(self):
        """Tests that CDLConvertError can be chained from OSError (like in write functions)"""
        try:
            try:
                raise OSError("Permission denied")
            except OSError as e:
                raise CDLConvertError("Failed to write file") from e
        except CDLConvertError as ce:
            self.assertIsInstance(ce.__cause__, OSError)
            self.assertEqual(str(ce.__cause__), "Permission denied")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    unittest.main()