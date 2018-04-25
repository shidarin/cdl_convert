#!/usr/bin/env python
"""
Tests the ale related functions of cdl_convert

REQUIREMENTS:

mock
"""

#==============================================================================
# IMPORTS
#==============================================================================

# Standard Imports
from decimal import Decimal
import os
from random import choice, randrange
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

import cdl_convert
from test_cdl_convert import TimeCodeSegment

#==============================================================================
# GLOBALS
#==============================================================================

ALE_HEADER = """Heading
FIELD_DELIM\tTABS
VIDEO_FORMAT\t1080
AUDIO_FORMAT\t48khz
FPS\t24

Column
Name\tStart\tEnd\tDuration\tHandle Length\tAvid Clip Name\tScan Resolution\tASC_SAT\tASC_SOP\tScan Filename\tTotal Frame Count

Data
"""
ALE_LINE = "{name}\t{tcIn}\t{tcOut}\t{duration}\t{handleLen}\t{avidClip}\t{res}\t{sat}\t({slopeR} {slopeG} {slopeB})({offsetR} {offsetG} {offsetB})({powerR} {powerG} {powerB})\t{filename}\t{frames}\n"

ALE_HEADER_SHORT = """Heading
FIELD_DELIM\tTABS
VIDEO_FORMAT\t1080
AUDIO_FORMAT\t48khz
FPS\t24

Column
Start\tEnd\tHandle Length\tAvid Clip Name\tASC_SAT\tASC_SOP\tName

Data
"""
ALE_LINE_SHORT = "{tcIn}\t{tcOut}\t{handleLen}\t{avidClip}\t{sat}\t({slopeR} {slopeG} {slopeB})({offsetR} {offsetG} {offsetB})({powerR} {powerG} {powerB})\t{name}\n"

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

# ale parse ===================================================================


class TestParseALEBasic(unittest.TestCase):
    """Tests basic parsing of a standard ALE"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope1 = decimalize(1.329, 0.9833, 1.003)
        self.offset1 = decimalize(0.011, 0.013, 0.11)
        self.power1 = decimalize(.993, .998, 1.0113)
        self.sat1 = Decimal('1.01')

        line1 = buildALELine(self.slope1, self.offset1, self.power1, self.sat1,
                             'bb94_x103_line1')

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = decimalize(137829.329, 4327890.9833, 3489031.003)
        self.offset2 = decimalize(-3424.011, -342789423.013, -4238923.11)
        self.power2 = decimalize(3271893.993, .0000998, 0.0000000000000000113)
        self.sat2 = Decimal('1798787.01')

        line2 = buildALELine(self.slope2, self.offset2, self.power2, self.sat2,
                             'bb94_x104_line2')

        self.slope3 = decimalize(1.2, 2.32, 10.82)
        self.offset3 = decimalize(-1.3782, 278.32, 0.738378233782)
        self.power3 = decimalize(1.329, 0.9833, 1.003)
        self.sat3 = Decimal('0.99')

        line3 = buildALELine(self.slope3, self.offset3, self.power3, self.sat3,
                             'bb94_x105_line3')

        self.file = ALE_HEADER + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdls = cdl_convert.parse_ale(self.filename)
        self.cdl1 = self.cdls.color_corrections[0]
        self.cdl2 = self.cdls.color_corrections[1]
        self.cdl3 = self.cdls.color_corrections[2]

    #==========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testCollection(self):
        """Tests that we were returned a ColorCollection"""
        self.assertEqual(
            cdl_convert.ColorCollection,
            self.cdls.__class__
        )

    #==========================================================================

    def testFileIn(self):
        """Tests that file_in has been set on the collection correctly"""
        self.assertEqual(
            self.filename,
            self.cdls.file_in
        )

    #==========================================================================

    def testType(self):
        """Test that the type of the collection is set to ccc"""
        self.assertEqual(
            'ccc',
            self.cdls.type
        )

    #==========================================================================

    def testId(self):
        """Tests that filenames were parsed correctly"""

        self.assertEqual(
            'bb94_x103_line1',
            self.cdl1.id
        )

        self.assertEqual(
            'bb94_x104_line2',
            self.cdl2.id
        )

        self.assertEqual(
            'bb94_x105_line3',
            self.cdl3.id
        )

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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


class TestParseALEShort(TestParseALEBasic):
    """Tests basic parsing of a shortened ALE with different tab"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope1 = decimalize(1.329, 0.9833, 1.003)
        self.offset1 = decimalize(0.011, 0.013, 0.11)
        self.power1 = decimalize(.993, .998, 1.0113)
        self.sat1 = Decimal('1.01')

        line1 = buildALELine(self.slope1, self.offset1, self.power1, self.sat1,
                             'bb94_x103_line1', short=True)

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = decimalize(137829.329, 4327890.9833, 3489031.003)
        self.offset2 = decimalize(-3424.011, -342789423.013, -4238923.11)
        self.power2 = decimalize(3271893.993, .0000998, 0.0000000000000000113)
        self.sat2 = Decimal('1798787.01')

        line2 = buildALELine(self.slope2, self.offset2, self.power2, self.sat2,
                             'bb94_x104_line2', short=True)

        self.slope3 = decimalize(1.2, 2.32, 10.82)
        self.offset3 = decimalize(-1.3782, 278.32, 0.738378233782)
        self.power3 = decimalize(1.329, 0.9833, 1.003)
        self.sat3 = Decimal('0.99')

        line3 = buildALELine(self.slope3, self.offset3, self.power3, self.sat3,
                             'bb94_x105_line3', short=True)

        self.file = ALE_HEADER_SHORT + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdls = cdl_convert.parse_ale(self.filename)
        self.cdl1 = self.cdls.color_corrections[0]
        self.cdl2 = self.cdls.color_corrections[1]
        self.cdl3 = self.cdls.color_corrections[2]


