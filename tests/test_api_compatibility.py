#!/usr/bin/env python
"""
API Compatibility Regression Tests

Tests to ensure that the modernized CDL Convert maintains API compatibility
and produces consistent CDL format outputs compared to the original behavior.

REQUIREMENTS:
- All public API methods must maintain compatibility
- CDL format outputs must be consistent with original behavior
- No breaking changes to existing functionality
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import os
import sys
import tempfile
import unittest
from decimal import Decimal
from io import StringIO
from pathlib import Path

# Add the cdl_convert root directory to Python path
sys.path.append("/".join(os.path.realpath(__file__).split("/")[:-2]))

import cdl_convert
from cdl_convert import (
    ColorCollection,
    ColorCorrection,
    SatNode,
    SopNode,
    ValidationError,
    parse_file,
    sanity_check,
    to_decimal,
    write_cc,
    write_ccc,
    write_cdl,
    write_rnh_cdl,
)

# ==============================================================================
# TEST CLASSES
# ==============================================================================


class TestPublicAPICompatibility(unittest.TestCase):
    """Test that all public API methods maintain compatibility"""

    def setUp(self):
        """Set up test fixtures"""
        cdl_convert.reset_all()
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures"""
        cdl_convert.reset_all()
        # Clean up temp files
        for file in self.temp_dir.glob("*"):
            file.unlink()
        self.temp_dir.rmdir()

    def test_color_correction_api_compatibility(self):
        """Test ColorCorrection class API compatibility"""
        # Test basic instantiation
        cc = ColorCorrection(id="test_cc")
        self.assertEqual(cc.id, "test_cc")

        # Test with input_file parameter
        cc_with_file = ColorCorrection(id="test_cc2", input_file="test.cc")
        self.assertEqual(cc_with_file.id, "test_cc2")

        # Test slope, offset, power, sat properties
        cc.slope = [1.0, 1.0, 1.0]
        cc.offset = [0.0, 0.0, 0.0]
        cc.power = [1.0, 1.0, 1.0]
        cc.sat = 1.0

        # Values are stored as Decimal tuples, not lists
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

        # Test that sop_node and sat_node are accessible
        self.assertIsInstance(cc.sop_node, SopNode)
        self.assertIsInstance(cc.sat_node, SatNode)

    def test_color_collection_api_compatibility(self):
        """Test ColorCollection class API compatibility"""
        # Test basic instantiation
        ccc = ColorCollection()
        self.assertIsInstance(ccc, ColorCollection)

        # Test with input_file parameter
        ccc_with_file = ColorCollection(input_file="test.ccc")
        self.assertIsInstance(ccc_with_file, ColorCollection)

        # Test append_child method
        cc = ColorCorrection(id="child_cc")
        ccc.append_child(cc)
        self.assertIn(cc, ccc.color_corrections)

        # Test append_children method
        cc2 = ColorCorrection(id="child_cc2")
        cc3 = ColorCorrection(id="child_cc3")
        ccc.append_children([cc2, cc3])
        self.assertIn(cc2, ccc.color_corrections)
        self.assertIn(cc3, ccc.color_corrections)

    def test_parse_functions_api_compatibility(self):
        """Test that parse functions maintain API compatibility"""
        # Test that parse_file function exists and is callable
        self.assertTrue(callable(parse_file))

        # Test that individual parse functions exist
        from cdl_convert import (
            parse_ale,
            parse_cc,
            parse_ccc,
            parse_cdl,
            parse_flex,
            parse_rnh_cdl,
        )

        parse_functions = [
            parse_ale,
            parse_cc,
            parse_ccc,
            parse_cdl,
            parse_flex,
            parse_rnh_cdl,
        ]
        for parse_func in parse_functions:
            self.assertTrue(callable(parse_func))

    def test_write_functions_api_compatibility(self):
        """Test that write functions maintain API compatibility"""
        write_functions = [write_cc, write_ccc, write_cdl, write_rnh_cdl]
        for write_func in write_functions:
            self.assertTrue(callable(write_func))

    def test_utility_functions_api_compatibility(self):
        """Test utility functions API compatibility"""
        # Test sanity_check function
        cc = ColorCorrection(id="test_cc")
        cc.slope = [1.0, 1.0, 1.0]
        cc.offset = [0.0, 0.0, 0.0]
        cc.power = [1.0, 1.0, 1.0]
        cc.sat = 1.0

        result = sanity_check(cc)
        self.assertIsInstance(result, bool)

        # Test to_decimal function
        decimal_result = to_decimal("1.5")
        self.assertIsInstance(decimal_result, Decimal)
        self.assertEqual(decimal_result, Decimal("1.5"))

    def test_reset_all_function_compatibility(self):
        """Test reset_all function maintains compatibility"""
        # Create some objects
        cc1 = ColorCorrection(id="cc1")
        cc2 = ColorCorrection(id="cc2")
        ColorCollection()

        # Verify they exist in member dictionaries (members is a dict, not list)
        self.assertIn("cc1", ColorCorrection.members)
        self.assertIn("cc2", ColorCorrection.members)
        self.assertEqual(ColorCorrection.members["cc1"], cc1)
        self.assertEqual(ColorCorrection.members["cc2"], cc2)

        # Reset all
        cdl_convert.reset_all()

        # Verify member lists are cleared
        self.assertEqual(len(ColorCorrection.members), 0)
        self.assertEqual(len(ColorCollection.members), 0)


