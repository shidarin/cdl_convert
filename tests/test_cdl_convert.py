#/usr/bin/python
# Cdl Convert Tests
# By Sean Wallitsch, 2014/04/18
"""
Tests for all of the classes and functions inside of cdl_convert

REQUIREMENTS:

mock
"""

#===============================================================================
# IMPORTS
#===============================================================================

# Standard Imports
import datetime
import os
import mock
from random import choice, random, randrange
from StringIO import StringIO
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

#===============================================================================
# GLOBALS
#===============================================================================

# ale ==========================================================================

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
Start\tEnd\tHandle Length\tAvid Clip Name\tASC_SAT\tASC_SOP\tScan Filename\tTotal Frame Count

Data
"""
ALE_LINE_SHORT = "{tcIn}\t{tcOut}\t{handleLen}\t{avidClip}\t{sat}\t({slopeR} {slopeG} {slopeB})({offsetR} {offsetG} {offsetB})({powerR} {powerG} {powerB})\t{filename}\t{frames}\n"

# FLEx =========================================================================

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

#===============================================================================
# CLASSES
#===============================================================================

# AscCdl =======================================================================


class TestAscCdl(unittest.TestCase):
    """Tests all aspects of the AscCdl class"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):
        # Note that the file doesn't really need to exist for our test purposes
        self.cdl = cdl_convert.AscCdl(id='uniqueId', file='../testcdl.cc')

    #===========================================================================
    # TESTS
    #===========================================================================

    # Properties & Attributes ==================================================

    def testFileInReturn(self):
        """Tests that calling AscCdl.fileIn returns the file given"""
        self.assertEqual(
            os.path.abspath('../testcdl.cc'),
            self.cdl.fileIn
        )

    #===========================================================================

    def testFileInSetException(self):
        """Tests that exception raised when setting fileIn after init"""
        def testFileIn():
            self.cdl.fileIn = '../NewFile.cc'

        self.assertRaises(
            AttributeError,
            testFileIn
        )

    #===========================================================================

    def testFileOutSetException(self):
        """Tests that exception raised when attempting to set fileOut direct"""
        def testFileOut():
            self.cdl.fileOut = '../NewFile.cc'

        self.assertRaises(
            AttributeError,
            testFileOut
        )

    #===========================================================================

    def testIdReturn(self):
        """Tests that calling AscCdl.id returns the id"""
        self.assertEqual(
            'uniqueId',
            self.cdl.id
        )

    #===========================================================================

    def testIdSetException(self):
        """Tests that exception raised when attempting to set cdl after init"""
        def testId():
            self.cdl.id = 'betterId'

        self.assertRaises(
            AttributeError,
            testId
        )

    #===========================================================================

    def testOffsetSetAndGet(self):
        """Tests setting and getting the offset"""

        offset = [-1.3782, 278.32, 0.738378233782]

        self.cdl.offset = offset

        self.assertEqual(
            offset,
            self.cdl.offset
        )

    #===========================================================================

    def testOffsetBadLength(self):
        """Tests passing offset an incorrect length list"""
        def setOffset():
            self.cdl.offset = ['banana']

        self.assertRaises(
            ValueError,
            setOffset
        )

    #===========================================================================

    def testOffsetSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setOffset():
            self.cdl.offset = [-1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setOffset
        )

    #===========================================================================

    def testOffsetBadType(self):
        """Tests passing offset a correct length but bad type value"""
        def setOffset():
            self.cdl.offset = 'ban'

        self.assertRaises(
            TypeError,
            setOffset
        )

    #===========================================================================

    def testOffsetBecomesList(self):
        """Tests offset is converted to list from tuple"""

        offset = (-1.3782, 278.32, 0.738378233782)

        self.cdl.offset = offset

        self.assertEqual(
            list(offset),
            self.cdl.offset
        )

    #===========================================================================

    def testPowerSetAndGet(self):
        """Tests setting and getting the power"""

        power = [1.3782, 278.32, 0.738378233782]

        self.cdl.power = power

        self.assertEqual(
            power,
            self.cdl.power
        )

    #===========================================================================

    def testPowerSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setPower():
            self.cdl.power = [-1.3782, 278.32, 0.738378233782]

        self.assertRaises(
            ValueError,
            setPower
        )

    #===========================================================================

    def testPowerSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setPower():
            self.cdl.power = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setPower
        )

    #===========================================================================

    def testPowerBadLength(self):
        """Tests passing power an incorrect length list"""
        def setPower():
            self.cdl.power = ['banana']

        self.assertRaises(
            ValueError,
            setPower
        )

    #===========================================================================

    def testPowerBadType(self):
        """Tests passing power a correct length but bad type value"""
        def setPower():
            self.cdl.power = 'ban'

        self.assertRaises(
            TypeError,
            setPower
        )

    #===========================================================================

    def testPowerBecomesList(self):
        """Tests power is converted to list from tuple"""

        power = (1.3782, 278.32, 0.738378233782)

        self.cdl.power = power

        self.assertEqual(
            list(power),
            self.cdl.power
        )

    #===========================================================================

    def testSlopeSetAndGet(self):
        """Tests setting and getting the slope"""

        slope = [1.3782, 278.32, 0.738378233782]

        self.cdl.slope = slope

        self.assertEqual(
            slope,
            self.cdl.slope
        )

    #===========================================================================

    def testSlopeSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setSlope():
            self.cdl.slope = [-1.3782, 278.32, 0.738378233782]

        self.assertRaises(
            ValueError,
            setSlope
        )

    #===========================================================================

    def testSlopeSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setSlope():
            self.cdl.slope = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setSlope
        )

    #===========================================================================

    def testSlopeBadLength(self):
        """Tests passing slope an incorrect length list"""
        def setSlope():
            self.cdl.slope = ['banana']

        self.assertRaises(
            ValueError,
            setSlope
        )

    #===========================================================================

    def testSlopeBadType(self):
        """Tests passing slope a correct length but bad type value"""
        def setSlope():
            self.cdl.slope = 'ban'

        self.assertRaises(
            TypeError,
            setSlope
        )

    #===========================================================================

    def testSlopeBecomesList(self):
        """Tests slope is converted to list from tuple"""

        slope = (1.3782, 278.32, 0.738378233782)

        self.cdl.slope = slope

        self.assertEqual(
            list(slope),
            self.cdl.slope
        )

    #===========================================================================

    def testSatSetAndGet(self):
        """Tests setting and getting saturation"""

        sat = 34.3267

        self.cdl.sat = sat

        self.assertEqual(
            sat,
            self.cdl.sat
        )

    #===========================================================================

    def testSatSetNegative(self):
        """Tests that a ValueError is raised if sat is set to negative"""
        def setSat():
            self.cdl.sat = -376.23

        self.assertRaises(
            ValueError,
            setSat
        )
    #===========================================================================

    def testSatSetString(self):
        """Tests that a TypeError is raised if sat is set to string"""
        def setSat():
            self.cdl.sat = 'banana'

        self.assertRaises(
            TypeError,
            setSat
        )

    #===========================================================================

    def testSatBecomesFloat(self):
        """Tests that saturation is converted to float from int"""
        sat = 3

        self.cdl.sat = sat

        self.assertEqual(
            float(sat),
            self.cdl.sat
        )

    # determineDest() ==========================================================

    def testDetermineDest(self):
        """Tests that determine destination is calculated correctly"""
        self.cdl.determineDest('cdl')

        dir = os.path.abspath('../')
        filename = os.path.join(dir, 'uniqueId.cdl')

        self.assertEqual(
            filename,
            self.cdl.fileOut
        )

