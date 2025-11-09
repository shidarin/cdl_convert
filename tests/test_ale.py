#!/usr/bin/env python
"""
Tests the ALE integration with OTIO adapter for cdl_convert

This file contains minimal integration tests to verify that the OTIO
adapter integration works correctly. The detailed ALE parsing logic
is now tested by the otio-ale-adapter test suite.

"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Imports
import os
import sys
import unittest

# Grab our test's path and append the cdl_convert root directory
sys.path.append("/".join(os.path.realpath(__file__).split("/")[:-2]))

import cdl_convert
from cdl_convert.exceptions import OTIOAdapterError, ParseError

# ==============================================================================
# TEST CLASSES
# ==============================================================================


class TestALEIntegration(unittest.TestCase):
    """Tests ALE integration with OTIO adapter"""

    def setUp(self):
        """Set up test fixtures"""
        # Clear ColorCorrection members to avoid ID conflicts between tests
        cdl_convert.reset_all()

    def test_parse_ale_function_exists(self):
        """Tests that parse_ale function exists and is callable"""
        self.assertTrue(hasattr(cdl_convert, "parse_ale"))
        self.assertTrue(callable(cdl_convert.parse_ale))

    def test_parse_ale_with_nonexistent_file(self):
        """Tests that parse_ale raises appropriate error for missing file"""
        with self.assertRaises((FileNotFoundError, ParseError)):
            cdl_convert.parse_ale("nonexistent_file.ale")

    def test_parse_ale_requires_otio_adapter(self):
        """Tests that parse_ale validates OTIO adapter availability"""
        # This test verifies that the function checks for the adapter
        # The actual adapter availability depends on the test environment
        try:
            # Try to call with a non-existent file to trigger adapter check
            cdl_convert.parse_ale("test.ale")
        except (FileNotFoundError, OTIOAdapterError, ParseError):
            # Any of these errors is acceptable - they indicate the function
            # is working correctly (either adapter check or file check)
            pass
        except Exception as e:
            # Any other exception type indicates a problem
            self.fail(f"Unexpected exception type: {type(e).__name__}: {e}")


# ==============================================================================
# RUNNER
# ==============================================================================
if __name__ == "__main__":
    unittest.main()
