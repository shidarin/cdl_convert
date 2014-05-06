#!/usr/bin/env python
"""
Tests the cdl related functions of cdl_convert

REQUIREMENTS:

mock
"""

#==============================================================================
# IMPORTS
#==============================================================================

# Standard Imports
try:
    from unittest import mock
except ImportError:
    import mock
import os
import sys
import tempfile
import unittest

# Grab our test's path and append the cdL_convert root directory

# There has to be a better method than:
# 1) Getting our current directory
# 2) Splitting into list
# 3) Splicing out the last 3 entries (filepath, test dir, tools dir)
# 4) Joining
# 5) Appending to our Python path.

sys.path.append('/'.join(os.path.realpath(__file__).split('/')[:-2]))

import cdl_convert.cdl_convert as cdl_convert

#==============================================================================
# GLOBALS
#==============================================================================

# We'll build what we know if a valid XML tree by hand, so we can test that our
# fancy etree code is working correctly

CC_OPEN = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection{idAttrib}>
"""
CC_SOP_OPEN = "    <SOPNode>\n"
CC_DESC = "        <Description>{desc}</Description>\n"
CC_SLOPE = "        <Slope>{slopeR} {slopeG} {slopeB}</Slope>\n"
CC_OFFSET = "        <Offset>{offsetR} {offsetG} {offsetB}</Offset>\n"
CC_POWER = "        <Power>{powerR} {powerG} {powerB}</Power>\n"
CC_SOP_CLOSE = "    </SOPNode>\n"
CC_SAT_OPEN = "    <SatNode>\n"
CC_SAT = "        <Saturation>{sat}</Saturation>\n"
CC_SAT_CLOSE = "    </SatNode>\n"
CC_CLOSE = "</ColorCorrection>\n"

# misc ========================================================================

UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWER = 'abcdefghijklmnopqrstuvwxyz'

if sys.version_info[0] >= 3:
    enc = lambda x: bytes(x, 'UTF-8')
else:
    enc = lambda x: x

if sys.version_info[0] >= 3:
    builtins = 'builtins'
else:
    builtins = '__builtin__'

#==============================================================================
# TEST CLASSES
#==============================================================================


class TestParseCDLBasic(unittest.TestCase):
    """Tests parsing a space separated cdl, a Rhythm & Hues format"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope = (1.329, 0.9833, 1.003)
        self.offset = (0.011, 0.013, 0.11)
        self.power = (.993, .998, 1.0113)
        self.sat = 1.01

        self.file = buildCDL(self.slope, self.offset, self.power, self.sat)

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cdl(self.filename)

    #==========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.ColorCorrection.members = {}

    #==========================================================================
    # TESTS
    #==========================================================================

    def testId(self):
        """Tests that id was set to the filename without extension"""
        id = os.path.basename(self.filename).split('.')[0]
        self.assertEqual(
            id,
            self.cdl.id
        )

    #==========================================================================

    def testSlope(self):
        """Tests that slope was set correctly"""
        self.assertEqual(
            self.slope,
            self.cdl.slope
        )

    #==========================================================================

    def testOffset(self):
        """Tests that offset was set correctly"""
        self.assertEqual(
            self.offset,
            self.cdl.offset
        )

    #==========================================================================

    def testPower(self):
        """Tests that power was set correctly"""
        self.assertEqual(
            self.power,
            self.cdl.power
        )

    #==========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        self.assertEqual(
            self.sat,
            self.cdl.sat
        )


class TestParseCDLOdd(TestParseCDLBasic):
    """Tests parsing a space separated cdl with odd but valid numbers"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope = (137829.329, 4327890.9833, 3489031.003)
        self.offset = (-3424.011, -342789423.013, -4238923.11)
        self.power = (3271893.993, .0000998, 0.0000000000000000113)
        self.sat = 1798787.01

        self.file = buildCDL(self.slope, self.offset, self.power, self.sat)

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cdl(self.filename)


class TestWriteCDLBasic(unittest.TestCase):
    """Tests writing a space separated cdl with basic values"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope = [1.329, 0.9833, 1.003]
        self.offset = [0.011, 0.013, 0.11]
        self.power = [.993, .998, 1.0113]
        self.sat = 1.01

        self.cdl = cdl_convert.ColorCorrection(
            'uniqueId',
            '../theVeryBestFile.ale'
        )

        self.cdl.determine_dest('cdl')
        self.cdl.slope = self.slope
        self.cdl.offset = self.offset
        self.cdl.power = self.power
        self.cdl.sat = self.sat

        self.file = buildCDL(self.slope, self.offset, self.power, self.sat)

        self.mockOpen = mock.mock_open()

        with mock.patch(builtins + '.open', self.mockOpen, create=True):
            cdl_convert.write_cdl(self.cdl)

    def tearDown(self):
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.ColorCorrection.members = {}

    #==========================================================================
    # TESTS
    #==========================================================================

    def testOpen(self):
        """Tests that open was called correctly"""
        self.mockOpen.assert_called_once_with(self.cdl.file_out, 'wb')

    #==========================================================================

    def testContent(self):
        """Tests that write_cdl wrote the correct CDL"""
        handle = self.mockOpen()
        handle.write.assert_called_once_with(enc(self.file))


class TestWriteCDLOdd(TestWriteCDLBasic):
    """Tests writing a space separated cdl with basic values"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope = [137829.329, 4327890.9833, 3489031.003]
        self.offset = [-3424.011, -342789423.013, -4238923.11]
        self.power = [3271893.993, .0000998, 0.0000000000000000113]
        self.sat = 1798787.01

        self.cdl = cdl_convert.ColorCorrection(
            'uniqueId', '../theVeryBestFile.ale'
        )

        self.cdl.determine_dest('cdl')
        self.cdl.slope = self.slope
        self.cdl.offset = self.offset
        self.cdl.power = self.power
        self.cdl.sat = self.sat

        self.file = buildCDL(self.slope, self.offset, self.power, self.sat)

        self.mockOpen = mock.mock_open()

        with mock.patch(builtins + '.open', self.mockOpen, create=True):
            cdl_convert.write_cdl(self.cdl)

#==============================================================================
# FUNCTIONS
#==============================================================================


def buildCDL(slope, offset, power, sat):
    """Populates a CDL string and returns it"""

    values = list(slope)
    values.extend(offset)
    values.extend(power)
    values.append(sat)
    values = [str(i) for i in values]

    ss_cdl = ' '.join(values)

    return ss_cdl

#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
