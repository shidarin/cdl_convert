#!/usr/bin/env python
"""
Tests for all of the generic functions of cdl_convert

REQUIREMENTS:

mock
"""

#==============================================================================
# IMPORTS
#==============================================================================

# Standard Imports
import datetime
try:
    from unittest import mock
except ImportError:
    import mock
import os
from random import randrange
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
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
# TEST CLASSES
#==============================================================================

# _de_exponent() ==============================================================


class TestDeExponent(unittest.TestCase):
    """Throws a bunch of scientific notation at de_exponent"""

    def testNegativeExp(self):
        """Tests a basic negative value"""
        value = 0.0000000000000000113
        value_string = '0.0000000000000000113'

        self.assertEqual(
            value_string,
            cdl_convert._de_exponent(value)
        )

    #==========================================================================

    def testNegativeExp2(self):
        """Tests a basic negative value"""
        value = .0000998
        value_string = '0.0000998'

        self.assertEqual(
            value_string,
            cdl_convert._de_exponent(value)
        )

    #==========================================================================

    def testNegativeExp3(self):
        """Tests a basic negative value"""
        value = -0.0000000003037892378
        value_string = '-0.0000000003037892378'

        self.assertEqual(
            value_string,
            cdl_convert._de_exponent(value)
        )

    #==========================================================================

    def testPositiveExp(self):
        """Tests a basic positive value"""
        value = 76283728313300000000000000000.0
        value_string = '76283728313300000000000000000.0'

        self.assertEqual(
            value_string,
            cdl_convert._de_exponent(value)
        )

    #==========================================================================

    def testPositiveExp2(self):
        """Tests a basic positive value"""
        value = 3217892322310000000000000000000000.0
        value_string = '3217892322310000000000000000000000.0'

        self.assertEqual(
            value_string,
            cdl_convert._de_exponent(value)
        )

    #==========================================================================

    def testPositiveExp3(self):
        """Tests a basic positive value"""
        value = -1628721600000.0
        value_string = '-1628721600000.0'

        self.assertEqual(
            value_string,
            cdl_convert._de_exponent(value)
        )

# _sanitize() =================================================================


class TestSanitize(unittest.TestCase):
    """Tests the helper function _sanitize()"""

    def testSpaces(self):
        """Tests that spaces are replaced with underscores"""
        result = cdl_convert._sanitize('banana apple blueberry')

        self.assertEqual(
            'banana_apple_blueberry',
            result
        )

    #==========================================================================

    def testUnderscoresOkay(self):
        """Tests that underscores pass through intact"""
        result = cdl_convert._sanitize('a_b_c')

        self.assertEqual(
            'a_b_c',
            result
        )

    #==========================================================================

    def testPeriodsOkay(self):
        """Tests that periods pass through intact"""
        result = cdl_convert._sanitize('a.b.c')

        self.assertEqual(
            'a.b.c',
            result
        )

    #==========================================================================

    def testLeadingPeriodRemove(self):
        """Tests that leading periods are removed"""
        result = cdl_convert._sanitize('.abc')

        self.assertEqual(
            'abc',
            result
        )

    #==========================================================================

    def testLeadingUnderscoreRemove(self):
        """Tests that leading underscores are removed"""
        result = cdl_convert._sanitize('_abc')

        self.assertEqual(
            'abc',
            result
        )

    #==========================================================================

    def testCommonBadChars(self):
        """Tests that common bad characters are removed"""
        result = cdl_convert._sanitize('a@$#b!)(*$%&^c`/\\"\';:<>,d')

        self.assertEqual(
            'abcd',
            result
        )

    #==========================================================================

    def testEmptyString(self):
        """Tests that sanitize will return and not choke on empty string"""
        result = cdl_convert._sanitize('')

        self.assertEqual(
            '',
            result
        )

# parse_args() ================================================================