class TestCDLFormatOutputConsistency(unittest.TestCase):
    """Test that CDL format outputs are consistent with expected behavior"""

    def setUp(self):
        """Set up test fixtures"""
        cdl_convert.reset_all()
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create a standard test ColorCorrection
        self.test_cc = ColorCorrection(id="test_output_cc")
        self.test_cc.slope = [1.02401, 1.00804, 0.89562]
        self.test_cc.offset = [-0.00864, -0.00261, 0.03612]
        self.test_cc.power = [1.0, 1.0, 1.0]
        self.test_cc.sat = 1.2

    def tearDown(self):
        """Clean up test fixtures"""
        cdl_convert.reset_all()
        # Clean up temp files
        for file in self.temp_dir.glob("*"):
            file.unlink()
        self.temp_dir.rmdir()

    def test_cc_format_output_consistency(self):
        """Test that CC format output is consistent"""
        # Use determine_dest method to set file_out
        self.test_cc.determine_dest("cc", self.temp_dir)

        # Write the CC file
        write_cc(self.test_cc)

        # Verify file was created (determine_dest creates filename based on ID)
        expected_file = self.temp_dir / "test_output_cc.cc"
        self.assertTrue(expected_file.exists())

        # Read and verify content structure
        with open(expected_file, encoding="utf-8") as f:
            content = f.read()

        # Verify XML structure
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', content)
        self.assertIn('<ColorCorrection id="test_output_cc">', content)
        self.assertIn("<SOPNode>", content)
        self.assertIn("<Slope>1.02401 1.00804 0.89562</Slope>", content)
        self.assertIn("<Offset>-0.00864 -0.00261 0.03612</Offset>", content)
        self.assertIn("<Power>1.0 1.0 1.0</Power>", content)
        self.assertIn("<SATNode>", content)
        self.assertIn("<Saturation>1.2</Saturation>", content)

    def test_ccc_format_output_consistency(self):
        """Test that CCC format output is consistent"""
        # Create a ColorCollection with our test CC
        ccc = ColorCollection()
        ccc.append_child(self.test_cc)
        # Use determine_dest method to set file_out
        ccc.determine_dest(self.temp_dir)

        # Write the CCC file
        write_ccc(ccc)

        # Verify file was created - check what files exist in temp_dir
        created_files = list(self.temp_dir.glob("*.ccc"))
        self.assertTrue(
            len(created_files) > 0, f"No CCC files created in {self.temp_dir}"
        )

        # Read and verify content structure
        with open(created_files[0], encoding="utf-8") as f:
            content = f.read()

        # Verify XML structure
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', content)
        self.assertIn("<ColorCorrectionCollection", content)
        self.assertIn('xmlns="urn:ASC:CDL:v1.01"', content)
        self.assertIn('<ColorCorrection id="test_output_cc">', content)
        self.assertIn("<SOPNode>", content)
        self.assertIn("<Slope>1.02401 1.00804 0.89562</Slope>", content)

    def test_cdl_format_output_consistency(self):
        """Test that CDL format output is consistent"""
        # Create a ColorCollection with our test CC
        ccc = ColorCollection()
        ccc.append_child(self.test_cc)
        # Set type to cdl before determining destination
        ccc.type = "cdl"
        # Use determine_dest method to set file_out
        ccc.determine_dest(self.temp_dir)

        # Write the CDL file
        write_cdl(ccc)

        # Verify file was created - ColorCollection creates files based on input filename or index
        created_files = list(self.temp_dir.glob("*.cdl"))
        if len(created_files) == 0:
            # Check all files in temp_dir for debugging
            all_files = list(self.temp_dir.glob("*"))
            self.fail(
                f"No CDL files created in {self.temp_dir}. Files found: {all_files}"
            )
        self.assertTrue(len(created_files) > 0)

        # Read and verify content structure
        with open(created_files[0], encoding="utf-8") as f:
            content = f.read()

        # Verify XML structure (CDL format includes ColorDecisionList)
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', content)
        self.assertIn("<ColorDecisionList", content)
        self.assertIn('xmlns="urn:ASC:CDL:v1.01"', content)

    def test_rnh_cdl_format_output_consistency(self):
        """Test that RNH CDL (space-separated) format output is consistent"""
        # Use determine_dest method to set file_out
        self.test_cc.determine_dest("cdl", self.temp_dir)

        # Write the RNH CDL file
        write_rnh_cdl(self.test_cc)

        # Verify file was created (determine_dest creates filename based on ID)
        expected_file = self.temp_dir / "test_output_cc.cdl"
        self.assertTrue(expected_file.exists())

        # Read and verify content
        with open(expected_file, encoding="utf-8") as f:
            content = f.read().strip()

        # Verify space-separated format
        expected_values = [
            "1.02401",
            "1.00804",
            "0.89562",  # slope
            "-0.00864",
            "-0.00261",
            "0.03612",  # offset
            "1.0",
            "1.0",
            "1.0",  # power
            "1.2",  # saturation
        ]
        expected_content = " ".join(expected_values)
        self.assertEqual(content, expected_content)

    def test_numeric_precision_consistency(self):
        """Test that numeric precision is maintained consistently"""
        # Test with high precision values
        high_precision_cc = ColorCorrection(id="precision_test")
        high_precision_cc.slope = [1.123456789, 0.987654321, 1.555555555]
        high_precision_cc.offset = [0.000000001, -0.000000002, 0.000000003]
        high_precision_cc.power = [1.0, 1.0, 1.0]
        high_precision_cc.sat = 0.999999999

        # Test RNH CDL output for precision
        # Use determine_dest method to set file_out
        high_precision_cc.determine_dest("cdl", self.temp_dir)
        write_rnh_cdl(high_precision_cc)

        # Find the actual output file
        output_file = self.temp_dir / "precision_test.cdl"
        with open(output_file, encoding="utf-8") as f:
            content = f.read().strip()

        # Verify that precision is maintained in fixed-point notation (no scientific notation)
        self.assertIn("1.123456789", content)
        self.assertIn("0.987654321", content)
        self.assertIn(
            "0.000000001", content
        )  # Should be fixed-point, not scientific notation
        self.assertIn("-0.000000002", content)
        self.assertIn("0.000000003", content)
        self.assertIn("0.999999999", content)

        # Ensure no scientific notation is present
        self.assertNotIn("E-", content)
        self.assertNotIn("e-", content)


