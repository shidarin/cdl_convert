#!/usr/bin/env python
"""
Tests for the flex related functions of cdl_convert

REQUIREMENTS:

mock
"""

#===============================================================================
# IMPORTS
#===============================================================================

# Standard Imports
try:
    from unittest import mock
except ImportError:
    import mock
import os
from random import choice

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
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

#===============================================================================
# GLOBALS
#===============================================================================

# A lot of these FLEx strings are ripped straight from the flex document
# http://www.scribd.com/doc/97598863/Flex-file-format-specification-v1005

FLEX_HEADER = """000 Manufacturer Da Vinci   No. 416 Equip TLC        Version 400      FLEx 1004
010 Title {title}
011 Client Black Hole Studios, Inc.      Facility The Best Post Place, Ltd.
012 Shoot Date 06-01-95  Transfer Date 06-02-95  Opr RGB  Asst YCM  Bay TC-1
013 Notes Reels 213A and 213B are KeyKoded; reel 99 is stock shot footage.
"""
FLEX_100 = "100 Edit 102  to V1234       Field A1 NTSC Split 34          Delay 00:01:56:12.0\n"
FLEX_101 = "101 Reel 001B to V12T                     Split V           Delay 00;00;05;15,1 \n"
FLEX_110 = "110 Scene {scene} Take {take} Cam Roll {roll} Sound {sound} 00;00;05;15.0 \n"
FLEX_120 = '120 Scrpt POV launch tower; PA: "T-minus...6...5... Abort, retry, ignore?>"     \n'
FLEX_200 = "200 RNK-A 35 23.98 OCN-12A  000100+00 000001+08 Key EASTM KJ123456 008845+02 p2 \n"
FLEX_300 = "300 VTR-1 Assemble  001      At 01:12:00:04.0 For 00:00:37:15.0 Using VITC      \n"
FLEX_400 = "400 SOUND Insert    025B     At 01:12:00:04.0 For 00:05:37:15.0 Using LTC       \n"
FLEX_500 = "500 RGB   02 Dissolve BLACK    to 026      Fx      Rate 060 Delay 00:00:05:00.0 \n"
FLEX_600 = "600 AMX   01 Register REEL023  to Reel023B Fx 8    Rate 030 Delay               \n"
FLEX_701 = "701 ASC_SOP({slopeR} {slopeG} {slopeB})({offsetR} {offsetG} {offsetB})({powerR} {powerG} {powerB})\n"
FLEX_702 = "702 ASC_SAT {sat}\n"

# misc =========================================================================

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

#===============================================================================
# TEST CLASSES
#===============================================================================


