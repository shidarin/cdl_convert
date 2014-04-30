#!/usr/bin/env python
"""
Tests the classes of cdl_convert

REQUIREMENTS:

mock
"""

#==============================================================================
# IMPORTS
#==============================================================================

# Standard Imports
import os
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
# GLOBALS
#==============================================================================

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

# AscColorSpaceBase ===========================================================


class TestAscColorSpaceBase(unittest.TestCase):
    """Tests the very simple base class which has colorspace attributes"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.AscColorSpaceBase()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testInputDesc(self):
        """Tests that input_desc exists and defaults to none"""

        self.assertTrue(
            hasattr(self.node, 'input_desc')
        )

        self.assertEqual(
            None,
            self.node.input_desc
        )

        self.node.input_desc = 'Sunset with an Eizo'

        self.assertEqual(
            'Sunset with an Eizo',
            self.node.input_desc
        )

    #==========================================================================

    def testViewingDesc(self):
        """Tests that viewing_desc exists and defaults to none"""

        self.assertTrue(
            hasattr(self.node, 'viewing_desc')
        )

        self.assertEqual(
            None,
            self.node.viewing_desc
        )

        self.node.viewing_desc = 'Darker with a tinge of blah'

        self.assertEqual(
            'Darker with a tinge of blah',
            self.node.viewing_desc
        )

# AscDescBase =================================================================


class TestAscDescBase(unittest.TestCase):
    """Tests the very simple base class which has desc attributes"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.AscDescBase()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testInit(self):
        """Tests that on init desc is created and empty"""

        self.assertEqual(
            (),
            self.node.desc
        )

    #==========================================================================

    def testFirstSet(self):
        """Tests setting desc to a string appends it to the list"""

        self.node.desc = 'first description'

        self.assertEqual(
            ('first description', ),
            self.node.desc
        )

    #==========================================================================

    def testAppendAdditional(self):
        """Tests that setting desc more than once appends to list"""

        self.node.desc = 'first description'

        self.assertEqual(
            ('first description', ),
            self.node.desc
        )

        self.node.desc = 'second description'

        self.assertEqual(
            ('first description', 'second description'),
            self.node.desc
        )

    #==========================================================================

    def testExtendWithList(self):
        """Tests extending the desc with another list"""

        # Bypass setter
        self.node._desc = ['first description']

        self.node.desc = ['second description', 'third description']

        self.assertEqual(
            ('first description', 'second description', 'third description'),
            self.node.desc
        )

    #==========================================================================

    def testExtendWithTuple(self):
        """Tests extending the desc with another tuple"""

        # Bypass setter
        self.node._desc = ['first description']

        self.node.desc = ('second description', 'third description')

        self.assertEqual(
            ('first description', 'second description', 'third description'),
            self.node.desc
        )

# ColorNodeBase ===============================================================


