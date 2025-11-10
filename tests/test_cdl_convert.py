#!/usr/bin/env python
"""
Tests for all of the generic functions of cdl_convert

REQUIREMENTS:

mock
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Imports
import datetime
import os
import sys
import unittest
from decimal import Decimal
from io import StringIO
from pathlib import Path
from random import randrange
from unittest import mock

# Grab our test's path and append the cdL_convert root directory

# There has to be a better method than:
# 1) Getting our current directory
# 2) Splitting into list
# 3) Splicing out the last 3 entries (filepath, test dir, tools dir)
# 4) Joining
# 5) Appending to our Python path.

sys.path.append("/".join(os.path.realpath(__file__).split("/")[:-2]))

import cdl_convert
from cdl_convert import cdl_convert as main
from cdl_convert import parse, utils, write
from cdl_convert.correction import _de_exponent, _sanitize

# ==============================================================================
# TEST CLASSES
# ==============================================================================

# _de_exponent() ==============================================================


class TestDeExponent(unittest.TestCase):
    """Throws a bunch of scientific notation at de_exponent"""

    def testNegativeExp(self):
        """Tests a basic negative value"""
        value = 0.0000000000000000113
        value_string = "0.0000000000000000113"

        self.assertEqual(value_string, _de_exponent(value))

    # ==========================================================================

    def testNegativeExp2(self):
        """Tests a basic negative value"""
        value = 0.0000998
        value_string = "0.0000998"

        self.assertEqual(value_string, _de_exponent(value))

    # ==========================================================================

    def testNegativeExp3(self):
        """Tests a basic negative value"""
        value = -0.0000000003037892378
        value_string = "-0.0000000003037892378"

        self.assertEqual(value_string, _de_exponent(value))

    # ==========================================================================

    def testPositiveExp(self):
        """Tests a basic positive value"""
        value = 76283728313300000000000000000.0
        value_string = "76283728313300000000000000000.0"

        self.assertEqual(value_string, _de_exponent(value))

    # ==========================================================================

    def testPositiveExp2(self):
        """Tests a basic positive value"""
        value = 3217892322310000000000000000000000.0
        value_string = "3217892322310000000000000000000000.0"

        self.assertEqual(value_string, _de_exponent(value))

    # ==========================================================================

    def testPositiveExp3(self):
        """Tests a basic positive value"""
        value = -1628721600000.0
        value_string = "-1628721600000.0"

        self.assertEqual(value_string, _de_exponent(value))


# _sanitize() =================================================================


class TestSanitize(unittest.TestCase):
    """Tests the helper function _sanitize()"""

    def testSpaces(self):
        """Tests that spaces are replaced with underscores"""
        result = _sanitize("banana apple blueberry")

        self.assertEqual("banana_apple_blueberry", result)

    # ==========================================================================

    def testUnderscoresOkay(self):
        """Tests that underscores pass through intact"""
        result = _sanitize("a_b_c")

        self.assertEqual("a_b_c", result)

    # ==========================================================================

    def testPeriodsOkay(self):
        """Tests that periods pass through intact"""
        result = _sanitize("a.b.c")

        self.assertEqual("a.b.c", result)

    # ==========================================================================

    def testDashesOkay(self):
        """Tests that dashes pass through intact"""
        result = _sanitize("a-b-c")

        self.assertEqual("a-b-c", result)

    # ==========================================================================

    def testLeadingPeriodRemove(self):
        """Tests that leading periods are removed"""
        result = _sanitize(".abc")

        self.assertEqual("abc", result)

    # ==========================================================================

    def testLeadingUnderscoreRemove(self):
        """Tests that leading underscores are removed"""
        result = _sanitize("_abc")

        self.assertEqual("abc", result)

    # ==========================================================================

    def testCommonBadChars(self):
        """Tests that common bad characters are removed"""
        result = _sanitize("a@$#b!)(*$%&^c`/\\\"';:<>,d")

        self.assertEqual("abcd", result)

    # ==========================================================================

    def testEmptyString(self):
        """Tests that sanitize will return and not choke on empty string"""
        result = _sanitize("")

        self.assertEqual("", result)


# sanity_check() ==============================================================


class TestSanityCheck(unittest.TestCase):
    """Tests the sanity check function"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO()
        self.cdl = cdl_convert.ColorCorrection("uniqueId", "banana.cc")

    # ==========================================================================

    def tearDown(self):
        sys.stdout = self.stdout
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testGoodRun(self):
        """Tests that if no bad values were found, sanity_check returns True"""
        self.cdl.slope = decimalize(1.2, 0.23, 2.487)
        self.cdl.offset = decimalize(-0.87, 0.987, 0.0)
        self.cdl.power = decimalize(2.97, 1.25, 1.0)
        self.cdl.sat = Decimal("2.9999")

        self.assertTrue(cdl_convert.sanity_check(self.cdl))

    # ==========================================================================

    def testSlope(self):
        """Tests that a bad slope value is reported"""
        self.cdl.slope = [0.1, 3.1, 1.5]

        self.assertFalse(cdl_convert.sanity_check(self.cdl))

        self.assertEqual(
            'The ColorCorrection "uniqueId" was given a Slope value of '
            '"0.1", which might be incorrect.\n'
            'The ColorCorrection "uniqueId" was given a Slope value of '
            '"3.1", which might be incorrect.\n',
            sys.stdout.getvalue(),
        )

    # ==========================================================================

    def testOffset(self):
        """Tests that a bad slope value is reported"""
        self.cdl.offset = decimalize(-1.01, 1.5, 0.157)

        self.assertFalse(cdl_convert.sanity_check(self.cdl))

        self.assertEqual(
            'The ColorCorrection "uniqueId" was given a Offset value of '
            '"-1.01", which might be incorrect.\n'
            'The ColorCorrection "uniqueId" was given a Offset value of '
            '"1.5", which might be incorrect.\n',
            sys.stdout.getvalue(),
        )

    # ==========================================================================

    def testPower(self):
        """Tests that a bad slope value is reported"""
        self.cdl.power = decimalize(0.1, 3.1, 1.5)

        self.assertFalse(cdl_convert.sanity_check(self.cdl))

        self.assertEqual(
            'The ColorCorrection "uniqueId" was given a Power value of '
            '"0.1", which might be incorrect.\n'
            'The ColorCorrection "uniqueId" was given a Power value of '
            '"3.1", which might be incorrect.\n',
            sys.stdout.getvalue(),
        )

    # ==========================================================================

    def testSaturation(self):
        """Tests that a bad sat value is reported"""
        self.cdl.sat = Decimal("3.01")

        self.assertFalse(cdl_convert.sanity_check(self.cdl))

        self.assertEqual(
            'The ColorCorrection "uniqueId" was given a Saturation value of '
            '"3.01", which might be incorrect.\n',
            sys.stdout.getvalue(),
        )