class TestParseALEShortAndBlankLines(TestParseALEBasic):
    """Tests basic parsing of a shortened ALE with line breaks"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope1 = decimalize(1.329, 0.9833, 1.003)
        self.offset1 = decimalize(0.011, 0.013, 0.11)
        self.power1 = decimalize(.993, .998, 1.0113)
        self.sat1 = Decimal('1.01')

        line1 = buildALELine(self.slope1, self.offset1, self.power1, self.sat1,
                             'bb94_x103_line1', short=True)

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = decimalize(137829.329, 4327890.9833, 3489031.003)
        self.offset2 = decimalize(-3424.011, -342789423.013, -4238923.11)
        self.power2 = decimalize(3271893.993, .0000998, 0.0000000000000000113)
        self.sat2 = Decimal('1798787.01')

        line2 = buildALELine(self.slope2, self.offset2, self.power2, self.sat2,
                             'bb94_x104_line2', short=True)

        self.slope3 = decimalize(1.2, 2.32, 10.82)
        self.offset3 = decimalize(-1.3782, 278.32, 0.738378233782)
        self.power3 = decimalize(1.329, 0.9833, 1.003)
        self.sat3 = Decimal('0.99')

        line3 = buildALELine(self.slope3, self.offset3, self.power3, self.sat3,
                             'bb94_x105_line3', short=True)

        self.file = ALE_HEADER_SHORT.replace('Column', 'Column\n\n').replace('Data', 'Data\n\n') + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdls = cdl_convert.parse_ale(self.filename)
        self.cdl1 = self.cdls.color_corrections[0]
        self.cdl2 = self.cdls.color_corrections[1]
        self.cdl3 = self.cdls.color_corrections[2]

#==============================================================================
# FUNCTIONS
#==============================================================================


def buildALELine(slope, offset, power, sat, filename, short=False):
    """Builds a tab delineated ALE EDL line"""
    # name usually looks like: D415_C001_01015RB
    # timecode looks like: 16:16:34:14
    # handleLen is an int: 8, 16, 32 usually
    # avidClip looks like 3.10F-2b (wtf?)
    # res looks like: 2k
    # ASC Sat and Sop like normal
    # Filename is usually the scan name, shot name, then avid clip name
    # Frames is total frames, an int
    # We'll only be using the sat sop and filename, so the rest can be random
    tc = TimeCodeSegment()

    name = "{a}{reelA}_{b}{reelB}_{frame}{c}{d}".format(
        a=choice(UPPER),
        reelA=str(randrange(0, 1000)).rjust(3, '0'),
        b=choice(UPPER),
        reelB=str(randrange(0, 1000)).rjust(3, '0'),
        frame=str(randrange(0, 10000)).rjust(4, '0'),
        c=choice(UPPER),
        d=choice(UPPER),
    )

    avidClip = "{major}.{minor}{a}-{ver}{b}".format(
        major=randrange(1, 10),
        minor=randrange(10, 100),
        a=choice(UPPER),
        ver=randrange(1, 10),
        b=choice(LOWER),
    )

    if not short:
        ale = ALE_LINE.format(
            name=name,
            tcIn=tc.start,
            tcOut=tc.end,
            duration=tc.dur,
            handleLen=randrange(1, 32),
            avidClip=avidClip,
            res='2k',
            sat=sat,
            slopeR=slope[0],
            slopeG=slope[1],
            slopeB=slope[2],
            offsetR=offset[0],
            offsetG=offset[1],
            offsetB=offset[2],
            powerR=power[0],
            powerG=power[1],
            powerB=power[2],
            filename=filename,
            frames=tc.durFrames
        )
    else:
        ale = ALE_LINE_SHORT.format(
            name=filename,
            tcIn=tc.start,
            tcOut=tc.end,
            handleLen=randrange(1, 32),
            avidClip=avidClip,
            sat=sat,
            slopeR=slope[0],
            slopeG=slope[1],
            slopeB=slope[2],
            offsetR=offset[0],
            offsetG=offset[1],
            offsetB=offset[2],
            powerR=power[0],
            powerG=power[1],
            powerB=power[2],
        )

    return ale


def decimalize(*args):
    """Converts a list of floats/ints to Decimal list"""
    return tuple([Decimal(str(i)) for i in args])

#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
