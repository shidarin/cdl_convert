#!/usr/bin/env python
"""
Tests encoding configuration for cdl_convert

Tests the configurable input and output encoding functionality, including:
- XML auto-detection from encoding declarations
- Explicit encoding override for XML files
- Non-XML file encoding handling
- CLI encoding arguments
- Unicode character preservation

REQUIREMENTS:
unittest
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Imports
import os
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

# Grab our test's path and append the cdl_convert root directory
sys.path.append("/".join(os.path.realpath(__file__).split("/")[:-2]))

import cdl_convert

# ==============================================================================
# GLOBALS - Test Data Constants
# ==============================================================================

# Latin-1 encoded XML with encoding declaration
LATIN1_CC_XML = r"""<?xml version="1.0" encoding="ISO-8859-1"?>
<ColorCorrection id="test_éñü">
    <SOPNode>
        <Slope>1.5 0.9 1.2</Slope>
        <Offset>0.1 -0.05 0.03</Offset>
        <Power>1.1 0.95 1.05</Power>
    </SOPNode>
    <SatNode>
        <Saturation>0.85</Saturation>
    </SatNode>
    <Description>Test with special chars: café, niño</Description>
</ColorCorrection>
"""

# UTF-8 encoded XML without encoding declaration
UTF8_CC_XML = r"""<?xml version="1.0"?>
<ColorCorrection id="test_中文">
    <SOPNode>
        <Slope>1.3 1.1 0.8</Slope>
        <Offset>-0.02 0.15 -0.1</Offset>
        <Power>0.9 1.2 1.05</Power>
    </SOPNode>
    <SatNode>
        <Saturation>1.15</Saturation>
    </SatNode>
    <Description>Unicode test: 中文 日本語 한글</Description>
</ColorCorrection>
"""

# Latin-1 encoded Nuke file (non-XML format)
LATIN1_NK = r"""OCIOCDLTransform {
  slope {1.4 0.85 1.25}
  offset {0.05 -0.1 0.02}
  power {1.15 0.92 1.08}
  saturation 0.95
  name café_niño
}
"""

# ==============================================================================
# TEST CLASSES
# ==============================================================================


class TestXMLEncodingAutoDetection(unittest.TestCase):
    """Test XML encoding auto-detection from XML declarations"""

    def setUp(self):
        """Create temp files with different encodings"""
        # Latin-1 XML with encoding declaration
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".cc"
        ) as f:
            f.write(LATIN1_CC_XML.encode("latin-1"))
            self.latin1_file = f.name

        # UTF-8 XML without encoding declaration
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".cc"
        ) as f:
            f.write(UTF8_CC_XML.encode("utf-8"))
            self.utf8_file = f.name

    def tearDown(self):
        """Clean up temp files and reset config"""
        os.remove(self.latin1_file)
        os.remove(self.utf8_file)
        cdl_convert.reset_all()
        # Reset encoding config to defaults
        cdl_convert.config.config.input_encoding = None
        cdl_convert.config.config.output_encoding = "utf-8"

    def test_xml_auto_detect_latin1_declaration(self):
        """Test XML auto-detection with Latin-1 encoding declaration"""
        # Parse without setting input_encoding (should auto-detect)
        cc = cdl_convert.parse_cc(self.latin1_file)

        # Verify special characters decoded correctly
        self.assertEqual(cc.id, "test_éñü")
        self.assertIn("café", cc.desc[0])
        self.assertIn("niño", cc.desc[0])

        # Verify CDL values were parsed correctly
        self.assertEqual(
            cc.slope, (Decimal("1.5"), Decimal("0.9"), Decimal("1.2"))
        )
        self.assertEqual(
            cc.offset, (Decimal("0.1"), Decimal("-0.05"), Decimal("0.03"))
        )
        self.assertEqual(
            cc.power, (Decimal("1.1"), Decimal("0.95"), Decimal("1.05"))
        )
        self.assertEqual(cc.sat, Decimal("0.85"))

    def test_xml_auto_detect_utf8_no_declaration(self):
        """Test XML auto-detection defaults to UTF-8 without declaration"""
        # Parse without setting input_encoding (should default to UTF-8)
        cc = cdl_convert.parse_cc(self.utf8_file)

        # Verify unicode characters preserved
        self.assertEqual(cc.id, "test_中文")
        self.assertIn("中文", cc.desc[0])
        self.assertIn("日本語", cc.desc[0])
        self.assertIn("한글", cc.desc[0])

        # Verify CDL values were parsed correctly
        self.assertEqual(
            cc.slope, (Decimal("1.3"), Decimal("1.1"), Decimal("0.8"))
        )
        self.assertEqual(
            cc.offset, (Decimal("-0.02"), Decimal("0.15"), Decimal("-0.1"))
        )
        self.assertEqual(
            cc.power, (Decimal("0.9"), Decimal("1.2"), Decimal("1.05"))
        )
        self.assertEqual(cc.sat, Decimal("1.15"))


class TestXMLEncodingOverride(unittest.TestCase):
    """Test explicit encoding override for XML files"""

    def setUp(self):
        """Create temp file with mismatched declaration"""
        # Create XML with UTF-8 declaration but Latin-1 bytes
        xml_with_wrong_declaration = r"""<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="test_override">
    <SOPNode>
        <Slope>1.0 1.0 1.0</Slope>
        <Offset>0.0 0.0 0.0</Offset>
        <Power>1.0 1.0 1.0</Power>
    </SOPNode>
    <SatNode>
        <Saturation>1.0</Saturation>
    </SatNode>
    <Description>Override test: café</Description>
