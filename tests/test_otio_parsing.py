#!/usr/bin/env python
"""
Tests the OTIO parsing functionality in cdl_convert

This file contains unit tests for the parse_otio function that parses
OpenTimelineIO (.otio) timeline files for CDL metadata extraction.

"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Imports
import os
import sys
import unittest
from unittest import mock

# Grab our test's path and append the cdl_convert root directory
sys.path.append("/".join(os.path.realpath(__file__).split("/")[:-2]))

import cdl_convert
from cdl_convert.collection import ColorCollection
from cdl_convert.exceptions import OTIOAdapterError, ParseError
from cdl_convert.parse import parse_otio

# ==============================================================================
# TEST CLASSES
# ==============================================================================


class TestParseOTIO(unittest.TestCase):
    """Tests the parse_otio function for OTIO timeline parsing"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear ColorCorrection members to avoid ID conflicts between tests
        cdl_convert.reset_all()

    def test_parse_otio_function_exists(self):
        """Tests that parse_otio function exists and is callable"""
        self.assertTrue(hasattr(cdl_convert, "parse_otio"))
        self.assertTrue(callable(cdl_convert.parse_otio))

    def test_parse_otio_with_nonexistent_file(self):
        """Tests that parse_otio raises appropriate error for missing file"""
        with self.assertRaises((FileNotFoundError, ParseError)):
            parse_otio("nonexistent_file.otio")

    def test_parse_otio_requires_otio_adapter(self):
        """Tests that parse_otio validates OTIO adapter availability"""
        # Mock OTIO not being available
        with mock.patch.dict("sys.modules", {"opentimelineio": None}):
            with mock.patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'opentimelineio'"),
            ):
                with self.assertRaises(OTIOAdapterError) as cm:
                    parse_otio("test.otio")

                error_msg = str(cm.exception)
                self.assertIn("OpenTimelineIO not installed", error_msg)

    def test_parse_otio_successful_single_clip(self):
        """Tests successful OTIO parsing with single clip containing CDL data"""
        # Create mock clip with complete CDL data
        mock_clip = mock.MagicMock()
        mock_clip.name = "shot_001"
        mock_clip.metadata = {
            "cdl": {
                "asc_sop": {
                    "slope": [1.2, 1.1, 1.0],
                    "offset": [-0.1, 0.0, 0.1],
                    "power": [0.9, 1.0, 1.1],
                },
                "asc_sat": 0.85,
            }
        }

        # Create mock track and timeline
        mock_track = [mock_clip]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio("test.otio")

        # Verify result structure
        self.assertIsInstance(result, ColorCollection)
        self.assertEqual(len(result.color_corrections), 1)
        self.assertEqual(result.color_corrections[0].id, "shot_001")
        self.assertTrue(str(result.file_in).endswith("test.otio"))

        # Verify CDL values
        cc = result.color_corrections[0]
        from decimal import Decimal

        self.assertEqual(
            cc.slope, (Decimal("1.2"), Decimal("1.1"), Decimal("1.0"))
        )
        self.assertEqual(
            cc.offset, (Decimal("-0.1"), Decimal("0.0"), Decimal("0.1"))
        )
        self.assertEqual(
            cc.power, (Decimal("0.9"), Decimal("1.0"), Decimal("1.1"))
        )
        self.assertEqual(cc.sat, Decimal("0.85"))

    def test_parse_otio_successful_multiple_clips(self):
        """Tests successful OTIO parsing with multiple clips containing CDL data"""
        # Create multiple mock clips with CDL data
        mock_clip1 = mock.MagicMock()
        mock_clip1.name = "shot_001"
        mock_clip1.metadata = {
            "cdl": {
                "asc_sop": {
                    "slope": [1.2, 1.1, 1.0],
                    "offset": [0.0, 0.0, 0.0],
                    "power": [1.0, 1.0, 1.0],
                },
                "asc_sat": 0.9,
            }
        }

        mock_clip2 = mock.MagicMock()
        mock_clip2.name = "shot_002"
        mock_clip2.metadata = {"cdl": {"asc_sat": 1.1}}

        mock_clip3 = mock.MagicMock()
        mock_clip3.name = "shot_003"
        mock_clip3.metadata = {
            "cdl": {
                "asc_sop": {
                    "slope": [0.8, 0.9, 1.0],
                    "offset": [0.1, 0.0, -0.1],
                    "power": [1.1, 1.0, 0.9],
                }
            }
        }

        # Create mock track and timeline
        mock_track = [mock_clip1, mock_clip2, mock_clip3]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio("multi_clip.otio")

        # Verify result structure
        self.assertIsInstance(result, ColorCollection)
        self.assertEqual(len(result.color_corrections), 3)

        # Verify clip names
        clip_names = [cc.id for cc in result.color_corrections]
        self.assertIn("shot_001", clip_names)
        self.assertIn("shot_002", clip_names)
        self.assertIn("shot_003", clip_names)

    def test_parse_otio_multiple_tracks(self):
        """Tests OTIO parsing with multiple tracks containing CDL clips"""
        # Create clips for different tracks
        mock_clip1 = mock.MagicMock()
        mock_clip1.name = "v1_shot_001"
        mock_clip1.metadata = {"cdl": {"asc_sat": 0.9}}

        mock_clip2 = mock.MagicMock()
        mock_clip2.name = "v1_shot_002"
        mock_clip2.metadata = {"cdl": {"asc_sat": 1.1}}

        mock_clip3 = mock.MagicMock()
        mock_clip3.name = "v2_shot_001"
        mock_clip3.metadata = {"cdl": {"asc_sat": 0.8}}

        # Create mock tracks
        mock_track1 = [mock_clip1, mock_clip2]
        mock_track2 = [mock_clip3]

        # Create mock timeline
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track1, mock_track2]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio("multi_track.otio")

        # Verify result structure
        self.assertIsInstance(result, ColorCollection)
        self.assertEqual(len(result.color_corrections), 3)

        # Verify all clips were found
        clip_names = [cc.id for cc in result.color_corrections]
        self.assertIn("v1_shot_001", clip_names)
        self.assertIn("v1_shot_002", clip_names)
        self.assertIn("v2_shot_001", clip_names)

    def test_parse_otio_mixed_clips_with_and_without_cdl(self):
        """Tests OTIO parsing with mix of clips with and without CDL data"""
        # Create clips - some with CDL, some without
        mock_clip_with_cdl = mock.MagicMock()
        mock_clip_with_cdl.name = "shot_with_cdl"
        mock_clip_with_cdl.metadata = {"cdl": {"asc_sat": 1.0}}

        mock_clip_without_cdl = mock.MagicMock()
        mock_clip_without_cdl.name = "shot_without_cdl"
        mock_clip_without_cdl.metadata = {"other_data": "value"}

        mock_clip_no_metadata = mock.MagicMock()
        del mock_clip_no_metadata.metadata

        # Create mock track and timeline
        mock_track = [
            mock_clip_with_cdl,
            mock_clip_without_cdl,
            mock_clip_no_metadata,
        ]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio("mixed_clips.otio")

        # Should only return the one clip with CDL data
        self.assertIsInstance(result, ColorCollection)
        self.assertEqual(len(result.color_corrections), 1)
        self.assertEqual(result.color_corrections[0].id, "shot_with_cdl")

    def test_parse_otio_empty_timeline(self):
        """Tests OTIO parsing with timeline containing no CDL data"""
        # Create mock timeline with no CDL clips
        mock_clip = mock.MagicMock()
        mock_clip.name = "no_cdl_shot"
        mock_clip.metadata = {"other_data": "value"}

        mock_track = [mock_clip]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio("empty_cdl.otio")

        # Should return empty collection
        self.assertIsInstance(result, ColorCollection)
        self.assertEqual(len(result.color_corrections), 0)

    def test_parse_otio_completely_empty_timeline(self):
        """Tests OTIO parsing with completely empty timeline"""
        # Create mock timeline with no tracks
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = []

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio("empty_timeline.otio")

        # Should return empty collection
        self.assertIsInstance(result, ColorCollection)
        self.assertEqual(len(result.color_corrections), 0)

    def test_parse_otio_malformed_file_error(self):
        """Tests that ParseError is raised for malformed OTIO files"""
        # Mock OTIO with parsing failure
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.side_effect = Exception(
            "Invalid JSON format"
        )

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            with self.assertRaises(ParseError) as cm:
                parse_otio("malformed.otio")

            error_msg = str(cm.exception)
            self.assertIn("Failed to parse OTIO file", error_msg)
            self.assertIn("malformed.otio", error_msg)
            self.assertIn("Invalid JSON format", error_msg)

    def test_parse_otio_otio_json_adapter_missing(self):
        """Tests that OTIOAdapterError is raised when otio_json adapter is missing"""
        # Mock OTIO with missing built-in adapter (should not happen in practice)
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = [
            "other_adapter"
        ]

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            with self.assertRaises(OTIOAdapterError) as cm:
                parse_otio("test.otio")

            error_msg = str(cm.exception)
            self.assertIn(
                "Built-in OTIO adapter 'otio_json' not available", error_msg
            )

    def test_parse_otio_timeline_processing_error(self):
        """Tests that ParseError is raised when timeline processing fails"""
        # Create mock timeline that will cause processing error
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = (
            None  # This should cause an exception when iterating
        )

        # Mock OTIO with successful file reading but bad timeline
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            with self.assertRaises(ParseError) as cm:
                parse_otio("bad_timeline.otio")

            error_msg = str(cm.exception)
            self.assertIn("Failed to parse OTIO file", error_msg)

    def test_parse_otio_with_pathlib_path(self):
        """Tests OTIO parsing with pathlib.Path input"""
        from pathlib import Path

        # Create mock clip with CDL data
        mock_clip = mock.MagicMock()
        mock_clip.name = "pathlib_shot"
        mock_clip.metadata = {"cdl": {"asc_sat": 0.95}}

        # Create mock track and timeline
        mock_track = [mock_clip]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio(Path("pathlib_test.otio"))

        # Verify result structure
        self.assertIsInstance(result, ColorCollection)
        self.assertEqual(len(result.color_corrections), 1)
        self.assertEqual(result.color_corrections[0].id, "pathlib_shot")

    def test_parse_otio_collection_type_set_correctly(self):
        """Tests that the returned ColorCollection has correct type and metadata"""
        # Create mock clip with CDL data
        mock_clip = mock.MagicMock()
        mock_clip.name = "collection_test_shot"
        mock_clip.metadata = {"cdl": {"asc_sat": 1.0}}

        # Create mock track and timeline
        mock_track = [mock_clip]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio("collection_test.otio")

        # Verify collection properties
        self.assertIsInstance(result, ColorCollection)
        self.assertTrue(str(result.file_in).endswith("collection_test.otio"))
        # ColorCollection should have default type (not explicitly set to 'ccc' in parse_otio)
        # The collection type is set by the specific set_to_* methods, not in parse_otio

    def test_parse_otio_clips_with_partial_cdl_data(self):
        """Tests OTIO parsing with clips containing partial CDL data"""
        # Create clips with different partial CDL data
        mock_clip_sop_only = mock.MagicMock()
        mock_clip_sop_only.name = "sop_only_shot"
        mock_clip_sop_only.metadata = {
            "cdl": {
                "asc_sop": {
                    "slope": [1.1, 1.0, 0.9],
                    "offset": [0.0, 0.0, 0.0],
                    "power": [1.0, 1.0, 1.0],
                }
            }
        }

        mock_clip_sat_only = mock.MagicMock()
        mock_clip_sat_only.name = "sat_only_shot"
        mock_clip_sat_only.metadata = {"cdl": {"asc_sat": 0.8}}

        mock_clip_incomplete_sop = mock.MagicMock()
        mock_clip_incomplete_sop.name = "incomplete_sop_shot"
        mock_clip_incomplete_sop.metadata = {
            "cdl": {
                "asc_sop": {
                    "slope": [1.2, 1.1, 1.0]
                    # Missing offset and power
                }
            }
        }

        # Create mock track and timeline
        mock_track = [
            mock_clip_sop_only,
            mock_clip_sat_only,
            mock_clip_incomplete_sop,
        ]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
            result = parse_otio("partial_cdl.otio")

        # All clips should be parsed successfully
        self.assertIsInstance(result, ColorCollection)
        self.assertEqual(len(result.color_corrections), 3)

        # Verify clip names
        clip_names = [cc.id for cc in result.color_corrections]
        self.assertIn("sop_only_shot", clip_names)
        self.assertIn("sat_only_shot", clip_names)
        self.assertIn("incomplete_sop_shot", clip_names)


