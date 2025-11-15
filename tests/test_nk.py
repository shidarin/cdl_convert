#!/usr/bin/env python
"""
Tests the Nuke OCIOCDLTransform format parsing and writing functions

REQUIREMENTS:

mock
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
from unittest import mock

# Grab our test's path and append the cdl_convert root directory

sys.path.append("/".join(os.path.realpath(__file__).split("/")[:-2]))

import cdl_convert
from cdl_convert.exceptions import CDLConvertError, ParseError

# ==============================================================================
# GLOBALS
# ==============================================================================

# Nuke OCIOCDLTransform node template
NK_TEMPLATE = """OCIOCDLTransform {{
  slope {{{slope}}}
  offset {{{offset}}}
  power {{{power}}}
  saturation {sat}
  name {name}
}}
"""

# ==============================================================================
# TEST CLASSES
# ==============================================================================


class TestParseNukeBasic(unittest.TestCase):
    """Tests parsing a basic Nuke OCIOCDLTransform node file"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):
        self.slope = decimalize(1.329, 0.9833, 1.003)
        self.offset = decimalize(0.011, 0.013, 0.3401)
        self.power = decimalize(0.993, 0.998, 1.0113)
        self.sat = Decimal("1.01")
        self.name = "test_node_001"

        self.file = buildNukeNode(
            self.slope, self.offset, self.power, self.sat, self.name
        )

        # Build our nk file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".nk", delete=False
        ) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdl = cdl_convert.parse_nk(self.filename)

    # ==========================================================================

    def tearDown(self):
        # Clean up temp file
        os.remove(self.filename)
        # Clear the ColorCorrection member dictionary
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testId(self):
        """Tests that id was set to the node name"""
        self.assertEqual(self.name, self.cdl.id)

    # ==========================================================================

    def testSlope(self):
        """Tests that slope was set correctly"""
        self.assertEqual(self.slope, self.cdl.slope)

    # ==========================================================================

    def testOffset(self):
        """Tests that offset was set correctly"""
        self.assertEqual(self.offset, self.cdl.offset)

    # ==========================================================================

    def testPower(self):
        """Tests that power was set correctly"""
        self.assertEqual(self.power, self.cdl.power)

    # ==========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        self.assertEqual(self.sat, self.cdl.sat)


# ==============================================================================
# FUNCTIONS
# ==============================================================================


def buildNukeNode(slope, offset, power, sat, name):
    """Builds a Nuke OCIOCDLTransform node string"""
    # Import here to avoid circular imports
    from cdl_convert.correction import _de_exponent

    slope_str = " ".join([_de_exponent(i) for i in slope])
    offset_str = " ".join([_de_exponent(i) for i in offset])
    power_str = " ".join([_de_exponent(i) for i in power])
    sat_str = _de_exponent(sat)

    return NK_TEMPLATE.format(
        slope=slope_str,
        offset=offset_str,
        power=power_str,
        sat=sat_str,
        name=name,
    )


def decimalize(*args):
    """Converts a list of floats/ints to Decimal tuple"""
    return tuple(Decimal(str(i)) for i in args)


class TestParseNukeOdd(TestParseNukeBasic):
    """Tests parsing a Nuke node with odd but valid numbers"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):
        # Test with extreme values
        self.slope = decimalize(137829.329, 4327890.9833, 3489031.003)
        self.offset = decimalize(-3424.011, -342789423.013, -4238923.11)
        self.power = decimalize(3271893.993, 0.0000998, 0.0000000000000000113)
        self.sat = Decimal("1798787.01")
        self.name = "extreme_values_node"

        self.file = buildNukeNode(
            self.slope, self.offset, self.power, self.sat, self.name
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".nk", delete=False
        ) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdl = cdl_convert.parse_nk(self.filename)


class TestParseNukeNoName(unittest.TestCase):
    """Tests parsing a Nuke node without a name attribute"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):
        self.slope = decimalize(1.2, 1.1, 1.0)
        self.offset = decimalize(0.0, 0.0, 0.0)
        self.power = decimalize(1.0, 1.0, 1.0)
        self.sat = Decimal("1.0")

        # Build node without name
        self.file = """OCIOCDLTransform {
  slope {1.2 1.1 1.0}
  offset {0.0 0.0 0.0}
  power {1.0 1.0 1.0}
  saturation 1.0
}
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".nk", delete=False
        ) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdl = cdl_convert.parse_nk(self.filename)

    # ==========================================================================

    def tearDown(self):
        os.remove(self.filename)
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testIdFromFilename(self):
        """Tests that id falls back to filename without extension"""
        expected_id = Path(self.filename).stem
        self.assertEqual(expected_id, self.cdl.id)


class TestParseNukeErrors(unittest.TestCase):
    """Tests error handling when parsing malformed Nuke files"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def tearDown(self):
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testMissingNode(self):
        """Tests that missing OCIOCDLTransform node raises ParseError"""
        content = "# This is just a comment, no node here\n"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".nk", delete=False
        ) as f:
            f.write(content)
            filename = f.name

        try:
            with self.assertRaises(ParseError) as cm:
                cdl_convert.parse_nk(filename)

            self.assertIn("No OCIOCDLTransform node found", str(cm.exception))
        finally:
            os.remove(filename)

    # ==========================================================================

    def testMissingSlope(self):
        """Tests handling of missing slope field"""
        content = """OCIOCDLTransform {
  offset {0.0 0.0 0.0}
  power {1.0 1.0 1.0}
  saturation 1.0
  name test_node
}
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".nk", delete=False
        ) as f:
            f.write(content)
            filename = f.name

        try:
            # Should not raise with halt_on_error=False (default)
            cdl = cdl_convert.parse_nk(filename)
            # Slope should be None or unity default
            self.assertIsNotNone(cdl)
        finally:
            os.remove(filename)

    # ==========================================================================

    def testInvalidValueCount(self):
        """Tests that 2 or 4+ values raises ParseError"""
        content = """OCIOCDLTransform {
  slope {1.0 1.0}
  offset {0.0 0.0 0.0}
  power {1.0 1.0 1.0}
  saturation 1.0
  name test_node
}
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".nk", delete=False
        ) as f:
            f.write(content)
            filename = f.name

        try:
            with self.assertRaises(ParseError) as cm:
                cdl_convert.parse_nk(filename)

            self.assertIn("expected 1 or 3 values", str(cm.exception))
        finally:
            os.remove(filename)