# ale ==========================================================================


class TestParseALEBasic(unittest.TestCase):
    """Tests basic parsing of a standard ALE"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):
        self.slope1 = [1.329, 0.9833, 1.003]
        self.offset1 = [0.011, 0.013, 0.11]
        self.power1 = [.993, .998, 1.0113]
        self.sat1 = 1.01

        line1 = buildALELine(self.slope1, self.offset1, self.power1, self.sat1,
                             'bb94_x103_line1')

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = [137829.329, 4327890.9833, 3489031.003]
        self.offset2 = [-3424.011, -342789423.013, -4238923.11]
        self.power2 = [3271893.993, .0000998, 0.0000000000000000113]
        self.sat2 = 1798787.01

        line2 = buildALELine(self.slope2, self.offset2, self.power2, self.sat2,
                             'bb94_x104_line2')

        self.slope3 = [1.2, 2.32, 10.82]
        self.offset3 = [-1.3782, 278.32, 0.738378233782]
        self.power3 = [1.329, 0.9833, 1.003]
        self.sat3 = 0.99

        line3 = buildALELine(self.slope3, self.offset3, self.power3, self.sat3,
                             'bb94_x105_line3')

        self.file = ALE_HEADER + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='r+b', delete=False) as f:
            f.write(self.file)
            self.filename = f.name

        cdls = cdl_convert.parseALE(self.filename)
        self.cdl1 = cdls[0]
        self.cdl2 = cdls[1]
        self.cdl3 = cdls[2]

    #===========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)

    #===========================================================================
    # TESTS
    #===========================================================================

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


class TestParseALEShort(TestParseALEBasic):
    """Tests basic parsing of a shortened ALE with different tab"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):
        self.slope1 = [1.329, 0.9833, 1.003]
        self.offset1 = [0.011, 0.013, 0.11]
        self.power1 = [.993, .998, 1.0113]
        self.sat1 = 1.01

        line1 = buildALELine(self.slope1, self.offset1, self.power1, self.sat1,
                             'bb94_x103_line1', short=True)

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = [137829.329, 4327890.9833, 3489031.003]
        self.offset2 = [-3424.011, -342789423.013, -4238923.11]
        self.power2 = [3271893.993, .0000998, 0.0000000000000000113]
        self.sat2 = 1798787.01

        line2 = buildALELine(self.slope2, self.offset2, self.power2, self.sat2,
                             'bb94_x104_line2', short=True)

        self.slope3 = [1.2, 2.32, 10.82]
        self.offset3 = [-1.3782, 278.32, 0.738378233782]
        self.power3 = [1.329, 0.9833, 1.003]
        self.sat3 = 0.99

        line3 = buildALELine(self.slope3, self.offset3, self.power3, self.sat3,
                             'bb94_x105_line3', short=True)

        self.file = ALE_HEADER_SHORT + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='r+b', delete=False) as f:
            f.write(self.file)
            self.filename = f.name

        cdls = cdl_convert.parseALE(self.filename)
        self.cdl1 = cdls[0]
        self.cdl2 = cdls[1]
        self.cdl3 = cdls[2]