class TestColorCollectionBase(unittest.TestCase):
    """Tests the very simple base class ColorCollectionBase"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.ColorCollectionBase()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testInputDesc(self):
        """Tests that input_desc inherited"""

        self.assertTrue(
            hasattr(self.node, 'input_desc')
        )

        self.assertEqual(
            None,
            self.node.input_desc
        )

    #==========================================================================

    def testViewingDesc(self):
        """Tests that viewing_desc inherited"""

        self.assertTrue(
            hasattr(self.node, 'viewing_desc')
        )

        self.assertEqual(
            None,
            self.node.viewing_desc
        )

    #==========================================================================

    def testDesc(self):
        """Tests that desc inherited"""

        self.assertTrue(
            hasattr(self.node, 'desc')
        )

        self.assertEqual(
            (),
            self.node.desc
        )

# ColorCorrection =============================================================


class TestColorCorrection(unittest.TestCase):
    """Tests all aspects of the ColorCorrection class.

    Many of the tests involving Sop and Sat values are obsolete, since those
    values have been moved into their own class. However, the tests will remain
    as they're still an attribute of ColorCorrection

    """

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Note that the file doesn't really need to exist for our test purposes
        self.cdl = cdl_convert.ColorCorrection(
            id='uniqueId', cdl_file='../testcdl.cc'
        )

    def tearDown(self):
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.ColorCorrection.members = {}

    #==========================================================================
    # TESTS
    #==========================================================================

    # Properties & Attributes =================================================

    def testInputDesc(self):
        """Tests that input_desc inherited"""

        self.assertTrue(
            hasattr(self.cdl, 'input_desc')
        )

        self.assertEqual(
            None,
            self.cdl.input_desc
        )

    #==========================================================================

    def testViewingDesc(self):
        """Tests that viewing_desc inherited"""

        self.assertTrue(
            hasattr(self.cdl, 'viewing_desc')
        )

        self.assertEqual(
            None,
            self.cdl.viewing_desc
        )

    #==========================================================================

    def testDesc(self):
        """Tests that desc inherited"""

        self.assertTrue(
            hasattr(self.cdl, 'desc')
        )

        self.assertEqual(
            (),
            self.cdl.desc
        )

    #==========================================================================


    def testFileInReturn(self):
        """Tests that calling ColorCorrection.fileIn returns the file given"""
        self.assertEqual(
            os.path.abspath('../testcdl.cc'),
            self.cdl.file_in
        )

    #==========================================================================

    def testFileInSetException(self):
        """Tests that exception raised when setting file_in after init"""
        def testFileIn():
            self.cdl.file_in = '../NewFile.cc'

        self.assertRaises(
            AttributeError,
            testFileIn
        )

    #==========================================================================

    def testFileOutSetException(self):
        """Tests that exception raised when attempting to set file_out direct"""
        def testFileOut():
            self.cdl.file_out = '../NewFile.cc'

        self.assertRaises(
            AttributeError,
            testFileOut
        )

    #==========================================================================

    def testIdReturn(self):
        """Tests that calling ColorCorrection.id returns the id"""
        self.assertEqual(
            'uniqueId',
            self.cdl.id
        )

    #==========================================================================

    def testIdNonUniqueIdOnInit(self):
        """Tests that exception raised when initializing a non-unique id."""

        self.assertRaises(
            ValueError,
            cdl_convert.ColorCorrection,
            'uniqueId',
            'file'
        )

    #==========================================================================

    def testIdNonUniqueIdOnSet(self):
        """Tests that exception raised when setting a non-unique id."""
        def setId(cdl):
            cdl.id = 'uniqueId'

        new = cdl_convert.ColorCorrection('betterId', 'file')

        self.assertRaises(
            ValueError,
            setId,
            new
        )

    #==========================================================================

    def testIdRenameDictionary(self):
        """Tests that dict entries are removed following a rename"""

        new = cdl_convert.ColorCorrection('betterId', 'file')

        self.assertTrue(
            'betterId' in cdl_convert.ColorCorrection.members.keys()
        )

        new.id = 'betterishId'

        self.assertFalse(
            'betterId' in cdl_convert.ColorCorrection.members.keys()
        )

        self.assertTrue(
            'betterishId' in cdl_convert.ColorCorrection.members.keys()
        )

    #==========================================================================

    def testOffsetSetAndGet(self):
        """Tests setting and getting the offset"""

        offset = (-1.3782, 278.32, 0.738378233782)

        self.cdl.offset = offset

        self.assertEqual(
            offset,
            self.cdl.offset
        )

    #==========================================================================

    def testOffsetBadLength(self):
        """Tests passing offset an incorrect length list"""
        def setOffset():
            self.cdl.offset = ['banana']

        self.assertRaises(
            ValueError,
            setOffset
        )

    #==========================================================================

    def testOffsetSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setOffset():
            self.cdl.offset = [-1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setOffset
        )

    #==========================================================================

    def testOffsetBadType(self):
        """Tests passing offset a correct length but bad type value"""
        def setOffset():
            self.cdl.offset = 'ban'

        self.assertRaises(
            TypeError,
            setOffset
        )

    #==========================================================================

    def testOffsetBecomesTuple(self):
        """Tests offset is converted to tuple from list"""

        offset = [-1.3782, 278.32, 0.738378233782]

        self.cdl.offset = offset

        self.assertEqual(
            tuple(offset),
            self.cdl.offset
        )

    #==========================================================================

    def testPowerSetAndGet(self):
        """Tests setting and getting the power"""

        power = (1.3782, 278.32, 0.738378233782)

        self.cdl.power = power

        self.assertEqual(
            power,
            self.cdl.power
        )

    #==========================================================================

    def testPowerSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setPower():
            self.cdl.power = [-1.3782, 278.32, 0.738378233782]

        self.assertRaises(
            ValueError,
            setPower
        )

    #==========================================================================

    def testPowerSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setPower():
            self.cdl.power = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setPower
        )

    #==========================================================================

    def testPowerBadLength(self):
        """Tests passing power an incorrect length list"""
        def setPower():
            self.cdl.power = ['banana']

        self.assertRaises(
            ValueError,
            setPower
        )

    #==========================================================================

    def testPowerBadType(self):
        """Tests passing power a correct length but bad type value"""
        def setPower():
            self.cdl.power = 'ban'

        self.assertRaises(
            TypeError,
            setPower
        )

    #==========================================================================

    def testPowerBecomesTuple(self):
        """Tests power is converted to tuple from list"""

        power = [1.3782, 278.32, 0.738378233782]

        self.cdl.power = power

        self.assertEqual(
            tuple(power),
            self.cdl.power
        )

    #==========================================================================

    def testSlopeSetAndGet(self):
        """Tests setting and getting the slope"""

        slope = (1.3782, 278.32, 0.738378233782)

        self.cdl.slope = slope

        self.assertEqual(
            slope,
            self.cdl.slope
        )

    #==========================================================================

    def testSlopeSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setSlope():
            self.cdl.slope = [-1.3782, 278.32, 0.738378233782]

        self.assertRaises(
            ValueError,
            setSlope
        )

    #==========================================================================

    def testSlopeSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setSlope():
            self.cdl.slope = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setSlope
        )

    #==========================================================================

    def testSlopeBadLength(self):
        """Tests passing slope an incorrect length list"""
        def setSlope():
            self.cdl.slope = ['banana']

        self.assertRaises(
            ValueError,
            setSlope
        )

    #==========================================================================

    def testSlopeBadType(self):
        """Tests passing slope a correct length but bad type value"""
        def setSlope():
            self.cdl.slope = 'ban'

        self.assertRaises(
            TypeError,
            setSlope
        )

    #==========================================================================

    def testSlopeBecomesTuple(self):
        """Tests slope is converted to tuple from list"""

        slope = [1.3782, 278.32, 0.738378233782]

        self.cdl.slope = slope

        self.assertEqual(
            tuple(slope),
            self.cdl.slope
        )

    #==========================================================================

    def testSatSetAndGet(self):
        """Tests setting and getting saturation"""

        sat = 34.3267

        self.cdl.sat = sat

        self.assertEqual(
            sat,
            self.cdl.sat
        )

    #==========================================================================

    def testSatSetNegative(self):
        """Tests that a ValueError is raised if sat is set to negative"""
        def setSat():
            self.cdl.sat = -376.23

        self.assertRaises(
            ValueError,
            setSat
        )
    #==========================================================================

    def testSatSetString(self):
        """Tests that a TypeError is raised if sat is set to string"""
        def setSat():
            self.cdl.sat = 'banana'

        self.assertRaises(
            TypeError,
            setSat
        )

    #==========================================================================

    def testSatBecomesFloat(self):
        """Tests that saturation is converted to float from int"""
        sat = 3

        self.cdl.sat = sat

        self.assertEqual(
            float(sat),
            self.cdl.sat
        )

    # determine_dest() ========================================================

    def testDetermineDest(self):
        """Tests that determine destination is calculated correctly"""
        self.cdl.determine_dest('cdl')

        dir = os.path.abspath('../')
        filename = os.path.join(dir, 'uniqueId.cdl')

        self.assertEqual(
            filename,
            self.cdl.file_out
        )

# ColorNodeBase ===============================================================


class TestColorNodeBase(unittest.TestCase):
    """Tests the very simple base class ColorNodeBase"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.ColorNodeBase()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testDesc(self):
        """Tests that desc inherited"""

        self.assertTrue(
            hasattr(self.node, 'desc')
        )

        self.assertEqual(
            (),
            self.node.desc
        )