# parse_args() ================================================================


class TestParseArgs(unittest.TestCase):
    """Tests that arguments are being parsed correctly"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):
        self.sysargv = sys.argv
        self.stdout = sys.stdout
        sys.stdout = StringIO()
        # Reset tag names to defaults
        cdl_convert.config.config.sop_tag_name = "SOPNode"
        cdl_convert.config.config.sat_tag_name = "SatNode"

    # ==========================================================================

    def tearDown(self):
        sys.stdout = self.stdout
        sys.argv = self.sysargv
        cdl_convert.reset_all()
        # Reset tag names to defaults
        cdl_convert.config.config.sop_tag_name = "SOPNode"
        cdl_convert.config.config.sat_tag_name = "SatNode"

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testInputPositionalArg(self):
        """Tests that the input arg is positionally gotten correctly"""

        sys.argv = ["scriptname", "inputFile.txt"]

        args = main.parse_args(validate_files=False)

        self.assertEqual("inputFile.txt", args.input_file)

    # ==========================================================================

    def testGoodInputFormat(self):
        """Tests that a good input format is accepted and lowered"""

        sys.argv = ["scriptname", "inputFile", "-i", "ALE"]

        args = main.parse_args(validate_files=False)

        self.assertEqual("ale", args.input)

    # ==========================================================================

    def testBadInputFormat(self):
        """Tests that a bad input format is rejected with ValueError"""

        sys.argv = ["scriptname", "inputFile", "-i", "HUYYE"]

        self.assertRaises(ValueError, main.parse_args)

    # ==========================================================================

    def testGoodOutputFormat(self):
        """Tests that a good output format is accepted and lowered"""

        sys.argv = ["scriptname", "inputFile", "-o", "CDL"]

        args = main.parse_args(validate_files=False)

        self.assertEqual(["cdl"], args.output)

    # ==========================================================================

    def testMultipleGoodOutputFormat(self):
        """Tests that multiple good output formats are accepted and lowered"""

        sys.argv = ["scriptname", "inputFile", "-o", "CDL,CC"]

        args = main.parse_args(validate_files=False)

        self.assertEqual(["cdl", "cc"], args.output)

    # ==========================================================================

    def testBadOutputFormat(self):
        """Tests that a bad output format is rejected with ValueError"""

        sys.argv = ["scriptname", "inputFile", "-o", "HUYYE"]

        self.assertRaises(ValueError, main.parse_args)

    # ==========================================================================

    def testGoodWithBadOutputFormat(self):
        """Tests that a bad output format is rejected with ValueError"""

        sys.argv = ["scriptname", "inputFile", "-o", "cc,HUYYE"]

        self.assertRaises(ValueError, main.parse_args)

    # ==========================================================================

    def testNoProvidedOutput(self):
        """Tests that no provided output format is defaulted to cc"""

        sys.argv = ["scriptname", "inputFile"]

        args = main.parse_args(validate_files=False)

        self.assertEqual(["cc"], args.output)

    # ==========================================================================

    def testHaltOnError(self):
        """Tests that providing the --halt flag triggers halt_on_error"""
        cdl_convert.config.config.halt_on_error = False

        sys.argv = ["scriptname", "inputFile", "--halt"]

        main.parse_args(validate_files=False)

        self.assertTrue(cdl_convert.config.config.halt_on_error)

        cdl_convert.config.config.halt_on_error = False

    # ==========================================================================

    def testSanityCheck(self):
        """Tests the sanity check --check flag to be set"""

        sys.argv = ["scriptname", "inputFile", "--check"]

        args = main.parse_args(validate_files=False)

        self.assertTrue(args.check)

    # ==========================================================================

    def testSingle(self):
        """Tests that the single fileout --single flag is caught"""

        sys.argv = ["scriptname", "inputFile", "--single"]

        args = main.parse_args(validate_files=False)

        self.assertTrue(args.single)

    # ==========================================================================

    def testNoOutput(self):
        """Tests that --no-output was picked up correctly"""

        sys.argv = ["scriptname", "inputFile", "--no-output"]

        args = main.parse_args(validate_files=False)

        self.assertTrue(args.no_output)

    # ==========================================================================

    def testNoDestination(self):
        """Tests that no destination defaults to ./converted"""

        sys.argv = ["scriptname", "inputFile"]

        args = main.parse_args(validate_files=False)

        self.assertEqual(Path("./converted/"), args.destination)

    # ==========================================================================

    def testCustomDestination(self):
        """Tests that destination flag works"""

        sys.argv = ["scriptname", "inputFile", "-d", "/best/folder/"]

        args = main.parse_args(validate_files=False)

        self.assertEqual(Path("/best/folder/"), args.destination)

    # ==========================================================================

    def testSopTagDefault(self):
        """Tests that SOP tag defaults correctly"""

        sys.argv = ["scriptname", "inputFile"]

        main.parse_args(validate_files=False)

        self.assertEqual("SOPNode", cdl_convert.config.config.sop_tag_name)

    # ==========================================================================

    def testSopTagSOPNode(self):
        """Tests that --sop-tag SOPNode sets configuration"""

        sys.argv = ["scriptname", "inputFile", "--sop-tag", "SOPNode"]

        main.parse_args(validate_files=False)

        self.assertEqual("SOPNode", cdl_convert.config.config.sop_tag_name)

    # ==========================================================================

    def testSopTagASC_SOP(self):
        """Tests that --sop-tag ASC_SOP sets configuration"""

        sys.argv = ["scriptname", "inputFile", "--sop-tag", "ASC_SOP"]

        main.parse_args(validate_files=False)

        self.assertEqual("ASC_SOP", cdl_convert.config.config.sop_tag_name)

    # ==========================================================================

    def testSatTagDefault(self):
        """Tests that SAT tag defaults correctly"""

        sys.argv = ["scriptname", "inputFile"]

        main.parse_args(validate_files=False)

        self.assertEqual("SatNode", cdl_convert.config.config.sat_tag_name)

    # ==========================================================================

    def testSatTagSatNode(self):
        """Tests that --sat-tag SatNode sets configuration"""

        sys.argv = ["scriptname", "inputFile", "--sat-tag", "SatNode"]

        main.parse_args(validate_files=False)

        self.assertEqual("SatNode", cdl_convert.config.config.sat_tag_name)

    # ==========================================================================

    def testSatTagSATNode(self):
        """Tests that --sat-tag SATNode sets configuration (legacy)"""

        sys.argv = ["scriptname", "inputFile", "--sat-tag", "SATNode"]

        main.parse_args(validate_files=False)

        self.assertEqual("SATNode", cdl_convert.config.config.sat_tag_name)

    # ==========================================================================

    def testSatTagASC_SAT(self):
        """Tests that --sat-tag ASC_SAT sets configuration"""

        sys.argv = ["scriptname", "inputFile", "--sat-tag", "ASC_SAT"]

        main.parse_args(validate_files=False)

        self.assertEqual("ASC_SAT", cdl_convert.config.config.sat_tag_name)


# parse_args() ================================================================


class TestParseFile(unittest.TestCase):
    """Tests ParseFile, a convenience function"""

    def setUp(self):
        self.stored_inputs = parse.INPUT_FORMATS

    def tearDown(self):
        parse.INPUT_FORMATS = self.stored_inputs
        cdl_convert.reset_all()

    # ==========================================================================

    @mock.patch("cdl_convert.parse_ale")
    def test_ale(self, mockParse):
        """Tests that the parser is called correctly"""
        filepath = "blah.ale"
        parse.INPUT_FORMATS["ale"] = mockParse

        parse.parse_file(filepath)

        mockParse.assert_called_once_with("blah.ale")

    # ==========================================================================

    @mock.patch("cdl_convert.parse_ccc")
    def test_ccc(self, mockParse):
        """Tests that the parser is called correctly"""
        filepath = "blah.ccc"
        parse.INPUT_FORMATS["ccc"] = mockParse

        parse.parse_file(filepath)

        mockParse.assert_called_once_with("blah.ccc")

    # ==========================================================================

    @mock.patch("cdl_convert.parse_cc")
    def test_cc(self, mockParse):
        """Tests that the parser is called correctly"""
        filepath = "blah.cc"
        parse.INPUT_FORMATS["cc"] = mockParse

        parse.parse_file(filepath)

        mockParse.assert_called_once_with("blah.cc")

    # ==========================================================================

    @mock.patch("cdl_convert.parse_cdl")
    def test_cdl(self, mockParse):
        """Tests that the parser is called correctly"""
        filepath = "blah.cdl"
        parse.INPUT_FORMATS["cdl"] = mockParse

        parse.parse_file(filepath)

        mockParse.assert_called_once_with("blah.cdl")

    # ==========================================================================

    @mock.patch("cdl_convert.parse_flex")
    def test_flex(self, mockParse):
        """Tests that the parser is called correctly"""
        filepath = "blah.flex"
        parse.INPUT_FORMATS["flex"] = mockParse

        parse.parse_file(filepath)

        mockParse.assert_called_once_with("blah.flex")

    # ==========================================================================

    @mock.patch("cdl_convert.parse_rnh_cdl")
    def test_rnh_cdl(self, mockParse):
        """Tests that the parser is called correctly"""
        filepath = "blah.cdl"
        parse.INPUT_FORMATS["rcdl"] = mockParse

        parse.parse_file(filepath, "rcdl")

        mockParse.assert_called_once_with("blah.cdl")


# main() ======================================================================


class TestMain(unittest.TestCase):
    """Tests the main() function for correct execution"""

    # ==========================================================================
    # SETUP & TEARDOWN
    # ==========================================================================

    def setUp(self):
        # Note that the file doesn't really need to exist for our test purposes
        self.cdl = cdl_convert.ColorCorrection(
            id="uniqueId", input_file="../testcdl.flex"
        )
        self.ccc = cdl_convert.ColorCollection(input_file="../testcdl.flex")
        self.inputFormats = parse.INPUT_FORMATS
        self.outputFormats = write.OUTPUT_FORMATS
        self.makedirs = os.makedirs
        self.mockMakeDirs = mock.MagicMock("os.makedirs")
        self.sysargv = sys.argv
        self.stdout = sys.stdout
        sys.stdout = StringIO()
        os.makedirs = self.mockMakeDirs

    # ==========================================================================

    def tearDown(self):
        parse.INPUT_FORMATS = self.inputFormats
        write.OUTPUT_FORMATS = self.outputFormats
        sys.argv = self.sysargv
        sys.stdout = self.stdout
        os.makedirs = self.makedirs
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    # ==========================================================================
    # TESTS
    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_cc")
    def testGettingAbsolutePath(self, mockParse, mockMkdir):
        """Tests that we resolve paths to absolute paths"""

        mockParse.return_value = self.cdl
        mockWrite = mock.MagicMock()
        sys.argv = ["scriptname", "file.cc"]

        mockInputs = dict(self.inputFormats)
        mockInputs["cc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        # Mock the OUTPUT_FORMATS dictionary entry to prevent actual file writing
        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        # Verify that the parse function is called with an absolute path
        expected_path = Path("file.cc").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("pathlib.Path.exists")
    @mock.patch("cdl_convert.parse_cc")
    def testCustomDestinationPath(self, mockParse, mockExists, mockMkdir):
        """Tests that we resolve paths and create destination directories"""

        mockParse.return_value = self.cdl
        mockExists.return_value = False  # Directory doesn't exist
        sys.argv = ["scriptname", "file.cc", "-d", "/tmp/test/path/"]

        mockInputs = dict(self.inputFormats)
        mockInputs["cc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        main.main(validate_files=False)

        # Verify that mkdir was called to create the directory
        mockMkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Verify parse was called with resolved path
        expected_path = Path("file.cc").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_flex")
    def testDerivingInputTypeFlex(self, mockParse, mockMkdir):
        """Tests that input type will be derived from file extension"""

        mockParse.return_value = self.ccc
        sys.argv = ["scriptname", "file.flex"]

        mockInputs = dict(self.inputFormats)
        mockInputs["flex"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        main.main(validate_files=False)

        # Expect the resolved path, not just the filename
        expected_path = Path("file.flex").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_ale")
    def testDerivingInputTypeAle(self, mockParse, mockMkdir):
        """Tests that input type will be derived from file extension"""

        mockParse.return_value = self.ccc
        sys.argv = ["scriptname", "file.ale"]

        mockInputs = dict(self.inputFormats)
        mockInputs["ale"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        main.main(validate_files=False)

        # Expect the resolved path, not just the filename
        expected_path = Path("file.ale").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_ccc")
    def testDerivingInputTypeCCC(self, mockParse, mockMkdir):
        """Tests that input type will be derived from file extension"""

        mockParse.return_value = self.ccc
        sys.argv = ["scriptname", "file.ccc"]

        mockInputs = dict(self.inputFormats)
        mockInputs["ccc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        main.main(validate_files=False)

        # Expect the resolved path, not just the filename
        expected_path = Path("file.ccc").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_cc")
    def testDerivingInputTypeCC(self, mockParse, mockMkdir):
        """Tests that input type will be derived from file extension"""

        mockParse.return_value = self.cdl
        sys.argv = ["scriptname", "file.cc"]

        mockInputs = dict(self.inputFormats)
        mockInputs["cc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        main.main(validate_files=False)

        # Expect the resolved path, not just the filename
        expected_path = Path("file.cc").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_rnh_cdl")
    def testDerivingInputTypeCDL(self, mockParse, mockMkdir):
        """Tests that input type will be derived from file extension"""

        mockParse.return_value = self.ccc
        sys.argv = ["scriptname", "file.cdl"]

        mockInputs = dict(self.inputFormats)
        mockInputs["cdl"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        main.main(validate_files=False)

        # Expect the resolved path, not just the filename
        expected_path = Path("file.cdl").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_flex")
    def testDerivingInputTypeCased(self, mockParse, mockMkdir):
        """Tests that input type will be derived from file extension"""

        mockParse.return_value = self.ccc
        sys.argv = ["scriptname", "file.fLEx"]

        mockInputs = dict(self.inputFormats)
        mockInputs["flex"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        main.main(validate_files=False)

        # Expect the resolved path, not just the filename
        expected_path = Path("file.fLEx").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_flex")
    def testOverrideInputType(self, mockParse, mockMkdir):
        """Tests that overriding the input type happens when provided"""

        mockParse.return_value = self.ccc
        sys.argv = ["scriptname", "file.cc", "-i", "flex"]

        mockInputs = dict(self.inputFormats)
        mockInputs["flex"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        main.main(validate_files=False)

        # Expect the resolved path, not just the filename
        expected_path = Path("file.cc").resolve()
        mockParse.assert_called_once_with(expected_path)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_rnh_cdl")
    def testDetermineDestCalled(self, mockParse, mockMkdir):
        """Tests that we try and write a converted file"""

        mockParse.return_value = self.cdl
        sys.argv = ["scriptname", "file.cdl", "-i", "rcdl", "-o", "cc"]

        destination_dir = os.path.abspath("./converted/")

        mockInputs = dict(self.inputFormats)
        mockInputs["rcdl"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mock.MagicMock()
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        expected_path = Path(destination_dir) / "uniqueId.cc"
        self.assertEqual(expected_path, self.cdl.file_out)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.parse_rnh_cdl")
    def testDetermineDestCalledCollection(self, mockParse, mockMkdir):
        """Tests that we try and write a converted collection file"""

        mockParse.return_value = self.ccc
        sys.argv = ["scriptname", "file.flex", "-o", "ccc"]

        destination_dir = os.path.abspath("./converted/")

        mockInputs = dict(self.inputFormats)
        mockInputs["flex"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["ccc"] = mock.MagicMock()
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        expected_path = Path(destination_dir) / "testcdl.ccc"
        self.assertEqual(expected_path, self.ccc.file_out)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.write_cdl")
    @mock.patch("cdl_convert.parse_cdl")
    def testSingleCollectionExport(self, mockParse, mockWrite, mockMkdir):
        """Tests that with single export we export multiple times."""

        cc1 = cdl_convert.ColorCorrection(id="cc1", input_file="../cc1.cc")
        cc2 = cdl_convert.ColorCorrection(id="cc2", input_file="../cc2.cc")
        cc3 = cdl_convert.ColorCorrection(id="cc3", input_file="../cc3.cc")
        self.ccc.append_children([cc1, cc2, cc3])
        mockParse.return_value = self.ccc

        sys.argv = ["scriptname", "file.cdl", "-o", "cdl", "--single"]

        mockInputs = dict(self.inputFormats)
        mockInputs["cdl"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cdl"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        # Check that write was called three times, once for each child cc
        calls = [mock.call(cc1), mock.call(cc2), mock.call(cc3)]
        try:
            mockWrite.assert_has_calls(calls)
        except AssertionError:
            self.fail("Was not given a call for every child cc!")

        # Check that after writing, our parent is still set to the original ccc
        self.assertEqual(cc1.parent, self.ccc)

        self.assertEqual(cc2.parent, self.ccc)

        self.assertEqual(cc3.parent, self.ccc)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.write_ccc")
    @mock.patch("cdl_convert.parse_ccc")
    def testSingleCollectionExportCCC(self, mockParse, mockWrite, mockMkdir):
        """Tests that with single export we export multiple times."""

        cc1 = cdl_convert.ColorCorrection(id="cc1", input_file="../cc1.cc")
        cc2 = cdl_convert.ColorCorrection(id="cc2", input_file="../cc2.cc")
        cc3 = cdl_convert.ColorCorrection(id="cc3", input_file="../cc3.cc")
        self.ccc.append_children([cc1, cc2, cc3])
        mockParse.return_value = self.ccc

        sys.argv = ["scriptname", "file.ccc", "-o", "ccc", "--single"]

        mockInputs = dict(self.inputFormats)
        mockInputs["ccc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["ccc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        # Check that write was called three times, once for each child cc
        calls = [mock.call(cc1), mock.call(cc2), mock.call(cc3)]
        try:
            mockWrite.assert_has_calls(calls)
        except AssertionError:
            self.fail("Was not given a call for every child cc!")

        # Check that after writing, our parent is still set to the original ccc
        self.assertEqual(cc1.parent, self.ccc)

        self.assertEqual(cc2.parent, self.ccc)

        self.assertEqual(cc3.parent, self.ccc)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.cdl_convert.sanity_check")
    @mock.patch("cdl_convert.write_cc")
    @mock.patch("cdl_convert.parse_flex")
    @mock.patch("os.path.abspath")
    def testSanityCheckCalled(
        self, abspath, mockParse, mockWrite, mockSanity, mockMkdir
    ):
        """Tests that --check calls sanity check"""

        abspath.return_value = "file.cc"
        mockParse.return_value = self.cdl
        sys.argv = ["scriptname", "file.cc", "--check"]

        mockInputs = dict(self.inputFormats)
        mockInputs["cc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        mockSanity.assert_called_once_with(self.cdl)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.cdl_convert.sanity_check")
    @mock.patch("cdl_convert.write_cc")
    @mock.patch("cdl_convert.parse_flex")
    @mock.patch("os.path.abspath")
    def testSanityCheckCollectionCalled(
        self, abspath, mockParse, mockWrite, mockSanity, mockMkdir
    ):
        """Tests that --check calls sanity check with collection"""

        abspath.return_value = "file.flex"
        mockParse.return_value = self.ccc
        cdl2 = cdl_convert.ColorCorrection("45")
        cdl3 = cdl_convert.ColorCorrection("100")
        self.ccc.append_children([self.cdl, cdl2, cdl3])
        sys.argv = ["scriptname", "file.flex", "--check"]

        mockInputs = dict(self.inputFormats)
        mockInputs["flex"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        self.assertEqual(
            [mock.call(self.cdl), mock.call(cdl2), mock.call(cdl3)],
            mockSanity.call_args_list,
        )

        self.assertEqual(
            [mock.call(self.cdl), mock.call(cdl2), mock.call(cdl3)],
            mockWrite.call_args_list,
        )

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.sanity_check")
    @mock.patch("cdl_convert.write_cc")
    @mock.patch("cdl_convert.parse_flex")
    @mock.patch("os.path.abspath")
    def testSanityCheckNotCalled(
        self, abspath, mockParse, mockWrite, mockSanity, mockMkdir
    ):
        """Tests that sanity check is not called without --check"""

        abspath.return_value = "file.cc"
        mockParse.return_value = self.cdl
        sys.argv = ["scriptname", "file.cc"]

        mockInputs = dict(self.inputFormats)
        mockInputs["cc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        self.assertFalse(mockSanity.called)

    # ==========================================================================

    @mock.patch("pathlib.Path.exists")
    @mock.patch("cdl_convert.ColorCorrection.determine_dest")
    @mock.patch("cdl_convert.write_cc")
    @mock.patch("cdl_convert.parse_flex")
    def testNoOutput(self, mockParse, mockWrite, mockDest, mockPathExists):
        """Tests that we don't write a converted file"""

        # We'll set the path exists return value to equal false, so that
        # normally a new directory would be created.
        mockPathExists.return_value = False

        self.mockMakeDirs.reset_mock()

        mockParse.return_value = self.cdl
        sys.argv = ["scriptname", "file.cc", "-d", "/fakepath", "--no-output"]

        mockInputs = dict(self.inputFormats)
        mockInputs["cc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        # Because we have no output selected, a new directory should NOT
        # be created, but path exists should have still been called.
        mockPathExists.assert_called_with()
        self.assertFalse(self.mockMakeDirs.called)

        expected_path = Path("file.cc").resolve()
        mockParse.assert_called_once_with(expected_path)
        # Determine dest should have set a file_out
        # On Windows, Path('/fakepath') resolves to absolute path like 'D:/fakepath'
        expected_dest_path = Path("/fakepath").resolve()
        mockDest.assert_called_once_with("cc", expected_dest_path)
        # But the write should never have been called.
        self.assertFalse(mockWrite.called)

    # ==========================================================================

    @mock.patch("pathlib.Path.exists")
    @mock.patch("cdl_convert.ColorCollection.determine_dest")
    @mock.patch("cdl_convert.write_ccc")
    @mock.patch("cdl_convert.parse_flex")
    def testNoOutputCollection(
        self, mockParse, mockWrite, mockDest, mockPathExists
    ):
        """Tests that we don't write a converted collection file"""

        mockPathExists.return_value = True

        self.mockMakeDirs.reset_mock()

        mockParse.return_value = self.cdl
        sys.argv = [
            "scriptname",
            "file.cc",
            "-o",
            "ccc",
            "-d",
            "/fakepath",
            "--no-output",
        ]

        mockInputs = dict(self.inputFormats)
        mockInputs["cc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["ccc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        # Because we have no output selected, a new directory should NOT
        # be created, but path exists should have still been called.
        mockPathExists.assert_called_with()
        self.assertFalse(self.mockMakeDirs.called)

        expected_path = Path("file.cc").resolve()
        mockParse.assert_called_once_with(expected_path)
        # Determine dest should have set a file_out
        # On Windows, Path('/fakepath') resolves to absolute path like 'D:/fakepath'
        expected_dest_path = Path("/fakepath").resolve()
        mockDest.assert_called_once_with(expected_dest_path)
        # But the write should never have been called.
        self.assertFalse(mockWrite.called)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.write_cc")
    @mock.patch("cdl_convert.parse_rnh_cdl")
    @mock.patch("os.path.abspath")
    def testWriteCalled(self, abspath, mockParse, mockWrite, mockMkdir):
        """Tests that we try and write a converted file"""

        abspath.return_value = "file.cdl"
        mockParse.return_value = self.cdl
        sys.argv = ["scriptname", "file.cdl", "-i", "rcdl", "-o", "cc"]

        mockInputs = dict(self.inputFormats)
        mockInputs["rcdl"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        mockWrite.assert_called_once_with(self.cdl)
        mockMkdir.assert_called_once_with(parents=True, exist_ok=True)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.write_ccc")
    @mock.patch("cdl_convert.parse_rnh_cdl")
    @mock.patch("os.path.abspath")
    def testWriteCollectionCalled(
        self, abspath, mockParse, mockWrite, mockMkdir
    ):
        """Tests that we try and write a converted collection file"""

        abspath.return_value = "file.cdl"
        mockParse.return_value = self.cdl
        sys.argv = ["scriptname", "file.cdl", "-i", "rcdl", "-o", "ccc"]

        mockInputs = dict(self.inputFormats)
        mockInputs["rcdl"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["ccc"] = mockWrite
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        self.assertTrue(mockWrite.called)
        mockMkdir.assert_called_once_with(parents=True, exist_ok=True)

        self.assertEqual(
            [self.cdl], mockWrite.call_args_list[0][0][0].all_children
        )

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.write_rnh_cdl")
    @mock.patch("cdl_convert.write_cc")
    @mock.patch("cdl_convert.parse_ccc")
    @mock.patch("os.path.abspath")
    def testMultipleOutputWritesCalled(
        self, abspath, mockParse, mockWriteCC, mockWriteCDL, mockMkdir
    ):
        """Tests that we try and write a converted file"""

        abspath.return_value = "file.ccc"
        mockParse.return_value.color_corrections = [
            self.cdl,
        ]
        sys.argv = ["scriptname", "file.ccc", "-o", "cc,rcdl"]

        mockInputs = dict(self.inputFormats)
        mockInputs["ccc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mockWriteCC
        mockOutputs["rcdl"] = mockWriteCDL
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        mockWriteCC.assert_called_once_with(self.cdl)
        mockWriteCDL.assert_called_once_with(self.cdl)

    # ==========================================================================

    @mock.patch("pathlib.Path.mkdir")
    @mock.patch("cdl_convert.write_cc")
    @mock.patch("cdl_convert.parse_ccc")
    @mock.patch("os.path.abspath")
    def testMultipleWritesFromCollectionCalled(
        self, abspath, mockParse, mockWriteCC, mockMkdir
    ):
        """Tests that we try and write a converted file"""

        abspath.return_value = "file.ccc"
        mockParse.return_value.color_corrections = [
            self.cdl,
            self.cdl,
            self.cdl,
        ]
        sys.argv = ["scriptname", "file.ccc", "-o", "cc"]

        mockInputs = dict(self.inputFormats)
        mockInputs["ccc"] = mockParse
        parse.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs["cc"] = mockWriteCC
        write.OUTPUT_FORMATS = mockOutputs

        main.main(validate_files=False)

        mockWriteCC.assert_has_calls(
            [mock.call(self.cdl), mock.call(self.cdl), mock.call(self.cdl)]
        )


# Test Classes ================================================================

# TimeCodeSegment is from my SMTPE Timecode gist at:
# https://gist.github.com/shidarin/11091783


class TimeCodeSegment:
    """Generates an SMPTE timecode segment for in, out, duration

    If no args are provided, random timecode is generated and 24p assumed.

    If a duration of over 24 hours is provided, timecode will roll over.

    Args:
        hour : (int)
            The hour to start the timecode at
        minute : (int)
            The minute to start the timecode at
        second : (int)
            The second to start the timecode at
        frame : (int)
            The frame to start the timecode at
        duration : (int)
            Duration in frames (assuming 24p) If not provided, this will be
            a random number of frames up to 5 minutes.
        fps : (int)
            Frames per second as an int. Drop frame timecode is not supported.

    Attributes:
        start : (str)
            Timecode in, in the form of 10:52:55:20
            Hours, minutes, seconds, frames
        end : (str)
            Timecode out
        dur : (str)
            Timecode duration
        durFrames : (int)
            Frame duration as an int

    """

    def __init__(
        self,
        hour=None,
        minute=None,
        second=None,
        frame=None,
        duration=None,
        fps=24,
    ):
        # We compare against None so that 00 times are preserved.
        if hour is None:
            hour = randrange(00, 24)
        if minute is None:
            minute = randrange(00, 60)
        if second is None:
            second = randrange(00, 60)
        if frame is None:
            frame = randrange(00, 24)
        if duration is None:
            # We'll make these clips anything short of 5 minutes
            duration = randrange(00, fps * 300)

        # I'd like to use a time object here instead of datetime, but
        # timedelta oddly won't do any math operations with time.
        startTime = datetime.datetime(1, 1, 1, hour, minute, second)

        durSeconds = duration // fps
        durFrames = duration % fps
        frameRollover = False  # Keep track of if frames roll over.

        if durFrames + frame >= fps:
            # If our leftover frames and our starting frame add up to more than
            # 24 seconds, we need to add a second to our duration calculation.
            durSeconds += 1
            frameRollover = True

        endFrames = (frame + duration) % fps
        timeDelta = datetime.timedelta(seconds=durSeconds)

        endTime = startTime + timeDelta
        # If we adjusted duration up to get an accurate end time, we'll adjust
        # it back down now.
        if frameRollover:
            timeDelta = timeDelta - datetime.timedelta(seconds=1)
        durationTime = datetime.datetime(1, 1, 1, 0, 0, 0) + timeDelta

        # Because we had to use datetime objects, isoformat() will be returning
        # a string formatted as: '0001-01-01T12:10:25'
        # So we'll split on the T
        self.start = "{time}:{frames}".format(
            time=startTime.isoformat().split("T")[-1],
            frames=str(frame).rjust(2, "0"),
        )
        self.end = "{time}:{frames}".format(
            time=endTime.isoformat().split("T")[-1],
            frames=str(endFrames).rjust(2, "0"),
        )
        self.dur = "{time}:{frames}".format(
            time=durationTime.isoformat().split("T")[-1],
            frames=str(durFrames).rjust(2, "0"),
        )
        self.durFrames = duration


class TestTimeCodeSegment(unittest.TestCase):
    """Tests TimeCodeSegment class for correct functionality"""

    # ==========================================================================
    # TESTS
    # ==========================================================================

    def testWholeSeconds(self):
        """Tests timecode where seconds are an even multiple of frames"""
        tc = TimeCodeSegment(12, 0, 0, 0, 24)

        self.assertEqual("12:00:00:00", tc.start)

        self.assertEqual("12:00:01:00", tc.end)

        self.assertEqual("00:00:01:00", tc.dur)

    # ==========================================================================

    def testLessThanOneSecond(self):
        """Tests timecode where there's less than a second of duration"""
        tc = TimeCodeSegment(12, 0, 0, 0, 4)

        self.assertEqual("12:00:00:04", tc.end)

        self.assertEqual("00:00:00:04", tc.dur)

    # ==========================================================================

    def testMoreThanOneSecond(self):
        """Tests timecode where there's more than a second of duration"""
        tc = TimeCodeSegment(12, 0, 0, 0, 25)

        self.assertEqual("12:00:01:01", tc.end)

        self.assertEqual("00:00:01:01", tc.dur)

    # ==========================================================================

    def testUnevenCombination(self):
        """Tests timecode where there's less than a second of duration"""
        tc = TimeCodeSegment(12, 0, 0, 15, 10)

        self.assertEqual("12:00:00:15", tc.start)

        self.assertEqual("12:00:01:01", tc.end)

        self.assertEqual("00:00:00:10", tc.dur)

    # ==========================================================================

    def testAddManyHours(self):
        """Tests adding many hours, minutes and seconds of duration"""
        tc = TimeCodeSegment(0, 0, 0, 1, 1016356)

        self.assertEqual("00:00:00:01", tc.start)

        self.assertEqual("11:45:48:05", tc.end)

        self.assertEqual("11:45:48:04", tc.dur)

    # ==========================================================================

    def testRollover(self):
        """Tests timecode that rolls over 24 hours"""
        tc = TimeCodeSegment(23, 59, 59, 23, 2)

        self.assertEqual("23:59:59:23", tc.start)

        self.assertEqual("00:00:00:01", tc.end)

        self.assertEqual("00:00:00:02", tc.dur)

    # ==========================================================================

    def test30Fps(self):
        """Tests timecode with 30 fps"""
        tc = TimeCodeSegment(12, 0, 0, 15, 10, fps=30)

        self.assertEqual("12:00:00:15", tc.start)

        self.assertEqual("12:00:00:25", tc.end)

        self.assertEqual("00:00:00:10", tc.dur)

    # ==========================================================================

    def test60Fps(self):
        """Tests timecode with 60 fps"""
        tc = TimeCodeSegment(12, 0, 0, 15, 40, fps=60)

        self.assertEqual("12:00:00:15", tc.start)

        self.assertEqual("12:00:00:55", tc.end)

        self.assertEqual("00:00:00:40", tc.dur)

    # ==========================================================================

    def testAllRandomSetDuration(self):
        """Tests random timecode with set long duration"""
        tc = TimeCodeSegment(fps=60, duration=5183999)

        self.assertEqual("23:59:59:59", tc.dur)

        self.assertEqual(5183999, tc.durFrames)

    # ==========================================================================

    def testDurationUnderFiveMinutes(self):
        """Tests that duration when not provided is kept under 5 minutes"""
        tc = TimeCodeSegment(fps=24)

        self.assertTrue(tc.durFrames <= 7200)


class TestToDecimal(unittest.TestCase):
    """Some quick tests for ToDecimal"""

    def testString(self):
        """Tests string conversions"""
        value = "1.0"

        result = utils.to_decimal(value)
        self.assertEqual(Decimal(str(value)), result)

    def testStringInt(self):
        """Tests string conversions"""
        value = "1"

        result = utils.to_decimal(value)
        self.assertEqual(Decimal("1.0"), result)

    def testStringIntWithSpaces(self):
        """Tests string conversions"""
        value = " 1 "

        result = utils.to_decimal(value)
        self.assertEqual(Decimal("1.0"), result)

    def testStringAdvanced(self):
        """Tests string conversions"""
        value = "1237891273.23162178368123787214849017132897"

        result = utils.to_decimal(value)
        self.assertEqual(Decimal(str(value)), result)

    def testStringBad(self):
        """Tests not a number string conversions"""
        value = "banana"

        self.assertRaises(TypeError, utils.to_decimal, value)

    def testIntConversion(self):
        """Tests int conversions"""
        value = 323628378921398

        result = utils.to_decimal(value)
        self.assertEqual(Decimal(str(value) + ".0"), result)

    def testFloatConversion(self):
        """Tests basic float conversions"""
        value = 12739821.3262871

        result = utils.to_decimal(value)
        self.assertEqual(Decimal(str(value)), result)

    def testFloatConversiontruncated(self):
        """Tests a truncated float conversions"""
        value = 28902319032.3267826378126494173828937289739813902179398073

        result = utils.to_decimal(value)
        self.assertEqual(Decimal(str(value)), result)

    def testUnsupportedType(self):
        """Tests passing an unsupported type conversions"""
        value = ("1.0", "2.0")

        self.assertRaises(ValueError, utils.to_decimal, value)


# ==============================================================================
# FUNCTIONS
# ==============================================================================


def decimalize(*args):
    """Converts a list of floats/ints to Decimal list"""
    return [Decimal(str(i)) for i in args]


# ==============================================================================
# RUNNER
# ==============================================================================
if __name__ == "__main__":
    unittest.main()