# cdl ==========================================================================


class TestParseCDLBasic(unittest.TestCase):
    """Tests parsing a space separated cdl, a Rhythm & Hues format"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):
        self.slope = [1.329, 0.9833, 1.003]
        self.offset = [0.011, 0.013, 0.11]
        self.power = [.993, .998, 1.0113]
        self.sat = 1.01

        self.file = buildCDL(self.slope, self.offset, self.power, self.sat)

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='r+b', delete=False) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdl = cdl_convert.parseCDL(self.filename)[0]

    #===========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)

    #===========================================================================
    # TESTS
    #===========================================================================

    def testId(self):
        """Tests that id was set to the filename without extension"""
        id = os.path.basename(self.filename).split('.')[0]
        self.assertEqual(
            id,
            self.cdl.id
        )

    #===========================================================================

    def testSlope(self):
        """Tests that slope was set correctly"""
        self.assertEqual(
            self.slope,
            self.cdl.slope
        )

    #===========================================================================

    def testOffset(self):
        """Tests that offset was set correctly"""
        self.assertEqual(
            self.offset,
            self.cdl.offset
        )

    #===========================================================================

    def testPower(self):
        """Tests that power was set correctly"""
        self.assertEqual(
            self.power,
            self.cdl.power
        )

    #===========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        self.assertEqual(
            self.sat,
            self.cdl.sat
        )


class TestParseCDLOdd(TestParseCDLBasic):
    """Tests parsing a space separated cdl with odd but valid numbers"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):
        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope = [137829.329, 4327890.9833, 3489031.003]
        self.offset = [-3424.011, -342789423.013, -4238923.11]
        self.power = [3271893.993, .0000998, 0.0000000000000000113]
        self.sat = 1798787.01

        self.file = buildCDL(self.slope, self.offset, self.power, self.sat)

        # Build our cdl
        with tempfile.NamedTemporaryFile(mode='r+b', delete=False) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdl = cdl_convert.parseCDL(self.filename)[0]