class TestParseArgs(unittest.TestCase):
    """Tests that arguments are being parsed correctly"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.sysargv = sys.argv

    #==========================================================================

    def tearDown(self):
        sys.argv = self.sysargv

    #==========================================================================
    # TESTS
    #==========================================================================

    def testInputPositionalArg(self):
        """Tests that the input arg is positionally gotten correctly"""

        sys.argv = ['scriptname', 'inputFile.txt']

        args = cdl_convert.parse_args()

        self.assertEqual(
            'inputFile.txt',
            args.input_file
        )

    #==========================================================================

    def testGoodInputFormat(self):
        """Tests that a good input format is accepted and lowered"""

        sys.argv = ['scriptname', 'inputFile', '-i', 'ALE']

        args = cdl_convert.parse_args()

        self.assertEqual(
            'ale',
            args.input
        )

    #==========================================================================

    def testBadInputFormat(self):
        """Tests that a bad input format is rejected with ValueError"""

        sys.argv = ['scriptname', 'inputFile', '-i', 'HUYYE']

        self.assertRaises(
            ValueError,
            cdl_convert.parse_args
        )

    #==========================================================================

    def testGoodOutputFormat(self):
        """Tests that a good output format is accepted and lowered"""

        sys.argv = ['scriptname', 'inputFile', '-o', 'CDL']

        args = cdl_convert.parse_args()

        self.assertEqual(
            ['cdl'],
            args.output
        )

    #==========================================================================

    def testMultipleGoodOutputFormat(self):
        """Tests that multiple good output formats are accepted and lowered"""

        sys.argv = ['scriptname', 'inputFile', '-o', 'CDL,CC']

        args = cdl_convert.parse_args()

        self.assertEqual(
            ['cdl', 'cc'],
            args.output
        )

    #==========================================================================

    def testBadOutputFormat(self):
        """Tests that a bad output format is rejected with ValueError"""

        sys.argv = ['scriptname', 'inputFile', '-o', 'HUYYE']

        self.assertRaises(
            ValueError,
            cdl_convert.parse_args
        )

    #==========================================================================

    def testGoodWithBadOutputFormat(self):
        """Tests that a bad output format is rejected with ValueError"""

        sys.argv = ['scriptname', 'inputFile', '-o', 'cc,HUYYE']

        self.assertRaises(
            ValueError,
            cdl_convert.parse_args
        )

    #==========================================================================

    def testNoProvidedOutput(self):
        """Tests that no provided output format is defaulted to cc"""

        sys.argv = ['scriptname', 'inputFile']

        args = cdl_convert.parse_args()

        self.assertEqual(
            ['cc'],
            args.output
        )

# main() ======================================================================


class TestMain(unittest.TestCase):
    """Tests the main() function for correct execution"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Note that the file doesn't really need to exist for our test purposes
        self.cdl = cdl_convert.ColorCorrection(
            id='uniqueId', input_file='../testcdl.flex'
        )
        self.inputFormats = cdl_convert.INPUT_FORMATS
        self.outputFormats = cdl_convert.OUTPUT_FORMATS
        self.sysargv = sys.argv
        self.stdout = sys.stdout
        sys.stdout = StringIO()

    #==========================================================================

    def tearDown(self):
        cdl_convert.INPUT_FORMATS = self.inputFormats
        cdl_convert.OUTPUT_FORMATS = self.outputFormats
        sys.argv = self.sysargv
        sys.stdout = self.stdout
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.ColorCorrection.members = {}

    #==========================================================================
    # TESTS
    #==========================================================================

    @mock.patch('cdl_convert.cdl_convert.parse_flex')
    @mock.patch('os.path.abspath')
    def testGettingAbsolutePath(self, abspath, mockParse):
        """Tests that we make sure to get the absolute path"""

        abspath.return_value = 'file.flex'
        mockParse.return_value = None
        sys.argv = ['scriptname', 'file.flex']

        mockInputs = dict(self.inputFormats)
        mockInputs['flex'] = mockParse
        cdl_convert.INPUT_FORMATS = mockInputs

        cdl_convert.main()

        abspath.assert_called_once_with('file.flex')

    #==========================================================================

    @mock.patch('cdl_convert.cdl_convert.parse_flex')
    @mock.patch('os.path.abspath')
    def testDerivingInputType(self, abspath, mockParse):
        """Tests that input type will be derived from file extension"""

        abspath.return_value = 'file.flex'
        mockParse.return_value = None
        sys.argv = ['scriptname', 'file.flex']

        mockInputs = dict(self.inputFormats)
        mockInputs['flex'] = mockParse
        cdl_convert.INPUT_FORMATS = mockInputs

        cdl_convert.main()

        mockParse.assert_called_once_with('file.flex')

    #==========================================================================

    @mock.patch('cdl_convert.cdl_convert.parse_flex')
    @mock.patch('os.path.abspath')
    def testDerivingInputTypeCased(self, abspath, mockParse):
        """Tests that input type will be derived from file extension"""

        abspath.return_value = 'file.fLEx'
        mockParse.return_value = None
        sys.argv = ['scriptname', 'file.fLEx']

        mockInputs = dict(self.inputFormats)
        mockInputs['flex'] = mockParse
        cdl_convert.INPUT_FORMATS = mockInputs

        cdl_convert.main()

        mockParse.assert_called_once_with('file.fLEx')

    #==========================================================================

    @mock.patch('cdl_convert.cdl_convert.parse_flex')
    @mock.patch('os.path.abspath')
    def testOverrideInputType(self, abspath, mockParse):
        """Tests that overriding the input type happens when provided"""

        abspath.return_value = 'file.cc'
        mockParse.return_value = None
        sys.argv = ['scriptname', 'file.cc', '-i', 'flex']

        mockInputs = dict(self.inputFormats)
        mockInputs['flex'] = mockParse
        cdl_convert.INPUT_FORMATS = mockInputs

        cdl_convert.main()

        mockParse.assert_called_once_with('file.cc')

    #==========================================================================

    @mock.patch('os.path.dirname')
    @mock.patch('cdl_convert.cdl_convert.write_cc')
    @mock.patch('cdl_convert.cdl_convert.parse_flex')
    @mock.patch('os.path.abspath')
    def testDetermineDestCalled(self, abspath, mockParse, mockWrite, dirname):
        """Tests that we try and write a converted file"""

        abspath.return_value = 'file.flex'
        dirname.return_value = ''  # determine_dest method calls to get dirname
        mockParse.return_value = [self.cdl, ]
        sys.argv = ['scriptname', 'file.flex', '-o', 'cc']

        mockInputs = dict(self.inputFormats)
        mockInputs['flex'] = mockParse
        cdl_convert.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs['cc'] = mockWrite
        cdl_convert.OUTPUT_FORMATS = mockOutputs

        cdl_convert.main()

        self.assertEqual(
            'uniqueId.cc',
            self.cdl.file_out
        )


    #==========================================================================

    @mock.patch('cdl_convert.cdl_convert.write_cc')
    @mock.patch('cdl_convert.cdl_convert.parse_flex')
    @mock.patch('os.path.abspath')
    def testWriteCalled(self, abspath, mockParse, mockWrite):
        """Tests that we try and write a converted file"""

        abspath.return_value = 'file.flex'
        mockParse.return_value = [self.cdl, ]
        sys.argv = ['scriptname', 'file.flex', '-o', 'cc']

        mockInputs = dict(self.inputFormats)
        mockInputs['flex'] = mockParse
        cdl_convert.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs['cc'] = mockWrite
        cdl_convert.OUTPUT_FORMATS = mockOutputs

        cdl_convert.main()

        mockWrite.assert_called_once_with(self.cdl)


    #==========================================================================

    @mock.patch('cdl_convert.cdl_convert.write_cdl')
    @mock.patch('cdl_convert.cdl_convert.write_cc')
    @mock.patch('cdl_convert.cdl_convert.parse_flex')
    @mock.patch('os.path.abspath')
    def testMultipleWritesCalled(self, abspath, mockParse, mockWriteCC,
                                 mockWriteCDL):
        """Tests that we try and write a converted file"""

        abspath.return_value = 'file.flex'
        mockParse.return_value = [self.cdl, ]
        sys.argv = ['scriptname', 'file.flex', '-o', 'cc,cdl']

        mockInputs = dict(self.inputFormats)
        mockInputs['flex'] = mockParse
        cdl_convert.INPUT_FORMATS = mockInputs

        mockOutputs = dict(self.outputFormats)
        mockOutputs['cc'] = mockWriteCC
        mockOutputs['cdl'] = mockWriteCDL
        cdl_convert.OUTPUT_FORMATS = mockOutputs

        cdl_convert.main()

        mockWriteCC.assert_called_once_with(self.cdl)
        mockWriteCDL.assert_called_once_with(self.cdl)

# Test Classes ================================================================

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

    #==========================================================================
    # TESTS
    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

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

    #==========================================================================

    def testDurationUnderFiveMinutes(self):
        """Tests that duration when not provided is kept under 5 minutes"""
        tc = TimeCodeSegment(fps=24)

        self.assertTrue(
            tc.durFrames <= 7200
        )

#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
