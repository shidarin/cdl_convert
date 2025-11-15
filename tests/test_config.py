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
from cdl_convert.correction import ColorCorrection


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
        self.assertEqual(CDLFormat.NK.value, "nk")
        self.assertEqual(CDLFormat.OTIO.value, "otio")
        self.assertEqual(CDLFormat.RCDL.value, "rcdl")

    def test_format_creation_from_string(self):
        """Test creating CDLFormat from string values."""
        self.assertEqual(CDLFormat("ale"), CDLFormat.ALE)
        self.assertEqual(CDLFormat("cc"), CDLFormat.CC)
        self.assertEqual(CDLFormat("ccc"), CDLFormat.CCC)
        self.assertEqual(CDLFormat("cdl"), CDLFormat.CDL)
        self.assertEqual(CDLFormat("edl"), CDLFormat.EDL)
        self.assertEqual(CDLFormat("flex"), CDLFormat.FLEX)
        self.assertEqual(CDLFormat("nk"), CDLFormat.NK)
        self.assertEqual(CDLFormat("otio"), CDLFormat.OTIO)
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

        expected_single = {CDLFormat.CC, CDLFormat.NK, CDLFormat.RCDL}
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
        self.assertTrue(self.config.is_single_format("nk"))
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
        self.assertTrue(self.config.is_single_format("NK"))
        self.assertTrue(self.config.is_single_format("RCDL"))

    def test_halt_on_error_modification(self):
        """Test that halt_on_error can be modified."""
        self.assertFalse(self.config.halt_on_error)
        self.config.halt_on_error = True
        self.assertTrue(self.config.halt_on_error)
        self.config.halt_on_error = False
        self.assertFalse(self.config.halt_on_error)

    def test_default_tag_names(self):
        """Test that tag names have correct default values."""
        self.assertEqual(self.config.sop_tag_name, "SOPNode")
        self.assertEqual(self.config.sat_tag_name, "SatNode")

    def test_set_sop_tag_name_valid(self):
        """Test setting valid SOP tag names."""
        self.config.set_sop_tag_name("SOPNode")
        self.assertEqual(self.config.sop_tag_name, "SOPNode")

        self.config.set_sop_tag_name("ASC_SOP")
        self.assertEqual(self.config.sop_tag_name, "ASC_SOP")

    def test_set_sop_tag_name_invalid(self):
        """Test that invalid SOP tag names raise ValidationError."""
        from cdl_convert.exceptions import ValidationError

        with self.assertRaises(ValidationError) as cm:
            self.config.set_sop_tag_name("InvalidTag")
        self.assertIn("Invalid SOP tag name", str(cm.exception))
        self.assertIn("SOPNode, ASC_SOP", str(cm.exception))

    def test_set_sat_tag_name_valid(self):
        """Test setting valid Saturation tag names."""
        self.config.set_sat_tag_name("SatNode")
        self.assertEqual(self.config.sat_tag_name, "SatNode")

        self.config.set_sat_tag_name("SATNode")
        self.assertEqual(self.config.sat_tag_name, "SATNode")

        self.config.set_sat_tag_name("ASC_SAT")
        self.assertEqual(self.config.sat_tag_name, "ASC_SAT")

    def test_set_sat_tag_name_invalid(self):
        """Test that invalid Saturation tag names raise ValidationError."""
        from cdl_convert.exceptions import ValidationError

        with self.assertRaises(ValidationError) as cm:
            self.config.set_sat_tag_name("InvalidTag")
        self.assertIn("Invalid Saturation tag name", str(cm.exception))
        self.assertIn("SatNode, SATNode, ASC_SAT", str(cm.exception))


class TestGlobalConfigInstance(unittest.TestCase):
    """Tests for the global config instance."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset config to default state
        config.config.halt_on_error = False
        config.config.sop_tag_name = "SOPNode"
        config.config.sat_tag_name = "SatNode"

    def tearDown(self):
        """Clean up after tests."""
        # Reset config to default state
        config.config.halt_on_error = False
        config.config.sop_tag_name = "SOPNode"
        config.config.sat_tag_name = "SatNode"

    def test_global_config_exists(self):
        """Test that global config instance exists and is correct type."""
        self.assertIsInstance(config.config, Config)

    def test_global_config_modification(self):
        """Test that global config can be modified."""
        self.assertFalse(config.config.halt_on_error)

        config.config.halt_on_error = True
        self.assertTrue(config.config.halt_on_error)


class TestSopNodeTagNames(unittest.TestCase):
    """Tests for SopNode XML tag name configuration."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset config to default state
        config.config.sop_tag_name = "SOPNode"
        config.config.sat_tag_name = "SatNode"
        ColorCorrection.reset_members()

    def tearDown(self):
        """Clean up after tests."""
        # Reset config to default state
        config.config.sop_tag_name = "SOPNode"
        config.config.sat_tag_name = "SatNode"
        ColorCorrection.reset_members()

    def test_sop_default_tag_name(self):
        """Test SopNode uses default 'SOPNode' tag."""
        cc = ColorCorrection("test_id")
        cc.slope = [1.2, 1.1, 1.0]

        element = cc.sop_node.build_element()

        self.assertEqual(element.tag, "SOPNode")
        self.assertIsNotNone(element.find("Slope"))

    def test_sop_asc_tag_name(self):
        """Test SopNode uses 'ASC_SOP' tag when configured."""
        config.config.set_sop_tag_name("ASC_SOP")

        cc = ColorCorrection("test_id")
        cc.slope = [1.2, 1.1, 1.0]

        element = cc.sop_node.build_element()

        self.assertEqual(element.tag, "ASC_SOP")
        self.assertIsNotNone(element.find("Slope"))
        self.assertIsNotNone(element.find("Offset"))
        self.assertIsNotNone(element.find("Power"))


