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
import os
import mock
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
# FUNCTIONS
#===============================================================================

if __name__ == '__main__':
    unittest.main()