class TestWriteCDLBasic(unittest.TestCase):
    """Tests writing a space separated cdl with basic values"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):
        self.slope = [1.329, 0.9833, 1.003]
        self.offset = [0.011, 0.013, 0.11]
        self.power = [.993, .998, 1.0113]
        self.sat = 1.01

        self.cdl = cdl_convert.AscCdl('uniqueId', '../theVeryBestFile.ale')

        self.cdl.determineDest('cdl')
        self.cdl.slope = self.slope
        self.cdl.offset = self.offset
        self.cdl.power = self.power
        self.cdl.sat = self.sat

        self.file = buildCDL(self.slope, self.offset, self.power, self.sat)

        self.mockOpen = mock.mock_open()

        with mock.patch('__builtin__.open', self.mockOpen, create=True):
            cdl_convert.writeCDL(self.cdl)

    #===========================================================================
    # TESTS
    #===========================================================================

    def testOpen(self):
        """Tests that open was called correctly"""
        self.mockOpen.assert_called_once_with(self.cdl.fileOut, 'wb')

    #===========================================================================

    def testContent(self):
        """Tests that writeCDL wrote the correct CDL"""
        handle = self.mockOpen()
        handle.write.assert_called_once_with(self.file)


class TestWriteCDLOdd(TestWriteCDLBasic):
    """Tests writing a space separated cdl with basic values"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):
        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope = [137829.329, 4327890.9833, 3489031.003]
        self.offset = [-3424.011, -342789423.013, -4238923.11]
        self.power = [3271893.993, .0000998, 0.0000000000000000113]
        self.sat = 1798787.01

        self.cdl = cdl_convert.AscCdl('uniqueId', '../theVeryBestFile.ale')

        self.cdl.determineDest('cdl')
        self.cdl.slope = self.slope
        self.cdl.offset = self.offset
        self.cdl.power = self.power
        self.cdl.sat = self.sat

        self.file = buildCDL(self.slope, self.offset, self.power, self.sat)

        self.mockOpen = mock.mock_open()

        with mock.patch('__builtin__.open', self.mockOpen, create=True):
            cdl_convert.writeCDL(self.cdl)

# FLEx =========================================================================