class TestBackwardCompatibilityBehavior(unittest.TestCase):
    """Test backward compatibility of behavior patterns"""

    def setUp(self):
        """Set up test fixtures"""
        cdl_convert.reset_all()
        self.stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        """Clean up test fixtures"""
        sys.stdout = self.stdout
        cdl_convert.reset_all()

    def test_sanity_check_behavior_compatibility(self):
        """Test that sanity_check behavior is consistent"""
        # Test with good values (should return True)
        good_cc = ColorCorrection(id="good_cc")
        good_cc.slope = [1.2, 0.8, 1.1]
        good_cc.offset = [0.1, -0.05, 0.02]
        good_cc.power = [1.1, 0.9, 1.0]
        good_cc.sat = 1.1

        result = sanity_check(good_cc)
        self.assertTrue(result)

        # Test with questionable values (should return False and print warnings)
        bad_cc = ColorCorrection(id="bad_cc")
        bad_cc.slope = [0.05, 3.5, 1.0]  # Values outside typical range
        bad_cc.offset = [0.0, 0.0, 0.0]
        bad_cc.power = [1.0, 1.0, 1.0]
        bad_cc.sat = 1.0

        result = sanity_check(bad_cc)
        self.assertFalse(result)

        # Verify warning messages were printed
        output = sys.stdout.getvalue()
        self.assertIn("bad_cc", output)
        self.assertIn("Slope", output)

    def test_member_tracking_behavior_compatibility(self):
        """Test that member tracking behavior is consistent"""
        # Create objects and verify they're tracked
        cc1 = ColorCorrection(id="tracked_cc1")
        cc2 = ColorCorrection(id="tracked_cc2")
        ColorCollection()

        # Verify member tracking (members is a dict keyed by ID)
        self.assertIn("tracked_cc1", ColorCorrection.members)
        self.assertIn("tracked_cc2", ColorCorrection.members)
        self.assertEqual(ColorCorrection.members["tracked_cc1"], cc1)
        self.assertEqual(ColorCorrection.members["tracked_cc2"], cc2)

        # Test unique ID enforcement - behavior depends on halt_on_error setting
        original_halt_setting = cdl_convert.config.config.halt_on_error

        try:
            # Test with halt_on_error = True (should raise exception)
            cdl_convert.config.config.halt_on_error = True
            with self.assertRaises(ValidationError):
                ColorCorrection(id="tracked_cc1")

            # Test with halt_on_error = False (should create unique ID)
            cdl_convert.config.config.halt_on_error = False
            cc3 = ColorCorrection(id="tracked_cc1")  # Should get modified ID
            self.assertNotEqual(cc3.id, "tracked_cc1")  # ID should be modified
            self.assertTrue(
                cc3.id.startswith("tracked_cc1")
            )  # Should be based on original

        finally:
            # Restore original setting
            cdl_convert.config.config.halt_on_error = original_halt_setting

    def test_file_path_handling_compatibility(self):
        """Test that file path handling maintains compatibility"""
        # Test with string paths (should still work, but returns resolved path)
        cc_string_path = ColorCorrection(
            id="string_path_cc", input_file="test.cc"
        )
        # file_in returns resolved absolute path
        self.assertTrue(str(cc_string_path.file_in).endswith("test.cc"))

        # Test with Path objects (should work)
        from pathlib import Path

        cc_path_obj = ColorCorrection(
            id="path_obj_cc", input_file=Path("test2.cc")
        )
        # file_in returns resolved absolute path
        self.assertTrue(str(cc_path_obj.file_in).endswith("test2.cc"))

    def test_decimal_conversion_compatibility(self):
        """Test that decimal conversion behavior is consistent"""
        # Test various input types
        test_cases = [
            ("1.5", Decimal("1.5")),
            (1.5, Decimal("1.5")),
            (1, Decimal("1.0")),
            ("  2.0  ", Decimal("2.0")),  # With whitespace
        ]

        for input_val, expected in test_cases:
            result = to_decimal(input_val)
            self.assertEqual(result, expected)

        # Test error cases
        with self.assertRaises(TypeError):
            to_decimal("not_a_number")

        with self.assertRaises(ValueError):
            to_decimal(["1.0", "2.0"])  # Unsupported type