# SatNode =====================================================================


class TestSatNode(unittest.TestCase):
    """Tests all aspects of SatNode"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.SatNode(self)

    #==========================================================================
    # TESTS
    #==========================================================================

    def testDesc(self):
        """Tests that desc inherited"""

        self.assertTrue(
            hasattr(self.node, 'desc')
        )

        self.assertEqual(
            (),
            self.node.desc
        )

    #==========================================================================

    def testParent(self):
        """Tests that parent was attached to us correctly"""
        self.assertEqual(
            self,
            self.node.parent
        )

    #==========================================================================

    def testSetParent(self):
        """Tests that we can't set the parent property after init"""
        def setParent():
            self.node.parent = 'banana'

        self.assertRaises(
            AttributeError,
            setParent
        )

    #==========================================================================

    def testDefault(self):
        """Tests that saturation starts off with a default value of 1.0"""
        self.assertEqual(
            1.0,
            self.node.sat
        )

    #==========================================================================

    def testGetSat(self):
        """Tests that we can get the saturation value"""
        # Bypass setter
        self.node._sat = 12.8

        self.assertEqual(
            12.8,
            self.node.sat,
        )

    #==========================================================================

    def testSetWithString(self):
        """Tests that we can set sat with a single string"""
        self.node.sat = '12.3'

        self.assertEqual(
            12.3,
            self.node.sat
        )

    #==========================================================================

    def testSetWithBadString(self):
        """Tests that we can't set sat with a single bad string"""
        def setSat():
            self.node.sat = 'banana'

        self.assertRaises(
            TypeError,
            setSat
        )

    #==========================================================================

    def testSetWithNegativeString(self):
        """Tests that we can't set sat with a single negative string"""
        def setSat():
            self.node.sat = '-20'

        self.assertRaises(
            ValueError,
            setSat
        )

    #==========================================================================

    def testSetWithFloat(self):
        """Tests that we can set sat with a single float"""
        self.node.sat = 100.1

        self.assertEqual(
            100.1,
            self.node.sat
        )

    #==========================================================================

    def testSetWithNegativeFloat(self):
        """Tests that we can't set sat with a single negative float"""
        def setSat():
            self.node.sat = -20.1

        self.assertRaises(
            ValueError,
            setSat
        )

    #==========================================================================

    def testSetWithInt(self):
        """Tests that we can set sat with a single int"""
        self.node.sat = 2

        self.assertEqual(
            2,
            self.node.sat
        )

    #==========================================================================

    def testSetWithNegativeInt(self):
        """Tests that we can't set sat with a single negative float"""
        def setSat():
            self.node.sat = -20

        self.assertRaises(
            ValueError,
            setSat
        )

    #==========================================================================

    def testSetWithListFails(self):
        """Tests that we can't set sat with a list"""
        def setSat():
            self.node.sat = [-1.1]

        self.assertRaises(
            TypeError,
            setSat
        )