class TestParseFLExBasic(unittest.TestCase):
    """Tests basic parsing of a standard FLEx

    FLEx can't store more than 6 sig digits, so we'll stay within that limit"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = "Bob's Big Apple Break, into the big apple! Part 365   H"

        self.slope1 = (1.329, 0.9833, 1.003)
        self.offset1 = (0.011, 0.013, 0.11)
        self.power1 = (.993, .998, 1.0113)
        self.sat1 = 1.01

        line1 = buildFLExTake(self.slope1, self.offset1, self.power1, self.sat1,
                              'bb94', 'x103', 'line1')

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = (13.329, 4.9334, 348908)
        self.offset2 = (-3424.0, -34.013, -642389)
        self.power2 = (37.993, .00009, 0.0000)
        self.sat2 = 177.01

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2, self.sat2,
                              'bb94', 'x104', 'line2')

        self.slope3 = (1.2, 2.32, 10.82)
        self.offset3 = (-1.3782, 278.32, 0.7383)
        self.power3 = (1.329, 0.9833, 1.003)
        self.sat3 = 0.99

        line3 = buildFLExTake(self.slope3, self.offset3, self.power3, self.sat3,
                              'bb94', 'x105', 'line3')

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdls = cdl_convert.parse_flex(self.filename)
        self.cdl1 = self.cdls[0]
        self.cdl2 = self.cdls[1]
        self.cdl3 = self.cdls[2]

    #===========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.ColorCorrection.members = {}

    #===========================================================================
    # TESTS
    #===========================================================================

    def testId(self):
        """Tests that filenames were parsed correctly"""

        self.assertEqual(
            'bb94_x103_line1',
            self.cdl1.cc_id
        )

        self.assertEqual(
            'bb94_x104_line2',
            self.cdl2.cc_id
        )

        self.assertEqual(
            'bb94_x105_line3',
            self.cdl3.cc_id
        )

    #===========================================================================

    def testSlope(self):
        """Tests that slopes were parsed correctly"""

        self.assertEqual(
            self.slope1,
            self.cdl1.slope
        )

        self.assertEqual(
            self.slope2,
            self.cdl2.slope
        )

        self.assertEqual(
            self.slope3,
            self.cdl3.slope
        )

    #===========================================================================

    def testOffset(self):
        """Tests that offsets were parsed correctly"""

        self.assertEqual(
            self.offset1,
            self.cdl1.offset
        )

        self.assertEqual(
            self.offset2,
            self.cdl2.offset
        )

        self.assertEqual(
            self.offset3,
            self.cdl3.offset
        )

    #===========================================================================

    def testPower(self):
        """Tests that powers were parsed correctly"""

        self.assertEqual(
            self.power1,
            self.cdl1.power
        )

        self.assertEqual(
            self.power2,
            self.cdl2.power
        )

        self.assertEqual(
            self.power3,
            self.cdl3.power
        )

    #===========================================================================

    def testSat(self):
        """Tests that sats were parsed correctly"""

        self.assertEqual(
            self.sat1,
            self.cdl1.sat
        )

        self.assertEqual(
            self.sat2,
            self.cdl2.sat
        )

        self.assertEqual(
            self.sat3,
            self.cdl3.sat
        )

    #===========================================================================

    def testDescription(self):
        """Tests that the descriptions have been parsed correctly"""

        for i in range(3):
            self.assertEqual(
                self.title,
                self.cdls[i].metadata['desc']
            )


class TestParseFLExMissingNames(TestParseFLExBasic):
    """Tests basic parsing of a Flex where some takes are missing name fields"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = "Bob's Big Apple Break, into the big apple! Part 365   H"

        self.slope1 = (1.329, 0.9833, 1.003)
        self.offset1 = (0.011, 0.013, 0.11)
        self.power1 = (.993, .998, 1.0113)
        self.sat1 = 1.01

        line1 = buildFLExTake(self.slope1, self.offset1, self.power1, self.sat1,
                              'bb94', 'x103', 'line1')

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = (13.329, 4.9334, 348908)
        self.offset2 = (-3424.0, -34.013, -642389)
        self.power2 = (37.993, .00009, 0.0000)
        self.sat2 = 177.01

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2, self.sat2,
                              'bb94', 'x104')

        self.slope3 = (1.2, 2.32, 10.82)
        self.offset3 = (-1.3782, 278.32, 0.7383)
        self.power3 = (1.329, 0.9833, 1.003)
        self.sat3 = 0.99

        line3 = buildFLExTake(self.slope3, self.offset3, self.power3, self.sat3,
                              'bb94')

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdls = cdl_convert.parse_flex(self.filename)
        self.cdl1 = self.cdls[0]
        self.cdl2 = self.cdls[1]
        self.cdl3 = self.cdls[2]

    #===========================================================================
    # TESTS
    #===========================================================================

    def testId(self):
        """Tests that filenames were parsed correctly"""

        self.assertEqual(
            'bb94_x103_line1',
            self.cdl1.cc_id
        )

        self.assertEqual(
            'bb94_x104',
            self.cdl2.cc_id
        )

        self.assertEqual(
            'bb94',
            self.cdl3.cc_id
        )