class TestParseFLExBasic(unittest.TestCase):
    """Tests basic parsing of a standard FLEx

    FLEx can't store more than 6 sig digits, so we'll stay within that limit"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = "Bob's Big Apple Break, into the big apple! Part 365   H"

        self.slope1 = [1.329, 0.9833, 1.003]
        self.offset1 = [0.011, 0.013, 0.11]
        self.power1 = [.993, .998, 1.0113]
        self.sat1 = 1.01

        line1 = buildFLExTake(self.slope1, self.offset1, self.power1, self.sat1,
                             'bb94', 'x103', 'line1')

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = [13.329, 4.9334, 348908]
        self.offset2 = [-3424.0, -34.013, -642389]
        self.power2 = [37.993, .00009, 0.0000]
        self.sat2 = 177.01

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2, self.sat2,
                             'bb94', 'x104', 'line2')

        self.slope3 = [1.2, 2.32, 10.82]
        self.offset3 = [-1.3782, 278.32, 0.7383]
        self.power3 = [1.329, 0.9833, 1.003]
        self.sat3 = 0.99

        line3 = buildFLExTake(self.slope3, self.offset3, self.power3, self.sat3,
                             'bb94', 'x105', 'line3')

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='r+b', delete=False) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdls = cdl_convert.parseFLEx(self.filename)
        self.cdl1 = self.cdls[0]
        self.cdl2 = self.cdls[1]
        self.cdl3 = self.cdls[2]

    #===========================================================================

    def tearDown(self):
        # The system should clean these up automatically,
        # but we'll be neat.
        os.remove(self.filename)

    #===========================================================================
    # TESTS
    #===========================================================================

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

        for i in xrange(3):
            self.assertEqual(
                self.title,
                self.cdls[i].description
            )


class TestParseFLExMissingNames(TestParseFLExBasic):
    """Tests basic parsing of a Flex where some takes are missing name fields"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = "Bob's Big Apple Break, into the big apple! Part 365   H"

        self.slope1 = [1.329, 0.9833, 1.003]
        self.offset1 = [0.011, 0.013, 0.11]
        self.power1 = [.993, .998, 1.0113]
        self.sat1 = 1.01

        line1 = buildFLExTake(self.slope1, self.offset1, self.power1, self.sat1,
                             'bb94', 'x103', 'line1')

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = [13.329, 4.9334, 348908]
        self.offset2 = [-3424.0, -34.013, -642389]
        self.power2 = [37.993, .00009, 0.0000]
        self.sat2 = 177.01

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2, self.sat2,
                             'bb94', 'x104')

        self.slope3 = [1.2, 2.32, 10.82]
        self.offset3 = [-1.3782, 278.32, 0.7383]
        self.power3 = [1.329, 0.9833, 1.003]
        self.sat3 = 0.99

        line3 = buildFLExTake(self.slope3, self.offset3, self.power3, self.sat3,
                             'bb94')

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='r+b', delete=False) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdls = cdl_convert.parseFLEx(self.filename)
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
            self.cdl1.id
        )

        self.assertEqual(
            'bb94_x104',
            self.cdl2.id
        )

        self.assertEqual(
            'bb94',
            self.cdl3.id
        )