# SopNode =====================================================================


class TestSopNode(unittest.TestCase):
    """Tests all aspects of SopNode"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.SopNode(self)

    #==========================================================================
    # TESTS
    #==========================================================================

    def testDesc(self):
        """Tests that desc inherited"""

        self.assertTrue(
            hasattr(self.node, 'desc')
        )

        self.assertEqual(
            (),
            self.node.desc
        )

    #==========================================================================

    def testParent(self):
        """Tests that parent was attached to us correctly"""
        self.assertEqual(
            self,
            self.node.parent
        )

    #==========================================================================

    def testSetParent(self):
        """Tests that we can't set the parent property after init"""
        def setParent():
            self.node.parent = 'banana'

        self.assertRaises(
            AttributeError,
            setParent
        )

    #==========================================================================

    def testSlopeDefault(self):
        """Tests that slope starts off with a default value of 1.0"""
        self.assertEqual(
            (1.0, 1.0, 1.0),
            self.node.slope
        )

    #==========================================================================

    def testGetSlope(self):
        """Tests that we can get the slope value"""
        # Bypass setter
        self.node._slope = [12.8, 1.2, 1.4]

        self.assertEqual(
            (12.8, 1.2, 1.4),
            self.node.slope,
        )

    #==========================================================================

    def testSetSlopeWithString(self):
        """Tests that we can set slope with a single string"""
        self.node.slope = '12.3'

        self.assertEqual(
            (12.3, 12.3, 12.3),
            self.node.slope
        )

    #==========================================================================

    def testSetSlopeWithBadString(self):
        """Tests that we can't set slope with a single bad string"""
        def setSlope():
            self.node.slope = 'banana'

        self.assertRaises(
            TypeError,
            setSlope
        )

    #==========================================================================

    def testSetSlopeWithNegativeString(self):
        """Tests that we can't set slope with a single negative string"""
        def setSlope():
            self.node.slope = '-20'

        self.assertRaises(
            ValueError,
            setSlope
        )

    #==========================================================================

    def testSetSlopeWithFloat(self):
        """Tests that we can set slope with a single float"""
        self.node.slope = 100.1

        self.assertEqual(
            (100.1, 100.1, 100.1),
            self.node.slope
        )

    #==========================================================================

    def testSetSlopeWithNegativeFloat(self):
        """Tests that we can't set slope with a single negative float"""
        def setSlope():
            self.node.slope = -20.1

        self.assertRaises(
            ValueError,
            setSlope
        )

    #==========================================================================

    def testSetSlopeWithInt(self):
        """Tests that we can set slope with a single int"""
        self.node.slope = 2

        self.assertEqual(
            (2, 2, 2),
            self.node.slope
        )

    #==========================================================================

    def testSetSlopeWithNegativeInt(self):
        """Tests that we can't set slope with a single negative float"""
        def setSlope():
            self.node.slope = -20

        self.assertRaises(
            ValueError,
            setSlope
        )

    #==========================================================================

    def testSlopeSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setSlope():
            self.node.slope = [-1.3782, 278.32, 0.738378233782]

        self.assertRaises(
            ValueError,
            setSlope
        )

    #==========================================================================

    def testSlopeSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setSlope():
            self.node.slope = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setSlope
        )

    #==========================================================================

    def testSlopeFromDict(self):
        """Tests that TypeError raised if given dict"""
        def setSlope():
            self.node.slope = {'r': 1.3782, 'g': 278.32, 'b': 2}

        self.assertRaises(
            TypeError,
            setSlope
        )

    #==========================================================================

    def testSlopeBadLength(self):
        """Tests passing slope an incorrect length list"""
        def setSlope():
            self.node.slope = ['banana']

        self.assertRaises(
            ValueError,
            setSlope
        )

    #==========================================================================

    def testSlopeBecomesTuple(self):
        """Tests slope is converted to tuple from list"""

        slope = [1.3782, 278.32, 0.738378233782]

        self.node.slope = slope

        self.assertEqual(
            tuple(slope),
            self.node.slope
        )

    #==========================================================================

    def testOffsetDefault(self):
        """Tests that offset starts off with a default value of 1.0"""
        self.assertEqual(
            (0.0, 0.0, 0.0),
            self.node.offset
        )

    #==========================================================================

    def testGetOffset(self):
        """Tests that we can get the offset value"""
        # Bypass setter
        self.node._offset = [12.8, 1.2, 1.4]

        self.assertEqual(
            (12.8, 1.2, 1.4),
            self.node.offset,
        )

    #==========================================================================

    def testSetOffsetWithString(self):
        """Tests that we can set offset with a single string"""
        self.node.offset = '12.3'

        self.assertEqual(
            (12.3, 12.3, 12.3),
            self.node.offset
        )

    #==========================================================================

    def testSetOffsetWithBadString(self):
        """Tests that we can't set offset with a single bad string"""
        def setOffset():
            self.node.offset = 'banana'

        self.assertRaises(
            TypeError,
            setOffset
        )

    #==========================================================================

    def testSetOffsetWithNegativeString(self):
        """Tests that we can set offset with a single negative string"""
        self.node.offset = '-20'

        self.assertEqual(
            (-20.0, -20.0, -20.0),
            self.node.offset
        )

    #==========================================================================

    def testSetOffsetWithFloat(self):
        """Tests that we can set offset with a single float"""
        self.node.offset = 100.1

        self.assertEqual(
            (100.1, 100.1, 100.1),
            self.node.offset
        )

    #==========================================================================

    def testSetOffsetWithNegativeFloat(self):
        """Tests that we can set offset with a single negative float"""
        self.node.offset = -20.1

        self.assertEqual(
            (-20.1, -20.1, -20.1),
            self.node.offset
        )

    #==========================================================================

    def testSetOffsetWithInt(self):
        """Tests that we can set offset with a single int"""
        self.node.offset = 2

        self.assertEqual(
            (2, 2, 2),
            self.node.offset
        )

    #==========================================================================

    def testSetOffsetWithNegativeInt(self):
        """Tests that we can set offset with a single negative int"""
        self.node.offset = -20

        self.assertEqual(
            (-20.0, -20.0, -20.0),
            self.node.offset
        )

    #==========================================================================

    def testOffsetSetNegative(self):
        """Tests that offset can be set to negative value"""
        self.node.offset = [-1.3782, 278.32, 0.738378233782]

        self.assertEqual(
            (-1.3782, 278.32, 0.738378233782),
            self.node.offset
        )

    #==========================================================================

    def testOffsetSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setOffset():
            self.node.offset = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setOffset
        )

    #==========================================================================

    def testOffsetFromDict(self):
        """Tests that TypeError raised if given dict"""
        def setOffset():
            self.node.offset = {'r': 1.3782, 'g': 278.32, 'b': 2}

        self.assertRaises(
            TypeError,
            setOffset
        )

    #==========================================================================

    def testOffsetBadLength(self):
        """Tests passing offset an incorrect length list"""
        def setOffset():
            self.node.offset = ['banana']

        self.assertRaises(
            ValueError,
            setOffset
        )

    #==========================================================================

    def testOffsetBecomesTuple(self):
        """Tests offset is converted to tuple from list"""

        offset = [1.3782, 278.32, 0.738378233782]

        self.node.offset = offset

        self.assertEqual(
            tuple(offset),
            self.node.offset
        )

    #==========================================================================

    def testPowerDefault(self):
        """Tests that power starts off with a default value of 1.0"""
        self.assertEqual(
            (1.0, 1.0, 1.0),
            self.node.power
        )

    #==========================================================================

    def testGetPower(self):
        """Tests that we can get the power value"""
        # Bypass setter
        self.node._power = [12.8, 1.2, 1.4]

        self.assertEqual(
            (12.8, 1.2, 1.4),
            self.node.power,
        )

    #==========================================================================

    def testSetPowerWithString(self):
        """Tests that we can set power with a single string"""
        self.node.power = '12.3'

        self.assertEqual(
            (12.3, 12.3, 12.3),
            self.node.power
        )

    #==========================================================================

    def testSetPowerWithBadString(self):
        """Tests that we can't set power with a single bad string"""
        def setPower():
            self.node.power = 'banana'

        self.assertRaises(
            TypeError,
            setPower
        )

    #==========================================================================

    def testSetPowerWithNegativeString(self):
        """Tests that we can't set power with a single negative string"""
        def setPower():
            self.node.power = '-20'

        self.assertRaises(
            ValueError,
            setPower
        )

    #==========================================================================

    def testSetPowerWithFloat(self):
        """Tests that we can set power with a single float"""
        self.node.power = 100.1

        self.assertEqual(
            (100.1, 100.1, 100.1),
            self.node.power
        )

    #==========================================================================

    def testSetPowerWithNegativeFloat(self):
        """Tests that we can't set power with a single negative float"""
        def setPower():
            self.node.power = -20.1

        self.assertRaises(
            ValueError,
            setPower
        )

    #==========================================================================

    def testSetPowerWithInt(self):
        """Tests that we can set power with a single int"""
        self.node.power = 2

        self.assertEqual(
            (2, 2, 2),
            self.node.power
        )

    #==========================================================================

    def testSetPowerWithNegativeInt(self):
        """Tests that we can't set power with a single negative float"""
        def setPower():
            self.node.power = -20

        self.assertRaises(
            ValueError,
            setPower
        )

    #==========================================================================

    def testPowerSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setPower():
            self.node.power = [-1.3782, 278.32, 0.738378233782]

        self.assertRaises(
            ValueError,
            setPower
        )

    #==========================================================================

    def testPowerSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setPower():
            self.node.power = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setPower
        )

    #==========================================================================

    def testPowerFromDict(self):
        """Tests that TypeError raised if given dict"""
        def setPower():
            self.node.power = {'r': 1.3782, 'g': 278.32, 'b': 2}

        self.assertRaises(
            TypeError,
            setPower
        )

    #==========================================================================

    def testPowerBadLength(self):
        """Tests passing power an incorrect length list"""
        def setPower():
            self.node.power = ['banana']

        self.assertRaises(
            ValueError,
            setPower
        )

    #==========================================================================

    def testPowerBecomesTuple(self):
        """Tests power is converted to tuple from list"""

        power = [1.3782, 278.32, 0.738378233782]

        self.node.power = power

        self.assertEqual(
            tuple(power),
            self.node.power
        )

#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
