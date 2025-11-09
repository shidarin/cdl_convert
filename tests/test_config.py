#!/usr/bin/env python
"""
Tests for the config module's type-safe configuration system.
"""

import os
import sys
import unittest

# Add the parent directory to the path to import cdl_convert
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cdl_convert.config as config
from cdl_convert.config import CDLFormat, Config


class TestCDLFormat(unittest.TestCase):
    """Tests for the CDLFormat enum."""

    def test_format_values(self):
        """Test that CDLFormat enum has correct string values."""
        self.assertEqual(CDLFormat.ALE.value, "ale")
        self.assertEqual(CDLFormat.CC.value, "cc")
        self.assertEqual(CDLFormat.CCC.value, "ccc")
        self.assertEqual(CDLFormat.CDL.value, "cdl")
        self.assertEqual(CDLFormat.EDL.value, "edl")
        self.assertEqual(CDLFormat.FLEX.value, "flex")
        self.assertEqual(CDLFormat.RCDL.value, "rcdl")

    def test_format_creation_from_string(self):
        """Test creating CDLFormat from string values."""
        self.assertEqual(CDLFormat("ale"), CDLFormat.ALE)
        self.assertEqual(CDLFormat("cc"), CDLFormat.CC)
        self.assertEqual(CDLFormat("ccc"), CDLFormat.CCC)
        self.assertEqual(CDLFormat("cdl"), CDLFormat.CDL)
        self.assertEqual(CDLFormat("edl"), CDLFormat.EDL)
        self.assertEqual(CDLFormat("flex"), CDLFormat.FLEX)
        self.assertEqual(CDLFormat("rcdl"), CDLFormat.RCDL)

    def test_invalid_format_raises_error(self):
        """Test that invalid format strings raise ValueError."""
        with self.assertRaises(ValueError):
            CDLFormat("invalid")


class TestConfig(unittest.TestCase):
    """Tests for the Config dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()

    def test_default_values(self):
        """Test that Config has correct default values."""
        self.assertFalse(self.config.halt_on_error)

        expected_collection = {
            CDLFormat.ALE,
            CDLFormat.CCC,
            CDLFormat.CDL,
            CDLFormat.EDL,
            CDLFormat.FLEX,
            CDLFormat.OTIO,
        }
        self.assertEqual(
            set(self.config.collection_formats), expected_collection
        )

        expected_single = {CDLFormat.CC, CDLFormat.RCDL}
        self.assertEqual(set(self.config.single_formats), expected_single)

    def test_is_collection_format(self):
        """Test is_collection_format method."""
        # Test collection formats
        self.assertTrue(self.config.is_collection_format("ale"))
        self.assertTrue(self.config.is_collection_format("ccc"))
        self.assertTrue(self.config.is_collection_format("cdl"))
        self.assertTrue(self.config.is_collection_format("edl"))
        self.assertTrue(self.config.is_collection_format("flex"))

        # Test single formats (should return False)
        self.assertFalse(self.config.is_collection_format("cc"))
        self.assertFalse(self.config.is_collection_format("rcdl"))

        # Test invalid formats
        self.assertFalse(self.config.is_collection_format("invalid"))

        # Test case insensitivity
        self.assertTrue(self.config.is_collection_format("ALE"))
        self.assertTrue(self.config.is_collection_format("CCC"))

    def test_is_single_format(self):
        """Test is_single_format method."""
        # Test single formats
        self.assertTrue(self.config.is_single_format("cc"))
        self.assertTrue(self.config.is_single_format("rcdl"))

        # Test collection formats (should return False)
        self.assertFalse(self.config.is_single_format("ale"))
        self.assertFalse(self.config.is_single_format("ccc"))
        self.assertFalse(self.config.is_single_format("cdl"))
        self.assertFalse(self.config.is_single_format("edl"))
        self.assertFalse(self.config.is_single_format("flex"))

        # Test invalid formats
        self.assertFalse(self.config.is_single_format("invalid"))

        # Test case insensitivity
        self.assertTrue(self.config.is_single_format("CC"))
        self.assertTrue(self.config.is_single_format("RCDL"))

    def test_halt_on_error_modification(self):
        """Test that halt_on_error can be modified."""
        self.assertFalse(self.config.halt_on_error)
        self.config.halt_on_error = True
        self.assertTrue(self.config.halt_on_error)
        self.config.halt_on_error = False
        self.assertFalse(self.config.halt_on_error)


class TestGlobalConfigInstance(unittest.TestCase):
    """Tests for the global config instance."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset config to default state
        config.config.halt_on_error = False

    def tearDown(self):
        """Clean up after tests."""
        # Reset config to default state
        config.config.halt_on_error = False

    def test_global_config_exists(self):
        """Test that global config instance exists and is correct type."""
        self.assertIsInstance(config.config, Config)

    def test_global_config_modification(self):
        """Test that global config can be modified."""
        self.assertFalse(config.config.halt_on_error)

        config.config.halt_on_error = True
        self.assertTrue(config.config.halt_on_error)


if __name__ == "__main__":
    unittest.main()