</ColorCorrection>
"""
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".cc"
        ) as f:
            # Write as Latin-1 despite UTF-8 declaration
            f.write(xml_with_wrong_declaration.encode("latin-1"))
            self.filename = f.name

    def tearDown(self):
        """Clean up temp file and reset config"""
        os.remove(self.filename)
        cdl_convert.reset_all()
        # Reset encoding config to defaults
        cdl_convert.config.config.input_encoding = None
        cdl_convert.config.config.output_encoding = "utf-8"

    def test_xml_encoding_override(self):
        """Test that explicit encoding overrides XML declaration"""
        # Set input_encoding to override the (wrong) declaration
        cdl_convert.config.config.input_encoding = "latin-1"

        # Parse with override
        cc = cdl_convert.parse_cc(self.filename)

        # Verify special characters decoded correctly with override
        self.assertIn("café", cc.desc[0])

        # Verify CDL values were parsed correctly
        self.assertEqual(
            cc.slope, (Decimal("1.0"), Decimal("1.0"), Decimal("1.0"))
        )
        self.assertEqual(
            cc.offset, (Decimal("0.0"), Decimal("0.0"), Decimal("0.0"))
        )
        self.assertEqual(
            cc.power, (Decimal("1.0"), Decimal("1.0"), Decimal("1.0"))
        )
        self.assertEqual(cc.sat, Decimal("1.0"))


class TestNonXMLInputEncoding(unittest.TestCase):
    """Test encoding configuration for non-XML formats"""

    def setUp(self):
        """Create temp Nuke file with Latin-1 encoding"""
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".nk"
        ) as f:
            f.write(LATIN1_NK.encode("latin-1"))
            self.filename = f.name

    def tearDown(self):
        """Clean up temp file and reset config"""
        os.remove(self.filename)
        cdl_convert.reset_all()
        # Reset encoding config to defaults
        cdl_convert.config.config.input_encoding = None
        cdl_convert.config.config.output_encoding = "utf-8"

    def test_non_xml_input_encoding(self):
        """Test _read_file_with_encoding with Latin-1 encoding"""
        # Set input_encoding to Latin-1
        cdl_convert.config.config.input_encoding = "latin-1"

        # Parse Nuke file
        cc = cdl_convert.parse_nk(self.filename)

        # Verify file was parsed successfully with Latin-1 encoding
        self.assertEqual(cc.id, "café_niño")
        # Verify CDL values were parsed correctly
        self.assertEqual(
            cc.slope, (Decimal("1.4"), Decimal("0.85"), Decimal("1.25"))
        )
        self.assertEqual(
            cc.offset, (Decimal("0.05"), Decimal("-0.1"), Decimal("0.02"))
        )
        self.assertEqual(
            cc.power, (Decimal("1.15"), Decimal("0.92"), Decimal("1.08"))
        )
        self.assertEqual(cc.sat, Decimal("0.95"))


class TestOutputEncoding(unittest.TestCase):
    """Test output encoding configuration"""

    def setUp(self):
        """Create a ColorCorrection with unicode characters"""
        self.cc = cdl_convert.ColorCorrection(id="test_unicode_éñü")
        self.cc.desc = "Unicode test: café, niño, 中文"
        self.cc.slope = [1.0, 1.0, 1.0]
        self.cc.offset = [0.0, 0.0, 0.0]
        self.cc.power = [1.0, 1.0, 1.0]
        self.cc.sat = 1.0

        # Create temp output file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".cc"
        )
        self.filename = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """Clean up temp file and reset config"""
        os.remove(self.filename)
        cdl_convert.reset_all()
        # Reset encoding config to defaults
        cdl_convert.config.config.input_encoding = None
        cdl_convert.config.config.output_encoding = "utf-8"

    def test_output_encoding_latin1(self):
        """Test writing with Latin-1 output encoding"""
        # Set output_encoding to Latin-1
        cdl_convert.config.config.output_encoding = "latin-1"

        # Write the file
        self.cc._file_out = Path(self.filename)
        cdl_convert.write_cc(self.cc)

        # Read back with Latin-1 encoding
        with open(self.filename, encoding="latin-1") as f:
            content = f.read()

        # Verify Latin-1 characters preserved
        self.assertIn("éñü", content)
        self.assertIn("café", content)
        self.assertIn("niño", content)

    def test_output_encoding_utf8(self):
        """Test writing with UTF-8 output encoding (default)"""
        # Use default UTF-8 encoding
        cdl_convert.config.config.output_encoding = "utf-8"

        # Write the file
        self.cc._file_out = Path(self.filename)
        cdl_convert.write_cc(self.cc)

        # Read back with UTF-8 encoding
        with open(self.filename, encoding="utf-8") as f:
            content = f.read()

        # Verify all unicode characters preserved
        self.assertIn("éñü", content)
        self.assertIn("café", content)
        self.assertIn("niño", content)
        self.assertIn("中文", content)


class TestDefaultEncodingBehavior(unittest.TestCase):
    """Test default encoding behavior without explicit configuration"""

    def setUp(self):
        """Create temp files and ensure config is at defaults"""
        # Reset config to defaults before each test
        cdl_convert.config.config.input_encoding = None
        cdl_convert.config.config.output_encoding = "utf-8"

        # UTF-8 XML without declaration
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".cc"
        ) as f:
            f.write(UTF8_CC_XML.encode("utf-8"))
            self.xml_file = f.name

        # UTF-8 Nuke file
        nk_content = r"""OCIOCDLTransform {
  slope {1.5 0.7 1.1}
  offset {0.0 0.5 0.0}
  power {1.0 0.5 1.0}
  saturation 1.9
  name test_default
}
"""
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".nk"
        ) as f:
            f.write(nk_content.encode("utf-8"))
            self.nk_file = f.name

    def tearDown(self):
        """Clean up temp files and reset config"""
        os.remove(self.xml_file)
        os.remove(self.nk_file)
        cdl_convert.reset_all()
        # Reset encoding config to defaults
        cdl_convert.config.config.input_encoding = None
        cdl_convert.config.config.output_encoding = "utf-8"

    def test_default_xml_auto_detection(self):
        """Test XML files use auto-detection by default"""
        # Don't set input_encoding (should be None by default)
        self.assertIsNone(cdl_convert.config.config.input_encoding)

        # Parse XML file
        cc = cdl_convert.parse_cc(self.xml_file)

        # Verify unicode characters preserved with auto-detection
        self.assertEqual(cc.id, "test_中文")
        self.assertIn("中文", cc.desc[0])

        # Verify CDL values were parsed correctly
        self.assertEqual(
            cc.slope, (Decimal("1.3"), Decimal("1.1"), Decimal("0.8"))
        )
        self.assertEqual(
            cc.offset, (Decimal("-0.02"), Decimal("0.15"), Decimal("-0.1"))
        )
        self.assertEqual(
            cc.power, (Decimal("0.9"), Decimal("1.2"), Decimal("1.05"))
        )
        self.assertEqual(cc.sat, Decimal("1.15"))

    def test_default_non_xml_utf8(self):
        """Test non-XML files use UTF-8 by default"""
        # Don't set input_encoding (should be None, which means UTF-8 for non-XML)
        self.assertIsNone(cdl_convert.config.config.input_encoding)

        # Parse Nuke file
        cc = cdl_convert.parse_nk(self.nk_file)

        # Verify parsing succeeded with UTF-8 default
        self.assertEqual(cc.id, "test_default")

        # Verify CDL values were parsed correctly
        self.assertEqual(
            cc.slope, (Decimal("1.5"), Decimal("0.7"), Decimal("1.1"))
        )
        self.assertEqual(
            cc.offset, (Decimal("0.0"), Decimal("0.5"), Decimal("0.0"))
        )
        self.assertEqual(
            cc.power, (Decimal("1.0"), Decimal("0.5"), Decimal("1.0"))
        )
        self.assertEqual(cc.sat, Decimal("1.9"))


class TestCLIEncodingArguments(unittest.TestCase):
    """Test CLI encoding arguments"""

    def setUp(self):
        """Create temp files for CLI testing"""
        # Latin-1 input file
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".cc"
        ) as f:
            f.write(LATIN1_CC_XML.encode("latin-1"))
            self.input_file = f.name

        # Output file
        self.output_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".cc"
        ).name

    def tearDown(self):
        """Clean up temp files and reset config"""
        os.remove(self.input_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        cdl_convert.reset_all()
        # Reset encoding config to defaults
        cdl_convert.config.config.input_encoding = None
        cdl_convert.config.config.output_encoding = "utf-8"

    def test_cli_input_encoding_argument(self):
        """Test --input-encoding CLI argument"""
        # Simulate CLI call with --input-encoding
        sys.argv = [
            "cdl_convert",
            self.input_file,
            "--input-encoding",
            "latin-1",
        ]

        # Parse arguments
        cdl_convert.cdl_convert.parse_args()

        # Verify encoding was set in config
        self.assertEqual(cdl_convert.config.config.input_encoding, "latin-1")

        # Parse the file
        cc = cdl_convert.parse_cc(self.input_file)

        # Verify special characters decoded correctly
        self.assertEqual(cc.id, "test_éñü")
        self.assertIn("café", cc.desc[0])

    def test_cli_output_encoding_argument(self):
        """Test --output-encoding CLI argument"""
        # Create a ColorCorrection with unicode
        cc = cdl_convert.ColorCorrection(id="test_output")
        cc.desc = "Test: café"
        cc.slope = [1.0, 1.0, 1.0]
        cc.offset = [0.0, 0.0, 0.0]
        cc.power = [1.0, 1.0, 1.0]
        cc.sat = 1.0

        # Create temp output directory
        import tempfile

        output_dir = tempfile.mkdtemp()

        try:
            # Simulate CLI call with --output-encoding
            sys.argv = [
                "cdl_convert",
                self.input_file,
                "-d",
                output_dir,
                "--output-encoding",
                "latin-1",
            ]

            # Parse arguments
            cdl_convert.cdl_convert.parse_args()

            # Verify encoding was set in config
            self.assertEqual(
                cdl_convert.config.config.output_encoding, "latin-1"
            )

            # Write the file
            output_file = os.path.join(output_dir, "test_output.cc")
            cc._file_out = Path(output_file)
            cdl_convert.write_cc(cc)

            # Read back with Latin-1 encoding
            with open(output_file, encoding="latin-1") as f:
                content = f.read()

            # Verify Latin-1 characters are readable
            self.assertIn("café", content)

            # Read as bytes to verify the actual encoding declaration
            with open(output_file, "rb") as f:
                raw_content = f.read()

            # Verify the XML declaration uses the XML standard encoding name
            # (latin-1 should be normalized to ISO-8859-1)
            self.assertIn(b'encoding="ISO-8859-1"', raw_content)
        finally:
            # Clean up output directory
            import shutil

            shutil.rmtree(output_dir, ignore_errors=True)


class TestUnicodeCharacterHandling(unittest.TestCase):
    """Test comprehensive unicode character handling"""

    def setUp(self):
        """Create ColorCorrection with diverse unicode characters"""
        self.cc = cdl_convert.ColorCorrection(id="test_emoji_🎬")
        self.cc.desc = "Unicode: 中文 日本語 한글 العربية עברית 🎨 🎭 🎪"
        self.cc.slope = [1.2, 0.9, 1.1]
        self.cc.offset = [0.05, -0.03, 0.02]
        self.cc.power = [1.05, 0.98, 1.02]
        self.cc.sat = 1.1

        # Create temp output file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".cc"
        )
        self.filename = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """Clean up temp file and reset config"""
        os.remove(self.filename)
        cdl_convert.reset_all()
        # Reset encoding config to defaults
        cdl_convert.config.config.input_encoding = None
        cdl_convert.config.config.output_encoding = "utf-8"

    def test_unicode_emoji_cjk_preservation(self):
        """Test that emoji and CJK characters are preserved through write/read cycle"""
        self.cc._file_out = Path(self.filename)
        cdl_convert.write_cc(self.cc)

        # Read back
        cc_read = cdl_convert.parse_cc(self.filename)

        # Verify all unicode characters preserved (ID may have suffix added)
        self.assertIn("test_emoji_🎬", cc_read.id)
        self.assertIn("中文", cc_read.desc[0])
        self.assertIn("日本語", cc_read.desc[0])
        self.assertIn("한글", cc_read.desc[0])
        self.assertIn("العربية", cc_read.desc[0])
        self.assertIn("עברית", cc_read.desc[0])
        self.assertIn("🎨", cc_read.desc[0])
        self.assertIn("🎭", cc_read.desc[0])
        self.assertIn("🎪", cc_read.desc[0])

        # Verify CDL values preserved
        self.assertEqual(
            cc_read.slope, (Decimal("1.2"), Decimal("0.9"), Decimal("1.1"))
        )
        self.assertEqual(
            cc_read.offset, (Decimal("0.05"), Decimal("-0.03"), Decimal("0.02"))
        )
        self.assertEqual(
            cc_read.power, (Decimal("1.05"), Decimal("0.98"), Decimal("1.02"))
        )
        self.assertEqual(cc_read.sat, Decimal("1.1"))


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    unittest.main()