class TestParseFLExTitleOnly(TestParseFLExBasic):
    """Tests basic parsing of a Flex where no takes have scn/roll/take fields"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = "Bob's Big Apple Break, into the big apple! Part.365   H"

        self.slope1 = [1.329, 0.9833, 1.003]
        self.offset1 = [0.011, 0.013, 0.11]
        self.power1 = [.993, .998, 1.0113]
        self.sat1 = 1.01

        line1 = buildFLExTake(self.slope1, self.offset1, self.power1, self.sat1)

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = [13.329, 4.9334, 348908]
        self.offset2 = [-3424.0, -34.013, -642389]
        self.power2 = [37.993, .00009, 0.0000]
        self.sat2 = 177.01

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2, self.sat2)

        self.slope3 = [1.2, 2.32, 10.82]
        self.offset3 = [-1.3782, 278.32, 0.7383]
        self.power3 = [1.329, 0.9833, 1.003]
        self.sat3 = 0.99

        line3 = buildFLExTake(self.slope3, self.offset3, self.power3, self.sat3)

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='r+b', delete=False) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdls = cdl_convert.parseFLEx(self.filename)
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
            self.cdl1.id
        )

        self.assertEqual(
            "Bobs_Big_Apple_Break_into_the_big_apple_Part.365___H002",
            self.cdl2.id
        )

        self.assertEqual(
            "Bobs_Big_Apple_Break_into_the_big_apple_Part.365___H003",
            self.cdl3.id
        )


class TestParseFLExNoTitle(TestParseFLExBasic):
    """Tests basic parsing of a Flex where id is based on filename"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):

        self.title = ''

        self.slope1 = [1.329, 0.9833, 1.003]
        self.offset1 = [0.011, 0.013, 0.11]
        self.power1 = [.993, .998, 1.0113]
        self.sat1 = 1.01

        line1 = buildFLExTake(self.slope1, self.offset1, self.power1, self.sat1)

        # Note that there are limits to the floating point precision here.
        # Python will not parse numbers exactly with numbers with more
        # significant whole and decimal digits
        self.slope2 = [13.329, 4.9334, 348908]
        self.offset2 = [-3424.0, -34.013, -642389]
        self.power2 = [37.993, .00009, 0.0000]
        self.sat2 = 177.01

        line2 = buildFLExTake(self.slope2, self.offset2, self.power2, self.sat2)

        self.slope3 = [1.2, 2.32, 10.82]
        self.offset3 = [-1.3782, 278.32, 0.7383]
        self.power3 = [1.329, 0.9833, 1.003]
        self.sat3 = 0.99

        line3 = buildFLExTake(self.slope3, self.offset3, self.power3, self.sat3)

        self.file = FLEX_HEADER.format(title=self.title) + line1 + line2 + line3

        # Build our ale
        with tempfile.NamedTemporaryFile(mode='r+b', delete=False) as f:
            f.write(self.file)
            self.filename = f.name

        self.cdls = cdl_convert.parseFLEx(self.filename)
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
            self.cdl1.id
        )

        self.assertEqual(
            "{0}002".format(filename),
            self.cdl2.id
        )

        self.assertEqual(
            "{0}003".format(filename),
            self.cdl3.id
        )

    #===========================================================================

    def testDescription(self):
        """Tests that the descriptions have been parsed correctly"""

        for i in xrange(3):
            self.assertIsNone(
                self.cdls[i].description
            )

# sanitize() ===================================================================


class TestSanitize(unittest.TestCase):
    """Tests the helper function sanitize()"""

    def testSpaces(self):
        """Tests that spaces are replaced with underscores"""
        result = cdl_convert.sanitize('banana apple blueberry')

        self.assertEqual(
            'banana_apple_blueberry',
            result
        )

    #===========================================================================

    def testUnderscoresOkay(self):
        """Tests that underscores pass through intact"""
        result = cdl_convert.sanitize('a_b_c')

        self.assertEqual(
            'a_b_c',
            result
        )

    #===========================================================================

    def testPeriodsOkay(self):
        """Tests that periods pass through intact"""
        result = cdl_convert.sanitize('a.b.c')

        self.assertEqual(
            'a.b.c',
            result
        )

    #===========================================================================

    def testLeadingPeriodRemove(self):
        """Tests that leading periods are removed"""
        result = cdl_convert.sanitize('.abc')

        self.assertEqual(
            'abc',
            result
        )

    #===========================================================================

    def testLeadingUnderscoreRemove(self):
        """Tests that leading underscores are removed"""
        result = cdl_convert.sanitize('_abc')

        self.assertEqual(
            'abc',
            result
        )

    #===========================================================================

    def testCommonBadChars(self):
        """Tests that common bad characters are removed"""
        result = cdl_convert.sanitize('a@$#b!)(*$%&^c`/\\"\';:<>,d')

        self.assertEqual(
            'abcd',
            result
        )

# parseArgs() ==================================================================