class TestEncodingConfiguration(unittest.TestCase):
    """Tests for encoding configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()

    def test_default_encoding_values(self):
        """Test that encoding has correct default values."""
        self.assertIsNone(self.config.input_encoding)
        self.assertEqual(self.config.output_encoding, "utf-8")

    def test_normalize_encoding_latin1(self):
        """Test that latin-1 variants are normalized to ISO-8859-1."""
        self.assertEqual(
            Config.normalize_encoding_name("latin-1"), "ISO-8859-1"
        )
        self.assertEqual(Config.normalize_encoding_name("latin1"), "ISO-8859-1")
        self.assertEqual(
            Config.normalize_encoding_name("iso-8859-1"), "ISO-8859-1"
        )
        self.assertEqual(
            Config.normalize_encoding_name("iso8859-1"), "ISO-8859-1"
        )

    def test_normalize_encoding_utf8(self):
        """Test that utf-8 variants are normalized to UTF-8."""
        self.assertEqual(Config.normalize_encoding_name("utf-8"), "UTF-8")
        self.assertEqual(Config.normalize_encoding_name("utf8"), "UTF-8")

    def test_normalize_encoding_ascii(self):
        """Test that ascii variants are normalized to US-ASCII."""
        self.assertEqual(Config.normalize_encoding_name("ascii"), "US-ASCII")
        self.assertEqual(Config.normalize_encoding_name("us-ascii"), "US-ASCII")

    def test_normalize_encoding_windows1252(self):
        """Test that windows-1252 variants are normalized."""
        self.assertEqual(
            Config.normalize_encoding_name("windows-1252"), "windows-1252"
        )
        self.assertEqual(
            Config.normalize_encoding_name("cp1252"), "windows-1252"
        )

    def test_invalid_encoding_raises_error(self):
        """Test that setting an invalid encoding raises LookupError."""
        with self.assertRaises(LookupError) as cm:
            self.config.output_encoding = "some-custom-encoding"
        self.assertIn("Unknown encoding", str(cm.exception))
        self.assertIn("some-custom-encoding", str(cm.exception))

        with self.assertRaises(LookupError) as cm:
            self.config.input_encoding = "invalid-encoding-name"
        self.assertIn("Unknown encoding", str(cm.exception))
        self.assertIn("invalid-encoding-name", str(cm.exception))

    def test_output_encoding_xml_property(self):
        """Test output_encoding_xml property returns normalized name."""
        self.config.output_encoding = "utf-8"
        self.assertEqual(self.config.output_encoding_xml, "UTF-8")

        self.config.output_encoding = "latin-1"
        self.assertEqual(self.config.output_encoding_xml, "ISO-8859-1")

        self.config.output_encoding = "ascii"
        self.assertEqual(self.config.output_encoding_xml, "US-ASCII")

    def test_valid_encoding_assignment(self):
        """Test that valid encodings can be assigned."""
        # These should all work without raising errors
        self.config.input_encoding = "utf-8"
        self.assertEqual(self.config.input_encoding, "utf-8")

        self.config.input_encoding = "latin-1"
        self.assertEqual(self.config.input_encoding, "latin-1")

        self.config.input_encoding = None
        self.assertIsNone(self.config.input_encoding)

        self.config.output_encoding = "iso-8859-1"
        self.assertEqual(self.config.output_encoding, "iso-8859-1")

        self.config.output_encoding = "cp1252"
        self.assertEqual(self.config.output_encoding, "cp1252")


class TestSatNodeTagNames(unittest.TestCase):
    """Tests for SatNode XML tag name configuration."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset config to default state
        config.config.sop_tag_name = "SOPNode"
        config.config.sat_tag_name = "SatNode"
        ColorCorrection.reset_members()

    def tearDown(self):
        """Clean up after tests."""
        # Reset config to default state
        config.config.sop_tag_name = "SOPNode"
        config.config.sat_tag_name = "SatNode"
        ColorCorrection.reset_members()

    def test_sat_default_tag_name(self):
        """Test SatNode uses default 'SatNode' tag."""
        cc = ColorCorrection("test_id")
        cc.sat = 0.9

        element = cc.sat_node.build_element()

        self.assertEqual(element.tag, "SatNode")
        self.assertIsNotNone(element.find("Saturation"))

    def test_sat_legacy_tag_name(self):
        """Test SatNode uses legacy 'SATNode' tag when configured."""
        config.config.set_sat_tag_name("SATNode")

        cc = ColorCorrection("test_id")
        cc.sat = 0.9

        element = cc.sat_node.build_element()

        self.assertEqual(element.tag, "SATNode")
        self.assertIsNotNone(element.find("Saturation"))

    def test_sat_asc_tag_name(self):
        """Test SatNode uses 'ASC_SAT' tag when configured."""
        config.config.set_sat_tag_name("ASC_SAT")

        cc = ColorCorrection("test_id")
        cc.sat = 0.9

        element = cc.sat_node.build_element()

        self.assertEqual(element.tag, "ASC_SAT")
        self.assertIsNotNone(element.find("Saturation"))


if __name__ == "__main__":
    unittest.main()