class TestCLICompatibility(unittest.TestCase):
    """Test CLI interface compatibility"""

    def setUp(self):
        """Set up test fixtures"""
        self.sysargv = sys.argv
        self.stdout = sys.stdout
        sys.stdout = StringIO()
        cdl_convert.reset_all()

    def tearDown(self):
        """Clean up test fixtures"""
        sys.stdout = self.stdout
        sys.argv = self.sysargv
        cdl_convert.reset_all()

    def test_cli_argument_parsing_compatibility(self):
        """Test that CLI argument parsing maintains compatibility"""
        from cdl_convert.cdl_convert import parse_args

        # Test basic input file argument
        sys.argv = ["cdl_convert", "input.cc"]
        args = parse_args(validate_files=False)
        self.assertEqual(args.input_file, "input.cc")

        # Test input format specification
        sys.argv = ["cdl_convert", "input.file", "-i", "cc"]
        args = parse_args(validate_files=False)
        self.assertEqual(args.input, "cc")

        # Test output format specification
        sys.argv = ["cdl_convert", "input.file", "-o", "ccc"]
        args = parse_args(validate_files=False)
        self.assertEqual(args.output, ["ccc"])

        # Test multiple output formats
        sys.argv = ["cdl_convert", "input.file", "-o", "cc,ccc"]
        args = parse_args(validate_files=False)
        self.assertEqual(set(args.output), {"cc", "ccc"})

        # Test destination directory
        sys.argv = ["cdl_convert", "input.file", "-d", "/custom/path"]
        args = parse_args(validate_files=False)
        self.assertEqual(args.destination, Path("/custom/path"))

        # Test flags
        sys.argv = [
            "cdl_convert",
            "input.file",
            "--halt",
            "--check",
            "--single",
            "--no-output",
        ]
        args = parse_args(validate_files=False)
        self.assertTrue(args.check)
        self.assertTrue(args.single)
        self.assertTrue(args.no_output)

    def test_cli_error_handling_compatibility(self):
        """Test that CLI error handling maintains compatibility"""
        from cdl_convert.cdl_convert import parse_args

        # Test invalid input format
        sys.argv = ["cdl_convert", "input.file", "-i", "invalid_format"]
        with self.assertRaises(ValueError):
            parse_args()

        # Test invalid output format
        sys.argv = ["cdl_convert", "input.file", "-o", "invalid_format"]
        with self.assertRaises(ValueError):
            parse_args()


# ==============================================================================
# RUNNER
# ==============================================================================

if __name__ == "__main__":
    unittest.main()