class TestParseArgs(unittest.TestCase):
    """Tests that arguments are being parsed correctly"""

    #===========================================================================
    # SETUP & TEARDOWN
    #===========================================================================

    def setUp(self):
        self.sysargv = sys.argv

    #===========================================================================

    def tearDown(self):
        sys.argv = self.sysargv

    #===========================================================================
    # TESTS
    #===========================================================================

    def testInputPositionalArg(self):
        """Tests that the input arg is positionally gotten correctly"""

        sys.argv = ['scriptname', 'inputFile.txt']

        args = cdl_convert.parseArgs()

        self.assertEqual(
            'inputFile.txt',
            args.input_file
        )

    #===========================================================================

    def testGoodInputFormat(self):
        """Tests that a good input format is accepted and lowered"""

        sys.argv = ['scriptname', 'inputFile', '-i', 'ALE']

        args = cdl_convert.parseArgs()

        self.assertEqual(
            'ale',
            args.input
        )

    #===========================================================================

    def testBadInputFormat(self):
        """Tests that a bad input format is rejected with ValueError"""

        sys.argv = ['scriptname', 'inputFile', '-i', 'HUYYE']

        self.assertRaises(
            ValueError,
            cdl_convert.parseArgs
        )

    #===========================================================================

    def testGoodOutputFormat(self):
        """Tests that a good output format is accepted and lowered"""

        sys.argv = ['scriptname', 'inputFile', '-o', 'CDL']

        args = cdl_convert.parseArgs()

        self.assertEqual(
            ['cdl'],
            args.output
        )

    #===========================================================================

    def testMultipleGoodOutputFormat(self):
        """Tests that multiple good output formats are accepted and lowered"""

        sys.argv = ['scriptname', 'inputFile', '-o', 'CDL,CC']

        args = cdl_convert.parseArgs()

        self.assertEqual(
            ['cdl', 'cc'],
            args.output
        )

    #===========================================================================

    def testBadOutputFormat(self):
        """Tests that a bad output format is rejected with ValueError"""

        sys.argv = ['scriptname', 'inputFile', '-o', 'HUYYE']

        self.assertRaises(
            ValueError,
            cdl_convert.parseArgs
        )

    #===========================================================================

    def testGoodWithBadOutputFormat(self):
        """Tests that a bad output format is rejected with ValueError"""

        sys.argv = ['scriptname', 'inputFile', '-o', 'cc,HUYYE']

        self.assertRaises(
            ValueError,
            cdl_convert.parseArgs
        )

    #===========================================================================

    def testNoProvidedOutput(self):
        """Tests that no provided output format is defaulted to cc"""

        sys.argv = ['scriptname', 'inputFile']

        args = cdl_convert.parseArgs()

        self.assertEqual(
            ['cc'],
            args.output
        )

# Test Classes =================================================================

# TimeCodeSegment is from my SMTPE Timecode gist at:
# https://gist.github.com/shidarin/11091783


class TimeCodeSegment(object):
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
    def __init__(self, hour=None, minute=None, second=None, frame=None,
                 duration=None, fps=24):
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

        durSeconds = duration / fps
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
            time=startTime.isoformat().split('T')[-1],
            frames=str(frame).rjust(2, '0')
        )
        self.end = "{time}:{frames}".format(
            time=endTime.isoformat().split('T')[-1],
            frames=str(endFrames).rjust(2, '0')
        )
        self.dur = "{time}:{frames}".format(
            time=durationTime.isoformat().split('T')[-1],
            frames=str(durFrames).rjust(2, '0')
        )
        self.durFrames = duration


