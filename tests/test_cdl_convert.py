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
from random import randrange
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

ALE_HEADER = """Heading
FIELD_DELIM/tTABS
VIDEO_FORMAT/t1080
AUDIO_FORMAT/t48khz
FPS/t23.976

Column
Name/tStart/tEnd/tDuration/tHandle Length/tAvid Clip Name/tScan Resolution/tASC_SAT/tASC_SOP/tScan Filename/tTotal Frame Count

Data
"""

ALE_LINE = "{name}/t{tcIn}/t{tcOut}/t{duration}/t{handleLen}/t{avidClip}/t{res}/t{sat}/t({slopeR} {slopeG} {slopeB})({offsetR} {offsetG} {offsetB})({powerR} {powerG} {powerB})/t{filename}/t{frames}\n"

#===============================================================================
# CLASSES
#===============================================================================

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
            self.cdl.offset = [-1.3782, 278.32, '0.738378233782']

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
            self.cdl.power = [1.3782, 278.32, '0.738378233782']

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
            self.cdl.slope = [1.3782, 278.32, '0.738378233782']

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
            self.cdl.sat = '26.1'

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

#===============================================================================

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

        # Build our config
        with tempfile.NamedTemporaryFile(mode='r+b') as f:
            f.write(self.file)
            self.filename = f.name
            # Calling readlines on the temp file. Without this open fails to
            # read it. I have no idea why.
            f.readlines()
            self.cdl = cdl_convert.parseCDL(f.name)[0]

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

#===============================================================================

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

        # Build our config
        with tempfile.NamedTemporaryFile(mode='r+b') as f:
            f.write(self.file)
            self.filename = f.name
            # Calling readlines on the temp file. Without this open fails to
            # read it. I have no idea why.
            f.readlines()
            self.cdl = cdl_convert.parseCDL(f.name)[0]

#===============================================================================

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

#===============================================================================

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

#===============================================================================

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
            hour = randrange(00, 23)
        if minute is None:
            minute = randrange(00, 59)
        if second is None:
            second = randrange(00, 59)
        if frame is None:
            frame = randrange(00, 23)
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
            frames='0' + str(frame) if frame < 10 else str(frame)
        )
        self.end = "{time}:{frames}".format(
            time=endTime.isoformat().split('T')[-1],
            frames='0' + str(endFrames) if endFrames < 10 else str(endFrames)
        )
        self.dur = "{time}:{frames}".format(
            time=durationTime.isoformat().split('T')[-1],
            frames='0' + str(durFrames) if durFrames < 10 else str(durFrames)
        )
        self.durFrames = duration

#===============================================================================

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

def buildALELine():
    # name usually looks like: D415_C001_01015RB
    # timecode looks like: 16:16:34:14
    # handleLen is an int: 8, 16, 32 usually
    # avidClip looks like 2.15F-3c (wtf?)
    # res looks like: 2k
    # ASC Sat and Sop like normal
    # Filename is usually the scan name, shot name, then avid clip name
    # Frames is total frames, an int
    # We'll only be using the sat sop and filename, so the rest can be random
    pass

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

if __name__ == '__main__':
    unittest.main()