class TestParseFLExTitleOnly(TestParseFLExBasic):
    """Tests basic parsing of a Flex where no takes have scn/roll/take fields"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = "Bob's Big Apple Break, into the big apple! Part.365   H"

        self.slope1 = (1.329, 0.9833, 1.003)
        self.offset1 = (0.011, 0.013, 0.11)
        self.power1 = (.993, .998, 1.0113)
        self.sat1 = 1.01

        line1 = buildFLExTake(self.slope1, self.offset1, self.power1, self.sat1)

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = (13.329, 4.9334, 348908)
        self.offset2 = (-3424.0, -34.013, -642389)
        self.power2 = (37.993, .00009, 0.0000)
        self.sat2 = 177.01

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2, self.sat2)

        self.slope3 = (1.2, 2.32, 10.82)
        self.offset3 = (-1.3782, 278.32, 0.7383)
        self.power3 = (1.329, 0.9833, 1.003)
        self.sat3 = 0.99

        line3 = buildFLExTake(self.slope3, self.offset3, self.power3, self.sat3)

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdls = cdl_convert.parse_flex(self.filename)
        self.cdl1 = self.cdls[0]
        self.cdl2 = self.cdls[1]
        self.cdl3 = self.cdls[2]

    #===========================================================================
    # TESTS
    #===========================================================================

    def testId(self):
        """Tests that filenames were parsed correctly"""

        self.assertEqual(
            "Bobs_Big_Apple_Break_into_the_big_apple_Part.365___H001",
            self.cdl1.cc_id
        )

        self.assertEqual(
            "Bobs_Big_Apple_Break_into_the_big_apple_Part.365___H002",
            self.cdl2.cc_id
        )

        self.assertEqual(
            "Bobs_Big_Apple_Break_into_the_big_apple_Part.365___H003",
            self.cdl3.cc_id
        )


class TestParseFLExNoTitle(TestParseFLExBasic):
    """Tests basic parsing of a Flex where id is based on filename"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = ''

        self.slope1 = (1.329, 0.9833, 1.003)
        self.offset1 = (0.011, 0.013, 0.11)
        self.power1 = (.993, .998, 1.0113)
        self.sat1 = 1.01

        line1 = buildFLExTake(self.slope1, self.offset1, self.power1, self.sat1)

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = (13.329, 4.9334, 348908)
        self.offset2 = (-3424.0, -34.013, -642389)
        self.power2 = (37.993, .00009, 0.0000)
        self.sat2 = 177.01

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2, self.sat2)

        self.slope3 = (1.2, 2.32, 10.82)
        self.offset3 = (-1.3782, 278.32, 0.7383)
        self.power3 = (1.329, 0.9833, 1.003)
        self.sat3 = 0.99

        line3 = buildFLExTake(self.slope3, self.offset3, self.power3, self.sat3)

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdls = cdl_convert.parse_flex(self.filename)
        self.cdl1 = self.cdls[0]
        self.cdl2 = self.cdls[1]
        self.cdl3 = self.cdls[2]

    #===========================================================================
    # TESTS
    #===========================================================================

    def testId(self):
        """Tests that filenames were parsed correctly"""

        filename = os.path.basename(self.filename).split('.')[0]

        self.assertEqual(
            "{0}001".format(filename),
            self.cdl1.cc_id
        )

        self.assertEqual(
            "{0}002".format(filename),
            self.cdl2.cc_id
        )

        self.assertEqual(
            "{0}003".format(filename),
            self.cdl3.cc_id
        )

    #===========================================================================

    def testDescription(self):
        """Tests that the descriptions have been parsed correctly"""

        for i in range(3):
            self.assertEqual(
                [],
                self.cdls[i].metadata['desc']
            )