class TestTimeCodeSegment(unittest.TestCase):
    """Tests TimeCodeSegment class for correct functionality"""

    #===========================================================================
    # TESTS
    #===========================================================================

    def testWholeSeconds(self):
        """Tests timecode where seconds are an even multiple of frames"""
        tc = TimeCodeSegment(12, 0, 0, 0, 24)

        self.assertEqual(
            '12:00:00:00',
            tc.start
        )

        self.assertEqual(
            '12:00:01:00',
            tc.end
        )

        self.assertEqual(
            '00:00:01:00',
            tc.dur
        )

    #===========================================================================

    def testLessThanOneSecond(self):
        """Tests timecode where there's less than a second of duration"""
        tc = TimeCodeSegment(12, 0, 0, 0, 4)

        self.assertEqual(
            '12:00:00:04',
            tc.end
        )

        self.assertEqual(
            '00:00:00:04',
            tc.dur
        )

    #===========================================================================

    def testMoreThanOneSecond(self):
        """Tests timecode where there's more than a second of duration"""
        tc = TimeCodeSegment(12, 0, 0, 0, 25)

        self.assertEqual(
            '12:00:01:01',
            tc.end
        )

        self.assertEqual(
            '00:00:01:01',
            tc.dur
        )

    #===========================================================================

    def testUnevenCombination(self):
        """Tests timecode where there's less than a second of duration"""
        tc = TimeCodeSegment(12, 0, 0, 15, 10)

        self.assertEqual(
            '12:00:00:15',
            tc.start
        )

        self.assertEqual(
            '12:00:01:01',
            tc.end
        )

        self.assertEqual(
            '00:00:00:10',
            tc.dur
        )

    #===========================================================================

    def testAddManyHours(self):
        """Tests adding many hours, minutes and seconds of duration"""
        tc = TimeCodeSegment(0, 0, 0, 1, 1016356)

        self.assertEqual(
            '00:00:00:01',
            tc.start
        )

        self.assertEqual(
            '11:45:48:05',
            tc.end
        )

        self.assertEqual(
            '11:45:48:04',
            tc.dur
        )

    #===========================================================================

    def testRollover(self):
        """Tests timecode that rolls over 24 hours"""
        tc = TimeCodeSegment(23, 59, 59, 23, 2)

        self.assertEqual(
            '23:59:59:23',
            tc.start
        )

        self.assertEqual(
            '00:00:00:01',
            tc.end
        )

        self.assertEqual(
            '00:00:00:02',
            tc.dur
        )

    #===========================================================================

    def test30Fps(self):
        """Tests timecode with 30 fps"""
        tc = TimeCodeSegment(12, 0, 0, 15, 10, fps=30)

        self.assertEqual(
            '12:00:00:15',
            tc.start
        )

        self.assertEqual(
            '12:00:00:25',
            tc.end
        )

        self.assertEqual(
            '00:00:00:10',
            tc.dur
        )

    #===========================================================================

    def test60Fps(self):
        """Tests timecode with 60 fps"""
        tc = TimeCodeSegment(12, 0, 0, 15, 40, fps=60)

        self.assertEqual(
            '12:00:00:15',
            tc.start
        )

        self.assertEqual(
            '12:00:00:55',
            tc.end
        )

        self.assertEqual(
            '00:00:00:40',
            tc.dur
        )

    #===========================================================================

    def testAllRandomSetDuration(self):
        """Tests random timecode with set long duration"""
        tc = TimeCodeSegment(fps=60, duration=5183999)

        self.assertEqual(
            '23:59:59:59',
            tc.dur
        )

        self.assertEqual(
            5183999,
            tc.durFrames
        )

    #===========================================================================

    def testDurationUnderFiveMinutes(self):
        """Tests that duration when not provided is kept under 5 minutes"""
        tc = TimeCodeSegment(fps=24)

        self.assertLess(
            tc.durFrames,
            7200
        )

#===============================================================================
# FUNCTIONS
#===============================================================================

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
            filename=filename,
            frames=tc.durFrames
        )

    return ale

#===============================================================================

def buildCDL(slope, offset, power, sat):
    """Populates a CDL string and returns it"""

    ssCdl = cdl_convert.CDL.format(
        slopeR=slope[0],
        slopeG=slope[1],
        slopeB=slope[2],
        offsetR=offset[0],
        offsetG=offset[1],
        offsetB=offset[2],
        powerR=power[0],
        powerG=power[1],
        powerB=power[2],
        sat=sat
    )

    return ssCdl

#===============================================================================

def buildFLExTake(slope, offset, power, sat, scene=None, take=None, roll=None):
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

    # We need an extra space in front of offset values if they are not negative
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

    flex += FLEX_702.format(
        sat=str(sat).ljust(6, ' ')[:6]
    )

    return flex

if __name__ == '__main__':
    unittest.main()