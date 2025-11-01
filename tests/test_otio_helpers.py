#!/usr/bin/env python
"""
Tests the OTIO helper functions in the parse module of cdl_convert

REQUIREMENTS:

mock
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
sys.path.append('/'.join(os.path.realpath(__file__).split('/')[:-2]))

import cdl_convert
from cdl_convert.parse import (
    _check_otio_adapter,
    _extract_cdl_from_otio_clip,
    _extract_cdl_metadata
)
from cdl_convert.exceptions import OTIOAdapterError, ParseError
from cdl_convert.correction import ColorCorrection

# ==============================================================================
# TEST CLASSES
# ==============================================================================


class TestOTIOAdapterError(unittest.TestCase):
    """Tests the OTIOAdapterError exception class"""

    def test_inheritance(self):
        """Tests that OTIOAdapterError inherits from CDLConvertError"""
        from cdl_convert.exceptions import CDLConvertError
        self.assertTrue(issubclass(OTIOAdapterError, CDLConvertError))

    def test_instantiation(self):
        """Tests that OTIOAdapterError can be instantiated"""
        error = OTIOAdapterError("OTIO adapter not found")
        self.assertIsInstance(error, OTIOAdapterError)
        self.assertEqual(str(error), "OTIO adapter not found")

    def test_raise_and_catch(self):
        """Tests that OTIOAdapterError can be raised and caught"""
        with self.assertRaises(OTIOAdapterError):
            raise OTIOAdapterError("OTIO error")


class TestCheckOTIOAdapter(unittest.TestCase):
    """Tests the _check_otio_adapter helper function"""

    def test_otio_not_installed(self):
        """Tests that OTIOAdapterError is raised when otio is not installed"""
        with mock.patch.dict('sys.modules', {'opentimelineio': None}):
            with mock.patch(
                'builtins.__import__',
                side_effect=ImportError("No module named 'opentimelineio'")
                ):
                with self.assertRaises(OTIOAdapterError) as cm:
                    _check_otio_adapter('cmx_3600')
                
                error_msg = str(cm.exception)
                self.assertIn("OpenTimelineIO not installed", error_msg)

    def test_adapter_not_available_cmx(self):
        """Tests that OTIOAdapterError is raised when CMX adapter is missing"""
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = [
            'ale', 'other_adapter'
            ]
        
        with mock.patch.dict('sys.modules', {'opentimelineio': mock_otio}):
            with self.assertRaises(OTIOAdapterError) as cm:
                _check_otio_adapter('cmx_3600')
            
            error_msg = str(cm.exception)
            self.assertIn("Missing required OTIO adapter: 'cmx_3600'", error_msg)

    def test_adapter_not_available_ale(self):
        """Tests that OTIOAdapterError is raised when ALE adapter is missing"""
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = [
            'cmx_3600', 'other_adapter'
            ]
        
        with mock.patch.dict('sys.modules', {'opentimelineio': mock_otio}):
            with self.assertRaises(OTIOAdapterError) as cm:
                _check_otio_adapter('ale')
            
            error_msg = str(cm.exception)
            self.assertIn("Missing required OTIO adapter: 'ale'", error_msg)

    def test_adapter_not_available_generic(self):
        """Tests that OTIOAdapterError is raised when generic is missing"""
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = [
            'cmx_3600', 'ale'
            ]
        
        with mock.patch.dict('sys.modules', {'opentimelineio': mock_otio}):
            with self.assertRaises(OTIOAdapterError) as cm:
                _check_otio_adapter('unknown_adapter')
            
            error_msg = str(cm.exception)
            self.assertIn(
                "Missing required OTIO adapter: 'unknown_adapter'", error_msg
                )

    def test_adapter_available_success(self):
        """Tests that no exception is raised when adapter is available"""
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.return_value = [
            'cmx_3600', 'ale', 'other_adapter'
            ]
        
        with mock.patch.dict('sys.modules', {'opentimelineio': mock_otio}):
            # Should not raise any exception
            _check_otio_adapter('cmx_3600')
            _check_otio_adapter('ale')

    def test_otio_exception_during_check(self):
        """Tests that OTIOAdapterError is raised when OTIO throws exception"""
        mock_otio = mock.MagicMock()
        mock_otio.adapters.available_adapter_names.side_effect = RuntimeError(
            "OTIO internal error"
        )
        
        with mock.patch.dict('sys.modules', {'opentimelineio': mock_otio}):
            with self.assertRaises(OTIOAdapterError) as cm:
                _check_otio_adapter('cmx_3600')
            
            error_msg = str(cm.exception)
            self.assertIn("OTIO internal error", error_msg)


class TestExtractCDLFromOTIOClip(unittest.TestCase):
    """Tests the _extract_cdl_from_otio_clip helper function"""

    def setUp(self):
        """Set up test fixtures"""
        self.source_file = "test.edl"
        # Clear ColorCorrection members to avoid ID conflicts between tests
        cdl_convert.reset_all()

    def test_clip_without_metadata(self):
        """Tests that None is returned when clip has no metadata attribute"""
        mock_clip = mock.MagicMock()
        del mock_clip.metadata  # Remove metadata attribute
        
        result = _extract_cdl_from_otio_clip(mock_clip, self.source_file)
        self.assertIsNone(result)

    def test_clip_without_cdl_metadata(self):
        """Tests that None is returned when clip metadata has no CDL data"""
        mock_clip = mock.MagicMock()
        mock_clip.metadata = {'other_data': 'value'}
        
        result = _extract_cdl_from_otio_clip(mock_clip, self.source_file)
        self.assertIsNone(result)

    def test_clip_with_complete_cdl_metadata(self):
        """Tests successful CDL extraction from clip with complete metadata"""
        mock_clip = mock.MagicMock()
        mock_clip.name = "shot_001_complete"
        mock_clip.metadata = {
            'cdl': {
                'asc_sop': {
                    'slope': [1.2, 1.1, 1.0],
                    'offset': [-0.1, 0.0, 0.1],
                    'power': [0.9, 1.0, 1.1]
                },
                'asc_sat': 0.85
            }
        }
        
        result = _extract_cdl_from_otio_clip(mock_clip, self.source_file)
        
        self.assertIsInstance(result, ColorCorrection)
        self.assertEqual(result.id, "shot_001_complete")
        # ColorCorrection returns Decimal tuples, so we need to compare accordingly
        from decimal import Decimal
        self.assertEqual(result.slope, (Decimal('1.2'), Decimal('1.1'), Decimal('1.0')))
        self.assertEqual(result.offset, (Decimal('-0.1'), Decimal('0.0'), Decimal('0.1')))
        self.assertEqual(result.power, (Decimal('0.9'), Decimal('1.0'), Decimal('1.1')))
        self.assertEqual(result.sat, Decimal('0.85'))

    def test_clip_with_partial_cdl_metadata_sop_only(self):
        """Tests CDL extraction with only SOP data"""
        mock_clip = mock.MagicMock()
        mock_clip.name = "shot_002_sop"
        mock_clip.metadata = {
            'cdl': {
                'asc_sop': {
                    'slope': [1.5, 1.3, 1.1],
                    'offset': [0.0, 0.0, 0.0],
                    'power': [1.0, 1.0, 1.0]
                }
            }
        }
        
        result = _extract_cdl_from_otio_clip(mock_clip, self.source_file)
        
        self.assertIsInstance(result, ColorCorrection)
        self.assertEqual(result.id, "shot_002_sop")
        from decimal import Decimal
        self.assertEqual(result.slope, (Decimal('1.5'), Decimal('1.3'), Decimal('1.1')))
        self.assertEqual(result.offset, (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')))
        self.assertEqual(result.power, (Decimal('1.0'), Decimal('1.0'), Decimal('1.0')))

    def test_clip_with_partial_cdl_metadata_sat_only(self):
        """Tests CDL extraction with only saturation data"""
        mock_clip = mock.MagicMock()
        mock_clip.name = "shot_003_sat"
        mock_clip.metadata = {
            'cdl': {
                'asc_sat': 1.2
            }
        }
        
        result = _extract_cdl_from_otio_clip(mock_clip, self.source_file)
        
        self.assertIsInstance(result, ColorCorrection)
        self.assertEqual(result.id, "shot_003_sat")
        from decimal import Decimal
        self.assertEqual(result.sat, Decimal('1.2'))

    def test_clip_with_incomplete_sop_data(self):
        """Tests CDL extraction with incomplete SOP data"""
        mock_clip = mock.MagicMock()
        mock_clip.name = "shot_004_incomplete"
        mock_clip.metadata = {
            'cdl': {
                'asc_sop': {
                    'slope': [1.2, 1.1, 1.0],
                    # Missing offset and power
                }
            }
        }
        
        result = _extract_cdl_from_otio_clip(mock_clip, self.source_file)
        
        self.assertIsInstance(result, ColorCorrection)
        self.assertEqual(result.id, "shot_004_incomplete")
        from decimal import Decimal
        self.assertEqual(result.slope, (Decimal('1.2'), Decimal('1.1'), Decimal('1.0')))

    def test_clip_without_name(self):
        """Tests CDL extraction when clip has no name attribute"""
        mock_clip = mock.MagicMock()
        del mock_clip.name  # Remove name attribute
        mock_clip.metadata = {
            'cdl': {
                'asc_sat': 0.9
            }
        }
        
        result = _extract_cdl_from_otio_clip(mock_clip, self.source_file)
        
        self.assertIsInstance(result, ColorCorrection)
        self.assertEqual(result.id, "Unknown")
        from decimal import Decimal
        self.assertEqual(result.sat, Decimal('0.9'))

    def test_malformed_cdl_metadata_halt_on_error_true(self):
        """Tests that ParseError is raised for malformed CDL with halt"""
        mock_clip = mock.MagicMock()
        mock_clip.name = "shot_005_malformed"
        mock_clip.metadata = {
            'cdl': {
                'asc_sop': "invalid_data"  # Should be dict, not string
            }
        }
        
        # Set halt_on_error to True
        original_halt = cdl_convert.config.config.halt_on_error
        cdl_convert.config.config.halt_on_error = True
        
        try:
            with self.assertRaises(ParseError) as cm:
                _extract_cdl_from_otio_clip(mock_clip, self.source_file)
            
            error_msg = str(cm.exception)
            self.assertIn("Malformed CDL metadata", error_msg)
            self.assertIn("shot_005_malformed", error_msg)
        finally:
            # Restore original setting
            cdl_convert.config.config.halt_on_error = original_halt

    def test_malformed_cdl_metadata_halt_on_error_false(self):
        """Tests that None is returned for malformed CDL with halt"""
        mock_clip = mock.MagicMock()
        mock_clip.name = "shot_006_malformed_false"
        mock_clip.metadata = {
            'cdl': {
                'asc_sop': "invalid_data"  # Should be dict, not string
            }
        }
        
        # Set halt_on_error to False
        original_halt = cdl_convert.config.config.halt_on_error
        cdl_convert.config.config.halt_on_error = False
        
        try:
            result = _extract_cdl_from_otio_clip(mock_clip, self.source_file)
            self.assertIsNone(result)
        finally:
            # Restore original setting
            cdl_convert.config.config.halt_on_error = original_halt


class TestExtractCDLMetadata(unittest.TestCase):
    """Tests the _extract_cdl_metadata helper function"""

    def setUp(self):
        """Set up test fixtures"""
        self.source_file = "test.edl"
        # Clear ColorCorrection members to avoid ID conflicts between tests
        cdl_convert.reset_all()

    def test_timeline_with_direct_track_iteration(self):
        """Tests CDL extraction from timeline with direct track iteration (correct OTIO API)"""
        # Create mock clips with CDL data
        mock_clip1 = mock.MagicMock()
        mock_clip1.name = "timeline_shot_001"
        mock_clip1.metadata = {
            'cdl': {
                'asc_sop': {
                    'slope': [1.2, 1.1, 1.0],
                    'offset': [0.0, 0.0, 0.0],
                    'power': [1.0, 1.0, 1.0]
                },
                'asc_sat': 0.9
            }
        }
        
        mock_clip2 = mock.MagicMock()
        mock_clip2.name = "timeline_shot_002"
        mock_clip2.metadata = {
            'cdl': {
                'asc_sat': 1.1
            }
        }
        
        # Create mock track that is iterable (like real OTIO tracks)
        mock_track = [mock_clip1, mock_clip2]
        
        # Create mock timeline
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]
        
        result = _extract_cdl_metadata(mock_timeline, self.source_file)
        
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ColorCorrection)
        self.assertIsInstance(result[1], ColorCorrection)
        self.assertEqual(result[0].id, "timeline_shot_001")
        self.assertEqual(result[1].id, "timeline_shot_002")

    def test_timeline_with_single_clip(self):
        """Tests CDL extraction from timeline with single clip"""
        # Create mock clip with CDL data
        mock_clip = mock.MagicMock()
        mock_clip.name = "single_timeline_shot"
        mock_clip.metadata = {
            'cdl': {
                'asc_sat': 0.8
            }
        }
        
        # Create mock track
        mock_track = [mock_clip]
        
        # Create mock timeline
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]
        
        result = _extract_cdl_metadata(mock_timeline, self.source_file)
        
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ColorCorrection)
        self.assertEqual(result[0].id, "single_timeline_shot")

    def test_timeline_with_mixed_clips(self):
        """Tests CDL extraction with mix of clips with and without CDL data"""
        # Create clips - some with CDL, some without
        mock_clip_with_cdl = mock.MagicMock()
        mock_clip_with_cdl.name = "shot_with_cdl"
        mock_clip_with_cdl.metadata = {
            'cdl': {
                'asc_sat': 1.0
            }
        }
        
        mock_clip_without_cdl = mock.MagicMock()
        mock_clip_without_cdl.name = "shot_without_cdl"
        mock_clip_without_cdl.metadata = {'other_data': 'value'}
        
        mock_clip_no_metadata = mock.MagicMock()
        del mock_clip_no_metadata.metadata
        
        # Create mock track
        mock_track = [
            mock_clip_with_cdl, mock_clip_without_cdl, mock_clip_no_metadata
        ]
        
        # Create mock timeline
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]
        
        result = _extract_cdl_metadata(mock_timeline, self.source_file)
        
        # Should only return the one clip with CDL data
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "shot_with_cdl")

    def test_timeline_with_multiple_tracks(self):
        """Tests CDL extraction from timeline with multiple tracks"""
        # Create clips for different tracks
        mock_clip1 = mock.MagicMock()
        mock_clip1.name = "track1_shot1"
        mock_clip1.metadata = {'cdl': {'asc_sat': 0.9}}
        
        mock_clip2 = mock.MagicMock()
        mock_clip2.name = "track1_shot2"
        mock_clip2.metadata = {'cdl': {'asc_sat': 1.1}}
        
        mock_clip3 = mock.MagicMock()
        mock_clip3.name = "track2_shot1"
        mock_clip3.metadata = {'cdl': {'asc_sat': 0.8}}
        
        # Create mock tracks
        mock_track1 = [mock_clip1, mock_clip2]
        mock_track2 = [mock_clip3]
        
        # Create mock timeline
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track1, mock_track2]
        
        result = _extract_cdl_metadata(mock_timeline, self.source_file)
        
        self.assertEqual(len(result), 3)
        clip_names = [cc.id for cc in result]
        self.assertIn("track1_shot1", clip_names)
        self.assertIn("track1_shot2", clip_names)
        self.assertIn("track2_shot1", clip_names)

    def test_timeline_with_non_iterable_track(self):
        """Tests that ParseError is raised when track is not iterable"""
        # Create mock track that is not iterable (should cause exception)
        mock_track = mock.MagicMock()
        # Make the track non-iterable by making __iter__ raise TypeError
        mock_track.__iter__.side_effect = TypeError(
            "'MockTrack' object is not iterable"
        )
        
        # Create mock timeline
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = [mock_track]
        
        # Should raise ParseError since track is not iterable
        with self.assertRaises(ParseError) as cm:
            _extract_cdl_metadata(mock_timeline, self.source_file)
        
        error_msg = str(cm.exception)
        self.assertIn("Error processing OTIO timeline structure", error_msg)

    def test_timeline_with_empty_tracks(self):
        """Tests CDL extraction from timeline with empty tracks"""
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = []
        
        result = _extract_cdl_metadata(mock_timeline, self.source_file)
        
        self.assertEqual(len(result), 0)

    def test_timeline_processing_exception(self):
        """Tests that ParseError is raised when timeline processing fails"""
        # Create mock timeline that will cause an exception
        mock_timeline = mock.MagicMock()
        mock_timeline.tracks = None  # This should cause an exception when iterating
        
        with self.assertRaises(ParseError) as cm:
            _extract_cdl_metadata(mock_timeline, self.source_file)
        
        error_msg = str(cm.exception)
        self.assertIn("Error processing OTIO timeline structure", error_msg)


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    unittest.main()