class TestParseOTIOErrorHandling(unittest.TestCase):
    """Tests error handling scenarios for parse_otio function"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear ColorCorrection members to avoid ID conflicts between tests
        cdl_convert.reset_all()

    def test_parse_otio_with_malformed_cdl_halt_on_error_true(self):
        """Tests that ParseError is raised for malformed CDL with halt_on_error=True"""
        # Create mock clip with malformed CDL data
        mock_clip = mock.MagicMock()
        mock_clip.name = "malformed_cdl_shot"
        mock_clip.metadata = {
            "cdl": {
                "asc_sop": "invalid_data"  # Should be dict, not string
            }
        }

        # Create mock track and timeline
        mock_track = [mock_clip]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        # Set halt_on_error to True
        original_halt = cdl_convert.config.config.halt_on_error
        cdl_convert.config.config.halt_on_error = True

        try:
            with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
                with self.assertRaises(ParseError) as cm:
                    parse_otio("malformed_cdl.otio")

                error_msg = str(cm.exception)
                self.assertIn("Failed to parse OTIO file", error_msg)
        finally:
            # Restore original setting
            cdl_convert.config.config.halt_on_error = original_halt

    def test_parse_otio_with_malformed_cdl_halt_on_error_false(self):
        """Tests that malformed CDL clips are skipped with halt_on_error=False"""
        # Create clips - one valid, one malformed
        mock_clip_valid = mock.MagicMock()
        mock_clip_valid.name = "valid_shot"
        mock_clip_valid.metadata = {"cdl": {"asc_sat": 1.0}}

        mock_clip_malformed = mock.MagicMock()
        mock_clip_malformed.name = "malformed_shot"
        mock_clip_malformed.metadata = {
            "cdl": {
                "asc_sop": "invalid_data"  # Should be dict, not string
            }
        }

        # Create mock track and timeline
        mock_track = [mock_clip_valid, mock_clip_malformed]
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]

        # Mock OTIO with successful parsing
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = ["otio_json"]
        mock_otio.adapters.read_from_file.return_value = mock_timeline

        # Set halt_on_error to False
        original_halt = cdl_convert.config.config.halt_on_error
        cdl_convert.config.config.halt_on_error = False

        try:
            with mock.patch.dict("sys.modules", {"opentimelineio": mock_otio}):
                result = parse_otio("mixed_validity.otio")

            # Should only return the valid clip
            self.assertIsInstance(result, ColorCollection)
            self.assertEqual(len(result.color_corrections), 1)
            self.assertEqual(result.color_corrections[0].id, "valid_shot")
        finally:
            # Restore original setting
            cdl_convert.config.config.halt_on_error = original_halt


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    unittest.main()