class TestParseFLExMissingSopSat(TestParseFLExBasic):
    """Tests basic parsing of a Flex where sop/sat are missing"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = "Hanky Panky Bromance"

        self.slope1 = (1.0, 1.0, 1.0)
        self.offset1 = (0.0, 0.0, 0.0)
        self.power1 = (1.0, 1.0, 1.0)
        self.sat1 = 1.01

        line1 = buildFLExTake(sat=self.sat1, scene='bb94', take='x103',
                              roll='line1')

        self.slope2 = (1.2, 2.32, 10.82)
        self.offset2 = (-1.32, 2.32, 0.73)
        self.power2 = (1.329, 0.9833, 1.003)
        self.sat2 = 1.0

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2,
                              scene='bb94', take='x104', roll='line2')

        self.slope3 = (1.0, 1.0, 1.0)
        self.offset3 = (0.0, 0.0, 0.0)
        self.power3 = (1.0, 1.0, 1.0)
        self.sat3 = 1.0

        line3 = buildFLExTake()

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.raw_cdls = cdl_convert.parse_flex(self.filename)
        self.cdls = self.raw_cdls[:]
        self.cdl1 = self.cdls[0]
        self.cdl2 = self.cdls[1]
        self.cdl3 = cdl_convert.ColorCorrection(
            'bb94_x105_line3', self.filename
        )
        self.cdl3.metadata['desc'] = self.title
        self.cdls.append(self.cdl3)

    #===========================================================================
    # TESTS
    #===========================================================================

    def testOnlyTwoCDLsReturned(self):
        """Tests that with no SOP or SAT value, only 2 lines will become cdls"""

        self.assertEqual(
            2,
            len(self.raw_cdls)
        )

#===============================================================================
# FUNCTIONS
#===============================================================================


def buildFLExTake(slope=None, offset=None, power=None, sat=None, scene=None,
                  take=None, roll=None):
    """Builds a multiline take for a FLEx edl

    This gets a little complicated because the FLEx uses strict character
    delineation, so that's why we have all the ljust's spacing out characters.
    """

    tf = (True, False)

    flex = FLEX_100
    if choice(tf):
        flex += FLEX_101

    if not scene:
        scene = ''
    if not take:
        take = ''
    if not roll:
        roll = ''

    flex += FLEX_110.format(
        scene=scene.ljust(8, ' '),
        take=take.ljust(8, ' '),
        roll=roll.ljust(8, ' '),
        sound='138     ',
    )

    if choice(tf):
        flex += FLEX_120
    if choice(tf):
        flex += FLEX_200
    if choice(tf):
        flex += FLEX_300
    if choice(tf):
        flex += FLEX_400
    if choice(tf):
        flex += FLEX_500
    if choice(tf):
        flex += FLEX_600

    if slope and offset and power:
        # We need an extra space in front of offset values if they are not neg
        if offset[0] >= 0:
            offsetR = ' ' + str(offset[0]).ljust(6, ' ')[:6]
        else:
            offsetR = '' + str(offset[0]).ljust(7, ' ')[:7]
        if offset[1] >= 0:
            offsetG = ' ' + str(offset[1]).ljust(6, ' ')[:6]
        else:
            offsetG = '' + str(offset[1]).ljust(7, ' ')[:7]
        if offset[2] >= 0:
            offsetB = ' ' + str(offset[2]).ljust(6, ' ')[:6]
        else:
            offsetB = '' + str(offset[2]).ljust(7, ' ')[:7]

        flex += FLEX_701.format(
            slopeR=str(slope[0]).ljust(6, ' ')[:6],
            slopeG=str(slope[1]).ljust(6, ' ')[:6],
            slopeB=str(slope[2]).ljust(6, ' ')[:6],
            offsetR=offsetR,
            offsetG=offsetG,
            offsetB=offsetB,
            powerR=str(power[0]).ljust(6, ' ')[:6],
            powerG=str(power[1]).ljust(6, ' ')[:6],
            powerB=str(power[2]).ljust(6, ' ')[:6],
        )

    if sat:
        flex += FLEX_702.format(
            sat=str(sat).ljust(6, ' ')[:6]
        )

    return flex

#===============================================================================
# RUNNER
#===============================================================================
if __name__ == '__main__':
    unittest.main()