class TestWriteNukeBasic(unittest.TestCase):
    """Tests writing a basic Nuke OCIOCDLTransform node"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):
        self.slope = list(decimalize(1.329, 0.9833, 1.003))
        self.offset = list(decimalize(0.011, 0.013, 0.11))
        self.power = list(decimalize(0.993, 0.998, 1.0113))
        self.sat = Decimal("1.01")

        self.cdl = cdl_convert.ColorCorrection(
            "test_shot_001", "../theVeryBestFile.ale"
        )

        self.cdl.determine_dest("nk", "../converted/")
        self.cdl.slope = self.slope
        self.cdl.offset = self.offset
        self.cdl.power = self.power
        self.cdl.sat = self.sat

        self.file = buildNukeNode(
            self.slope, self.offset, self.power, self.sat, "test_shot_001"
        )

        self.mockOpen = mock.mock_open()

        with mock.patch("builtins.open", self.mockOpen, create=True):
            cdl_convert.write_nk(self.cdl)

    # ==========================================================================

    def tearDown(self):
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testOpen(self):
        """Tests that open was called correctly"""
        self.mockOpen.assert_called_once_with(
            self.cdl.file_out, "w", encoding="utf-8"
        )

    # ==========================================================================

    def testContent(self):
        """Tests that write_nk wrote the correct Nuke node"""
        handle = self.mockOpen()
        handle.write.assert_called_once_with(self.file)

    # ==========================================================================

    def test_write_oserror_raises_cdlconverterror(self):
        """Tests that OSError during write raises CDLConvertError"""
        self.cdl._file_out = "invalid_path/test_node.nk"

        with mock.patch(
            "builtins.open", side_effect=OSError("Permission denied")
        ):
            with self.assertRaises(CDLConvertError) as cm:
                cdl_convert.write_nk(self.cdl)

            self.assertIn("Failed to write Nuke file", str(cm.exception))
            self.assertIn("invalid_path/test_node.nk", str(cm.exception))
            self.assertIn("Permission denied", str(cm.exception))


class TestWriteNukeOdd(TestWriteNukeBasic):
    """Tests writing a Nuke node with extreme values"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):
        self.slope = list(decimalize(137829.329, 4327890.9833, 3489031.003))
        self.offset = list(decimalize(-3424.011, -342789423.013, -4238923.11))
        self.power = list(decimalize(0.993, 0.0000998, 0.0000000000000000113))
        self.sat = Decimal("1798787.01")

        self.cdl = cdl_convert.ColorCorrection(
            "extreme_node", "../theVeryBestFile.ale"
        )

        self.cdl.determine_dest("nk", "../converted/")
        self.cdl.slope = self.slope
        self.cdl.offset = self.offset
        self.cdl.power = self.power
        self.cdl.sat = self.sat

        self.file = buildNukeNode(
            self.slope, self.offset, self.power, self.sat, "extreme_node"
        )

        self.mockOpen = mock.mock_open()

        with mock.patch("builtins.open", self.mockOpen, create=True):
            cdl_convert.write_nk(self.cdl)


class TestWriteNukeNoFileOut(unittest.TestCase):
    """Tests that write_nk raises error when file_out is not set"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def tearDown(self):
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testNoFileOut(self):
        """Tests that CDLConvertError is raised when file_out is None"""
        cdl = cdl_convert.ColorCorrection("test_id", "../input.ale")
        cdl.slope = [1.0, 1.0, 1.0]

        # Don't set file_out
        with self.assertRaises(CDLConvertError) as cm:
            cdl_convert.write_nk(cdl)

        self.assertIn("Output file path not set", str(cm.exception))


# ==============================================================================
# RUNNER
# ==============================================================================
if __name__ == "__main__":
    unittest.main()
