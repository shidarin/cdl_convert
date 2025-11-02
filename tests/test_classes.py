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
from decimal import Decimal
from unittest import mock
import os
from pathlib import Path
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

import cdl_convert
from cdl_convert.base import AscColorSpaceBase, AscDescBase
from cdl_convert.correction import ColorNodeBase

#==============================================================================
# GLOBALS
#==============================================================================



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
        self.node = AscColorSpaceBase()

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

    #==========================================================================

    @mock.patch('xml.etree.ElementTree.Element')
    def test_parse_xml_input_desc(self, mock_elem):
        """Tests the input_desc method, which parses an ElementTree element"""

        mock_elem.find.return_value.text = 'Bob'

        self.assertEqual(
            None,
            self.node.input_desc
        )

        self.assertTrue(
            self.node.parse_xml_input_desc(mock_elem)
        )

        self.assertEqual(
            'Bob',
            self.node.input_desc
        )

        mock_elem.find.return_value.text = None

        self.assertTrue(
            self.node.parse_xml_input_desc(mock_elem)
        )

        self.assertEqual(
            None,
            self.node.input_desc
        )

        # Now we'll make the Element.find raise an AttributeError,
        # mocking that the element has no elem with that name.
        mock_elem.find.side_effect = AttributeError('')

        self.node.input_desc = 'Ralph'

        self.assertFalse(
            self.node.parse_xml_input_desc(mock_elem)
        )

        self.assertEqual(
            'Ralph',
            self.node.input_desc
        )

    #==========================================================================

    @mock.patch('xml.etree.ElementTree.Element')
    def test_parse_xml_viewing_desc(self, mock_elem):
        """Tests the viewing_desc method, which parses an ElementTree element"""

        mock_elem.find.return_value.text = 'Bob'

        self.assertEqual(
            None,
            self.node.viewing_desc
        )

        self.assertTrue(
            self.node.parse_xml_viewing_desc(mock_elem)
        )

        self.assertEqual(
            'Bob',
            self.node.viewing_desc
        )

        mock_elem.find.return_value.text = None

        self.assertTrue(
            self.node.parse_xml_viewing_desc(mock_elem)
        )

        self.assertEqual(
            None,
            self.node.viewing_desc
        )

        # Now we'll make the Element.find raise an AttributeError,
        # mocking that the element has no elem with that name.
        mock_elem.find.side_effect = AttributeError('')

        self.node.viewing_desc = 'Ralph'

        self.assertFalse(
            self.node.parse_xml_viewing_desc(mock_elem)
        )

        self.assertEqual(
            'Ralph',
            self.node.viewing_desc
        )

# AscDescBase =================================================================


class TestAscDescBase(unittest.TestCase):
    """Tests the very simple base class which has desc attributes"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = AscDescBase()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testInit(self):
        """Tests that on init desc is created and empty"""

        self.assertEqual(
            [],
            self.node.desc
        )

    #==========================================================================

    def testFirstSet(self):
        """Tests setting desc to a string appends it to the list"""

        self.node.desc = 'first description'

        self.assertEqual(
            ['first description', ],
            self.node.desc
        )

    #==========================================================================

    def testAppendAdditional(self):
        """Tests that setting desc more than once appends to list"""

        self.node.desc = 'first description'

        self.assertEqual(
            ['first description', ],
            self.node.desc
        )

        self.node.desc = 'second description'

        self.assertEqual(
            ['first description', 'second description'],
            self.node.desc
        )

    #==========================================================================

    def testReplaceWithList(self):
        """Tests extending the desc with another list"""

        # Bypass setter
        self.node._desc = ['first description']

        self.node.desc = ['second description', 'third description']

        self.assertEqual(
            ['second description', 'third description'],
            self.node.desc
        )

    #==========================================================================

    def testExtendWithTuple(self):
        """Tests extending the desc with another tuple"""

        # Bypass setter
        self.node._desc = ['first description']

        self.node.desc = ('second description', 'third description')

        self.assertEqual(
            ['second description', 'third description'],
            self.node.desc
        )

    #==========================================================================

    def testClearWithNone(self):
        """Tests that passing desc None will result in a blank list"""

        # Bypass setter
        self.node._desc = ['first description']

        self.node.desc = None

        self.assertEqual(
            [],
            self.node.desc
        )

    #==========================================================================

    def testReplaceWithList(self):
        """Tests replacing desc with a new list"""

        # Bypass setter
        self.node._desc = [
            'first description',
            'second description',
            'third description'
        ]

        self.node.desc = [
            'forth description',
            'fifth description',
            'sixth description'
        ]

        self.assertEqual(
            [
                'forth description',
                'fifth description',
                'sixth description'
            ],
            self.node.desc
        )

    #==========================================================================

    def testReplaceWithTuple(self):
        """Tests replacing desc with a new tuple"""

        # Bypass setter
        self.node._desc = [
            'first description',
            'second description',
            'third description'
        ]

        self.node.desc = (
            'forth description',
            'fifth description',
            'sixth description'
        )

        self.assertEqual(
            [
                'forth description',
                'fifth description',
                'sixth description'
            ],
            self.node.desc
        )

# ColorCollection==============================================================


class TestColorCollection(unittest.TestCase):
    """Tests the simple parameters of ColorCollection"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.ColorCollection()

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
            [],
            self.node.desc
        )

    #==========================================================================

    def testIdList(self):
        """Tests that the id_list behaves correctly"""
        self.assertEqual(
            [],
            self.node.id_list
        )

        self.node.append_child(cdl_convert.ColorCorrection('001'))

        self.assertEqual(
            ['001'],
            self.node.id_list
        )

        self.node.append_child(cdl_convert.ColorCorrection('002'))

        self.assertEqual(
            ['001', '002'],
            self.node.id_list
        )

        cd = cdl_convert.ColorDecision()
        cd.cc = cdl_convert.ColorCorrection('003')

        self.node.append_child(cd)

        self.assertEqual(
            ['001', '002', '003'],
            self.node.id_list
        )

        cd2 = cdl_convert.ColorDecision()
        cd2.cc = cdl_convert.ColorCorrectionRef('004')

        self.node.append_child(cd2)

        self.assertEqual(
            ['001', '002', '003'],  # Unresolved references do not return
            self.node.id_list
        )

        self.node.color_decisions.remove(cd)

        self.assertEqual(
            ['001', '002'],
            self.node.id_list
        )

    #==========================================================================

    def testIsCCC(self):
        """Tests that is_ccc works correctly"""
        self.assertTrue(
            self.node.is_ccc
        )

        self.node._type = 'cdl'

        self.assertFalse(
            self.node.is_ccc
        )

    #==========================================================================

    def testIsCDL(self):
        """Tests that is_cdl works correctly"""
        self.assertFalse(
            self.node.is_cdl
        )

        self.node._type = 'cdl'

        self.assertTrue(
            self.node.is_cdl
        )

    #==========================================================================

    def testType(self):
        """Tests that type protects and accesses the _type attribute"""
        def setType():
            self.node.type = 'banana'

        self.assertRaises(
            ValueError,
            setType
        )

        self.assertEqual(
            'ccc',
            self.node.type
        )

        self.node._type = 'cdl'

        self.assertEqual(
            'cdl',
            self.node.type
        )

        self.node.type = 'ccc'

        self.assertEqual(
            'ccc',
            self.node.type
        )

    #==========================================================================

    def testXmlns(self):
        """Tests the XML specificiation attribute"""
        def setXML():
            self.node.xmlns = 'banana'

        self.assertRaises(
            AttributeError,
            setXML
        )

        self.assertEqual(
            "urn:ASC:CDL:v1.01",
            self.node.xmlns
        )

    #==========================================================================

    def testSetToCCC(self):
        """Tests the set to CCC method"""
        self.node._type = 'cdl'

        self.node.set_to_ccc()

        self.assertEqual(
            'ccc',
            self.node._type
        )

    #==========================================================================

    def testSetToCDL(self):
        """Tests the set to CDL method"""
        self.node._type = 'ccc'

        self.node.set_to_cdl()

        self.assertEqual(
            'cdl',
            self.node._type
        )

    #==========================================================================

    def testFileInRead(self):
        """Tests that file in returns the resolved path"""
        self.node = cdl_convert.ColorCollection(input_file='mybestfile.ccc')

        # Should return the resolved absolute path
        expected_path = Path('mybestfile.ccc').resolve()
        self.assertEqual(
            expected_path,
            self.node.file_in
        )

    #==========================================================================

    def testFileInRead(self):
        """Tests that file in returns the resolved path"""
        self.assertEqual(
            None,
            self.node.file_in
        )

        self.node.file_in = 'mybestfile.ccc'

        # Should return the resolved absolute path
        expected_path = Path('mybestfile.ccc').resolve()
        self.assertEqual(
            expected_path,
            self.node.file_in
        )

    #==========================================================================

    def testFileOutSetException(self):
        """Tests that exception raised when attempting to set file_out direct"""
        def testFileOut():
            self.node.file_out = '../NewFile.ccc'

        self.assertRaises(
            AttributeError,
            testFileOut
        )

    #==========================================================================

    @mock.patch('cdl_convert.parse.parse_cc')
    def testParseXMLColorCorrectionsMultiFound(self, mock_parse):
        """Tests that the method returns True when CCs are found"""

        xml_element = mock.MagicMock()
        xml_element.findall.return_value = ['banana', 'apple', 'egg']

        mock_cdl = mock.MagicMock()
        mock_parse.return_value = mock_cdl

        self.assertTrue(
            self.node.parse_xml_color_corrections(xml_element)
        )

        mock_parse.assert_has_calls(
            [
                mock.call('banana'),
                mock.call('apple'),
                mock.call('egg')
            ]
        )

        self.assertEqual(
            self.node,
            mock_cdl.parent
        )

        # Tests that the returned mock_cdls were added to the color_corrections
        # list.
        self.assertEqual(
            [mock_cdl, mock_cdl, mock_cdl],
            self.node.color_corrections
        )

    #==========================================================================

    def testParseXMLColorCorrectionsNoneFound(self):
        """Tests that the method returns True when CCs are found"""

        xml_element = mock.MagicMock()
        xml_element.findall.return_value = []

        self.assertFalse(
            self.node.parse_xml_color_corrections(xml_element)
        )


    #==========================================================================

    def testDetermineDest(self):
        """Tests that determine destination is calculated correctly"""
        self.node = cdl_convert.ColorCollection(input_file='mybestfile.ccc')
        self.node.type = 'cdl'

        self.node.determine_dest('./converted/')

        # The file_out should be based on the resolved input file path
        expected_stem = Path('mybestfile.ccc').resolve().stem
        expected_out = Path(f'converted/{expected_stem}.cdl')
        self.assertEqual(
            expected_out,
            self.node.file_out
        )

    #==========================================================================

    def testDetermineDestNoFileIn(self):
        """Tests determine destination works with no file_in"""
        # Reset the members list
        cdl_convert.ColorCollection.reset_members()

        # Create a few Collections
        cdl_convert.ColorCollection()
        cdl_convert.ColorCollection()
        cdl_convert.ColorCollection()

        # The 4th one will be the one we use
        self.node = cdl_convert.ColorCollection()

        # But we'll create a 5th.
        cdl_convert.ColorCollection()

        self.node.type = 'ccc'

        self.node.determine_dest('./converted/')

        self.assertEqual(
            Path('converted/color_collection_003.ccc'),
            self.node.file_out
        )


class TestCollectionChildMethods(unittest.TestCase):
    """Tests the children methods and attributes of ColorCollection"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.ColorCollection()

        # We need lists of color corrections and decisions
        self.color_corrections = [
            cdl_convert.ColorCorrection(id='001'),
            cdl_convert.ColorCorrection(id='002'),
            cdl_convert.ColorCorrection(id='003'),
            cdl_convert.ColorCorrection(id='004')
        ]
        self.color_decisions = [
            cdl_convert.ColorDecision(cdl_convert.ColorCorrection(id='005')),
            cdl_convert.ColorDecision(cdl_convert.ColorCorrection(id='006')),
            cdl_convert.ColorDecision(
                cdl_convert.ColorCorrectionRef('005')
            ),
        ]

    def tearDown(self):
        # Empty out the members dictionary
        cdl_convert.reset_all()
        cdl_convert.config.config.halt_on_error = False

    #==========================================================================
    # TESTS
    #==========================================================================

    def testRetrieveColorCorrections(self):
        """Tests the color_corrections attribute"""
        self.node._color_corrections = self.color_corrections
        self.node._color_decisions = self.color_decisions

        self.assertEqual(
            self.color_corrections,
            self.node.color_corrections
        )

    #==========================================================================

    def testRetrieveColorDecisions(self):
        """Tests retrieving the color_decisions attribute"""
        self.node._color_corrections = self.color_corrections
        self.node._color_decisions = self.color_decisions

        self.assertEqual(
            self.color_decisions,
            self.node.color_decisions
        )

    #==========================================================================

    def testRetrieveAllChildren(self):
        """Tests retrieving all the children of a collection node"""
        self.node._color_corrections = self.color_corrections
        self.node._color_decisions = self.color_decisions

        # We add color_corrections to the list before color_decisions, so that
        # list is first.
        self.assertEqual(
            self.color_corrections + self.color_decisions,
            self.node.all_children
        )

    #==========================================================================

    def testAppendChildCorrection(self):
        """Tests that append child works for Corrections"""
        self.node.append_child(self.color_corrections[0])

        self.assertEqual(
            [self.color_corrections[0]],
            self.node.color_corrections
        )

    #==========================================================================

    def testAppendChildDecision(self):
        """Tests that append child works for Decisions"""
        self.node.append_child(self.color_decisions[0])

        self.assertEqual(
            [self.color_decisions[0]],
            self.node.color_decisions
        )

    #==========================================================================

    def testAppendChildBadType(self):
        """Tries appending a child to Collection that's not the right type"""
        self.assertRaises(
            TypeError,
            self.node.append_child,
            'I ama a banana'
        )

    #==========================================================================

    def testAppendDuplicateCorrection(self):
        """Tests appending a ColorCorrection that's already been appended"""
        def append():
            self.node.append_child(self.color_corrections[0])

        append()

        self.assertEqual(
            [self.color_corrections[0]],
            self.node.color_corrections
        )

        append()

        self.assertEqual(
            [self.color_corrections[0]],
            self.node.color_corrections
        )

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            append
        )

    #==========================================================================

    def testAppendDuplicateDecision(self):
        """Tests appending a ColorCorrection that's already been appended"""
        def append():
            self.node.append_child(self.color_decisions[0])

        append()

        self.assertEqual(
            [self.color_decisions[0]],
            self.node.color_decisions
        )

        append()

        self.assertEqual(
            [self.color_decisions[0]],
            self.node.color_decisions
        )

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            append
        )

    #==========================================================================

    def testAppendDuplicateMixed(self):
        """Tests appending a duplicate id with mixed objects"""
        def append():
            self.node.append_child(self.color_corrections[0])

        cd = cdl_convert.ColorDecision(self.color_corrections[0])

        append()

        self.assertEqual(
            [self.color_corrections[0]],
            self.node.color_corrections
        )

        self.assertFalse(
            self.node.append_child(cd)
        )

        self.assertEqual(
            [self.color_corrections[0]],
            self.node.all_children
        )

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            self.node.append_child,
            cd
        )

    #==========================================================================

    def testAppendChildren(self):
        """Tries appending multiple children of different types"""
        self.node.append_children(
            self.color_corrections + self.color_decisions
        )

        self.assertEqual(
            self.color_corrections,
            self.node.color_corrections
        )

        self.assertEqual(
            self.color_decisions,
            self.node.color_decisions
        )

    #==========================================================================

    def testSetColorCorrectionsNone(self):
        """Tries setting the color_corrections attribute with None"""
        self.node.color_corrections = None

        self.assertEqual(
            [],
            self.node.color_corrections
        )

    #==========================================================================

    def testSetColorCorrectionList(self):
        """Tests setting ColorCorrection directly with a list"""
        self.node.color_corrections = self.color_corrections

        # We need to convert self.color_corrections to a set then to a list
        # so the order matches
        self.assertEqual(
            list(set(self.color_corrections)),
            self.node.color_corrections
        )

    #==========================================================================

    def testSetColorCorrectionTuple(self):
        """Tests setting ColorCorrection directly with a tuple"""
        self.node.color_corrections = tuple(self.color_corrections)

        # We need to convert self.color_corrections to a set then to a list
        # so the order matches
        self.assertEqual(
            list(set(self.color_corrections)),
            self.node.color_corrections
        )

    #==========================================================================

    def testSetColorCorrectionSet(self):
        """Tests setting ColorCorrection directly with a list"""
        self.node.color_corrections = self.color_corrections

        # We need to convert self.color_corrections to a set then to a list
        # so the order matches
        self.assertEqual(
            list(set(self.color_corrections)),
            self.node.color_corrections
        )
    #==========================================================================

    def testSetColorCorrectionSingle(self):
        """Tests setting ColorCorrection with a single elem"""
        self.node.color_corrections = self.color_corrections[0]

        self.assertEqual(
            [self.color_corrections[0]],
            self.node.color_corrections
        )

    #==========================================================================

    def testSetColorCorrectonBadType(self):
        """Tests trying to set color correction with a bad type"""
        def setNode():
            self.node.color_corrections = 'Banana'

        self.assertRaises(
            TypeError,
            setNode
        )

    #==========================================================================

    def testSetColorCorrectionListBad(self):
        """Tests having a bad type in a list we're attempting to set with"""
        def setNode():
            self.node.color_corrections = [
                self.color_corrections[0],
                'banana'
            ]

        self.assertRaises(
            TypeError,
            setNode
        )

        self.assertEqual(
            [],
            self.node.color_corrections
        )

    #==========================================================================

    def testSetColorDecisionsNone(self):
        """Tries setting the color_decisions attribute with None"""
        self.node.color_decisions = None

        self.assertEqual(
            [],
            self.node.color_decisions
        )

    #==========================================================================

    def testSetColorDecisionList(self):
        """Tests setting ColorDecision directly with a list"""
        self.node.color_decisions = self.color_decisions

        # We need to convert self.color_decisions to a set then to a list
        # so the order matches
        self.assertEqual(
            list(set(self.color_decisions)),
            self.node.color_decisions
        )

    #==========================================================================

    def testSetColorDecisionTuple(self):
        """Tests setting ColorDecision directly with a tuple"""
        self.node.color_decisions = tuple(self.color_decisions)

        # We need to convert self.color_decisions to a set then to a list
        # so the order matches
        self.assertEqual(
            list(set(self.color_decisions)),
            self.node.color_decisions
        )

    #==========================================================================

    def testSetColorDecisionSet(self):
        """Tests setting ColorDecision directly with a list"""
        self.node.color_decisions = self.color_decisions

        # We need to convert self.color_decisions to a set then to a list
        # so the order matches
        self.assertEqual(
            list(set(self.color_decisions)),
            self.node.color_decisions
        )
    #==========================================================================

    def testSetColorDecisionSingle(self):
        """Tests setting ColorDecision with a single elem"""
        self.node.color_decisions = self.color_decisions[0]

        self.assertEqual(
            [self.color_decisions[0]],
            self.node.color_decisions
        )

    #==========================================================================

    def testSetColorCorrectonBadType(self):
        """Tests trying to set color decision with a bad type"""
        def setNode():
            self.node.color_decisions = 'Banana'

        self.assertRaises(
            TypeError,
            setNode
        )

    #==========================================================================

    def testSetColorDecisionListBad(self):
        """Tests having a bad type in a list and attempting to set"""
        def setNode():
            self.node.color_decisions = [
                self.color_decisions[0],
                'banana'
            ]

        self.assertRaises(
            TypeError,
            setNode
        )

        self.assertEqual(
            [],
            self.node.color_decisions
        )

    #==========================================================================

    def testSetParent(self):
        """Tests setting the parent of all children to an instance"""
        for child in self.color_corrections + self.color_decisions:
            self.assertEqual(
                None,
                child.parent
            )

        self.node.append_children(
            self.color_corrections + self.color_decisions
        )

        for child in self.node.all_children:
            self.assertEqual(
                self.node,
                child.parent
            )
            child.parent = 'banana'
            self.assertEqual(
                'banana',
                child.parent
            )

        self.node.set_parentage()

        for child in self.node.all_children:
            self.assertEqual(
                self.node,
                child.parent
            )


class TestMultipleCollections(unittest.TestCase):
    """Tests the children methods and attributes of ColorCollection"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = cdl_convert.ColorCollection()
        self.node2 = cdl_convert.ColorCollection()

        self.node.type = 'ccc'
        self.node2.type = 'cdl'

        self.node.desc = [
            'When Babies Attack Test DI',
            'Do not use for final',
            'Color by Zap Brannigan',
        ]
        self.node2.desc = [
            'Animals shot with a fisheye lens',
            'cute fluffy animals',
            'watch for blown out highlights',
            'Color by Zap Brannigan',
        ]

        self.node.input_desc = 'LogC to sRGB'
        self.node2.input_desc = 'Cineon Log'

        self.node.viewing_desc = 'DaVinci Resolve on Eizo'
        self.node2.viewing_desc = 'Panasonic Plasma rec709'

        # We need lists of color corrections and decisions
        self.color_corrections = [
            cdl_convert.ColorCorrection(id='001'),
            cdl_convert.ColorCorrection(id='002'),
            cdl_convert.ColorCorrection(id='003'),
            cdl_convert.ColorCorrection(id='004')
        ]
        self.color_decisions = [
            cdl_convert.ColorDecision(cdl_convert.ColorCorrection(id='005')),
            cdl_convert.ColorDecision(cdl_convert.ColorCorrection(id='006')),
            cdl_convert.ColorDecision(
                cdl_convert.ColorCorrectionRef('005')
            ),
        ]

    def tearDown(self):
        # Empty out the members dictionary
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testCopyCollection(self):
        """Tests copying a collection"""
        copy = self.node.copy_collection()

        self.assertEqual(
            self.node.type,
            copy.type
        )

        self.assertEqual(
            self.node.desc,
            copy.desc
        )

        self.assertEqual(
            self.node.input_desc,
            copy.input_desc
        )

        self.assertEqual(
            self.node.viewing_desc,
            copy.viewing_desc
        )

        self.assertEqual(
            self.node.all_children,
            copy.all_children
        )

    #==========================================================================

    def testMergeCollectionsCCCParent(self):
        """Merges collections with a CCC as parent"""
        merged = self.node.merge_collections([self.node2])

        self.assertEqual(
            self.node.desc + self.node2.desc,
            merged.desc
        )
        self.assertEqual(
            self.node.input_desc,
            merged.input_desc
        )
        self.assertEqual(
            self.node.viewing_desc,
            merged.viewing_desc
        )
        self.assertCountEqual(
            self.node.all_children + self.node2.all_children,
            merged.all_children)
        self.assertEqual(
            self.node.type,
            merged.type
        )

    #==========================================================================

    def testMergeCollectionsCCCParentWithDuplicates(self):
        """Merges collections with a CCC as parent and duplicates"""
        # Now we have the same color decisions in both node and node2
        self.node.color_decisions = self.node2.color_decisions

        merged = self.node.merge_collections([self.node2])

        self.assertEqual(
            self.node.desc + self.node2.desc,
            merged.desc
        )
        self.assertEqual(
            self.node.input_desc,
            merged.input_desc
        )
        self.assertEqual(
            self.node.viewing_desc,
            merged.viewing_desc
        )
        # We'll just check the length
        self.assertEqual(
            len(set(self.node.all_children + self.node2.all_children)),
            len(merged.all_children)
        )
        self.assertEqual(
            self.node.type,
            merged.type
        )

    #==========================================================================

    def testMergeCollectionsCCCParentIncludeSelf(self):
        """Merges collections with a CCC as parent and includes self"""
        merged = self.node.merge_collections([self.node2, self.node])

        self.assertEqual(
            self.node.desc + self.node2.desc,
            merged.desc
        )
        self.assertEqual(
            self.node.input_desc,
            merged.input_desc
        )
        self.assertEqual(
            self.node.viewing_desc,
            merged.viewing_desc
        )
        self.assertCountEqual(
            self.node.all_children + self.node2.all_children,
            merged.all_children)
        self.assertEqual(
            self.node.type,
            merged.type
        )

    #==========================================================================

    def testMergeCollectionsCDLParent(self):
        """Merges collections with a CDL as parent"""
        merged = self.node2.merge_collections([self.node])

        self.assertEqual(
            self.node2.desc + self.node.desc,
            merged.desc
        )
        self.assertEqual(
            self.node2.input_desc,
            merged.input_desc
        )
        self.assertEqual(
            self.node2.viewing_desc,
            merged.viewing_desc
        )
        self.assertCountEqual(
            self.node.all_children + self.node2.all_children,
            merged.all_children)
        self.assertEqual(
            self.node2.type,
            merged.type
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
        self.cc = cdl_convert.ColorCorrection(
            id='uniqueId', input_file='../testcdl.cc'
        )

    def tearDown(self):
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    # Properties & Attributes =================================================

    def testInputDesc(self):
        """Tests that input_desc inherited"""

        self.assertTrue(
            hasattr(self.cc, 'input_desc')
        )

        self.assertEqual(
            None,
            self.cc.input_desc
        )

    #==========================================================================

    def testViewingDesc(self):
        """Tests that viewing_desc inherited"""

        self.assertTrue(
            hasattr(self.cc, 'viewing_desc')
        )

        self.assertEqual(
            None,
            self.cc.viewing_desc
        )

    #==========================================================================

    def testDesc(self):
        """Tests that desc inherited"""

        self.assertTrue(
            hasattr(self.cc, 'desc')
        )

        self.assertEqual(
            [],
            self.cc.desc
        )

    #==========================================================================

    def testFileInReturn(self):
        """Tests that calling ColorCorrection.fileIn returns the file given"""
        self.assertEqual(
            Path('../testcdl.cc').resolve(),
            self.cc.file_in
        )

    #==========================================================================

    def testFileOutSetException(self):
        """Tests that exception raised when attempting to set file_out direct"""
        def testFileOut():
            self.cc.file_out = '../NewFile.cc'

        self.assertRaises(
            AttributeError,
            testFileOut
        )

    #==========================================================================

    def testIdReturn(self):
        """Tests that calling ColorCorrection.id returns the id"""
        self.assertEqual(
            'uniqueId',
            self.cc.id
        )

    #==========================================================================

    def testIdNonUniqueIdOnInit(self):
        """Tests that exception raised when initializing a non-unique id."""

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            cdl_convert.ColorCorrection,
            'uniqueId',
            'file'
        )

        cdl_convert.config.config.halt_on_error = False

        try:
            cc = cdl_convert.ColorCorrection('uniqueId', 'file')
        except ValueError:
            self.fail("Non-unique ID was not accepted!")

        self.assertEqual(
            'uniqueId001',
            cc.id
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

    def testBlankId(self):
        """Tests what happens when a blank id is given to CC"""
        cdl_convert.reset_all()

        cdl1 = cdl_convert.ColorCorrection('', 'file')

        self.assertEqual(
            '001',
            cdl1.id
        )

        cdl2 = cdl_convert.ColorCorrection('', 'file')

        self.assertEqual(
            '002',
            cdl2.id
        )

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            cdl_convert.ColorCorrection,
            '',
            'file'
        )

        cdl_convert.config.config.halt_on_error = False

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

    def testHasSat(self):
        """Tests the has_sat attribute"""
        # Verify that with the blank cc, we start with no sat node
        self.assertFalse(
            self.cc.has_sat
        )

        # But if we make a reference to the sat node, it'll create one.
        self.cc.sat_node

        self.assertTrue(
            self.cc.has_sat
        )

    #==========================================================================

    def testHasSop(self):
        """Tests the has_sop attribute"""
        # Verify that with a blank cc, we start with no sop node
        self.assertFalse(
            self.cc.has_sop
        )

        # But if we make a reference to the sop node, it'll create one.
        self.cc.sop_node

        self.assertTrue(
            self.cc.has_sop
        )

    #==========================================================================

    def testOffsetSetAndGet(self):
        """Tests setting and getting the offset"""

        offset = (-1.3782, 278.32, 0.738378233782)
        offsetD = tuple([Decimal(str(i)) for i in offset])

        self.cc.offset = offset

        self.assertEqual(
            offsetD,
            self.cc.offset
        )

    #==========================================================================

    def testOffsetBadLength(self):
        """Tests passing offset an incorrect length list"""
        def setOffset():
            self.cc.offset = ['banana']

        self.assertRaises(
            ValueError,
            setOffset
        )

    #==========================================================================

    def testOffsetSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setOffset():
            self.cc.offset = [-1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setOffset
        )

    #==========================================================================

    def testOffsetBadType(self):
        """Tests passing offset a correct length but bad type value"""
        def setOffset():
            self.cc.offset = 'ban'

        self.assertRaises(
            TypeError,
            setOffset
        )

    #==========================================================================

    def testOffsetBecomesTuple(self):
        """Tests offset is converted to tuple from list"""

        offset = [Decimal('-1.3782'), Decimal('278.32'), Decimal('0.738378233782')]

        self.cc.offset = offset

        self.assertEqual(
            tuple(offset),
            self.cc.offset
        )

    #==========================================================================

    def testPowerSetAndGet(self):
        """Tests setting and getting the power"""

        power = (1.3782, 278.32, 0.738378233782)
        powerD = tuple([Decimal(str(i)) for i in power])

        self.cc.power = power

        self.assertEqual(
            powerD,
            self.cc.power
        )

    #==========================================================================

    def testPowerSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setPower():
            self.cc.power = [-1.3782, 278.32, 0.738378233782]

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setPower
        )

        cdl_convert.config.config.halt_on_error = False

        setPower()

        self.assertEqual(
            (Decimal('0.0'), Decimal('278.32'), Decimal('0.738378233782')),
            self.cc.power
        )

    #==========================================================================

    def testPowerSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setPower():
            self.cc.power = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setPower
        )

    #==========================================================================

    def testPowerBadLength(self):
        """Tests passing power an incorrect length list"""
        def setPower():
            self.cc.power = ['banana']

        self.assertRaises(
            ValueError,
            setPower
        )

    #==========================================================================

    def testPowerBadType(self):
        """Tests passing power a correct length but bad type value"""
        def setPower():
            self.cc.power = 'ban'

        self.assertRaises(
            TypeError,
            setPower
        )

    #==========================================================================

    def testPowerBecomesTuple(self):
        """Tests power is converted to tuple from list"""

        power = [Decimal('1.3782'), Decimal('278.32'), Decimal('0.738378233782')]

        self.cc.power = power

        self.assertEqual(
            tuple(power),
            self.cc.power
        )

    #==========================================================================

    def testSlopeSetAndGet(self):
        """Tests setting and getting the slope"""

        slope = (1.3782, 278.32, 0.738378233782)
        slopeD = tuple([Decimal(str(i)) for i in slope])

        self.cc.slope = slope

        self.assertEqual(
            slopeD,
            self.cc.slope
        )

    #==========================================================================

    def testSlopeSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setSlope():
            self.cc.slope = [-1.3782, 278.32, 0.738378233782]

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSlope
        )

        cdl_convert.config.config.halt_on_error = False

        setSlope()

        self.assertEqual(
            (Decimal('0.0'), Decimal('278.32'), Decimal('0.738378233782')),
            self.cc.slope
        )

    #==========================================================================

    def testSlopeSetStrings(self):
        """Tests that TypeError raised if given strings"""
        def setSlope():
            self.cc.slope = [1.3782, 278.32, 'banana']

        self.assertRaises(
            TypeError,
            setSlope
        )

    #==========================================================================

    def testSlopeBadLength(self):
        """Tests passing slope an incorrect length list"""
        def setSlope():
            self.cc.slope = ['banana']

        self.assertRaises(
            ValueError,
            setSlope
        )

    #==========================================================================

    def testSlopeBadType(self):
        """Tests passing slope a correct length but bad type value"""
        def setSlope():
            self.cc.slope = 'ban'

        self.assertRaises(
            TypeError,
            setSlope
        )

    #==========================================================================

    def testSlopeBecomesTuple(self):
        """Tests slope is converted to tuple from list"""

        slope = [Decimal('1.3782'), Decimal('278.32'), Decimal('0.738378233782')]

        self.cc.slope = slope

        self.assertEqual(
            tuple(slope),
            self.cc.slope
        )

    #==========================================================================

    def testSatSetAndGet(self):
        """Tests setting and getting saturation"""

        sat = 34.3267
        satD = Decimal(str(sat))

        self.cc.sat = sat

        self.assertEqual(
            satD,
            self.cc.sat
        )

    #==========================================================================

    def testSatSetNegative(self):
        """Tests that a ValueError is raised if sat is set to negative"""
        def setSat():
            self.cc.sat = -376.23

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSat
        )

        cdl_convert.config.config.halt_on_error = False

        setSat()

        self.assertEqual(
            Decimal('0.0'),
            self.cc.sat
        )

    #==========================================================================

    def testSatSetString(self):
        """Tests that a TypeError is raised if sat is set to string"""
        def setSat():
            self.cc.sat = 'banana'

        self.assertRaises(
            TypeError,
            setSat
        )

    #==========================================================================

    def testSatBecomesDecimal(self):
        """Tests that saturation is converted to Decimal from int"""
        sat = 3

        self.cc.sat = sat

        self.assertEqual(
            Decimal(sat),
            self.cc.sat
        )

    # determine_dest() ========================================================

    def testDetermineDest(self):
        """Tests that determine destination is calculated correctly"""
        self.cc.determine_dest('cdl', '/bobsBestDirectory')

        expected_path = Path('/bobsBestDirectory') / 'uniqueId.cdl'

        self.assertEqual(
            expected_path,
            self.cc.file_out
        )

# ColorCorrectionRef ====================================================


class TestColorCorrectionReference(unittest.TestCase):
    """Tests the ColorCorrectionRef class"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Note that the file doesn't really need to exist for our test purposes
        self.cc = cdl_convert.ColorCorrection(
            id='uniqueId', input_file='../testcdl.cc'
        )

        self.ccr = cdl_convert.ColorCorrectionRef(id='uniqueId')
        self.ccr_bad = cdl_convert.ColorCorrectionRef(id='oldId')

    def tearDown(self):
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()
        cdl_convert.config.config.halt_on_error = False

    #==========================================================================
    # TESTS
    #==========================================================================

    def testCC(self):
        """Tests that a CC is returned correctly"""
        self.assertEqual(
            self.cc,
            self.ccr.cc
        )

        self.assertEqual(
            None,
            self.ccr_bad.cc
        )

    #==========================================================================

    def testCCHalt(self):
        """Tests trying to get a CC reference with Halt set"""
        cdl_convert.config.config.halt_on_error = True

        def getCC():
            self.ccr_bad.cc

        self.assertRaises(
            ValueError,
            getCC
        )

    #==========================================================================

    def testRef(self):
        """Tests that id is returned correctly"""
        self.assertEqual(
            'uniqueId',
            self.ccr.id
        )

        self.assertEqual(
            'oldId',
            self.ccr_bad.id
        )

    #==========================================================================

    def testMembers(self):
        """Tests that the member's dictionary looks like it should"""
        self.assertEqual(
            {'uniqueId': [self.ccr], 'oldId': [self.ccr_bad]},
            cdl_convert.ColorCorrectionRef.members
        )

    #==========================================================================

    def testChangeRef(self):
        """Tests changing a reference id"""
        self.ccr.id = 'blahblahblah'

        self.assertEqual(
            {'blahblahblah': [self.ccr], 'oldId': [self.ccr_bad]},
            cdl_convert.ColorCorrectionRef.members
        )

    #==========================================================================

    def testChangeRefAppend(self):
        """Tests changing a reference id"""
        self.ccr.id = 'oldId'

        self.assertEqual(
            {'oldId': [self.ccr_bad, self.ccr]},
            cdl_convert.ColorCorrectionRef.members
        )

    #==========================================================================

    def testChangeRefHALT(self):
        """Tests changing a reference id if halt on error true"""
        def setRef():
            self.ccr.id = 'blahblahblah'

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setRef
        )

        self.assertEqual(
            'uniqueId',
            self.ccr.id
        )

        self.assertEqual(
            {'uniqueId': [self.ccr], 'oldId': [self.ccr_bad]},
            cdl_convert.ColorCorrectionRef.members
        )

    #==========================================================================

    def testBuildElement(self):
        """Tests that build element works correctly"""
        self.assertEqual(
            '<ColorCorrectionRef ref="uniqueId"/>\n',
            self.ccr.xml
        )

    #==========================================================================

    def testResetMembers(self):
        """Tests resetting the member dict"""
        cdl_convert.ColorCorrectionRef.reset_members()

        self.assertEqual(
            {},
            cdl_convert.ColorCorrectionRef.members
        )

# ColorDecision ===============================================================


class TestColorDecision(unittest.TestCase):
    """Tests all aspects of the ColorCorrection class."""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Note that the file doesn't really need to exist for our test purposes
        self.cc = cdl_convert.ColorCorrection(
            id='uniqueId', input_file='../testcdl.cc'
        )
        self.media_ref = cdl_convert.MediaRef('/best/url/ever/me.jpg')
        self.cd = cdl_convert.ColorDecision(self.cc, self.media_ref)

    def tearDown(self):
        # We need to clear the ColorCorrection member dictionary so we don't
        # have to worry about non-unique ids.
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testInputDesc(self):
        """Tests that input_desc inherited"""

        self.assertTrue(
            hasattr(self.cd, 'input_desc')
        )

        self.assertEqual(
            None,
            self.cd.input_desc
        )

    #==========================================================================

    def testViewingDesc(self):
        """Tests that viewing_desc inherited"""

        self.assertTrue(
            hasattr(self.cd, 'viewing_desc')
        )

        self.assertEqual(
            None,
            self.cc.viewing_desc
        )

    #==========================================================================

    def testDesc(self):
        """Tests that desc inherited"""

        self.assertTrue(
            hasattr(self.cd, 'desc')
        )

        self.assertEqual(
            [],
            self.cc.desc
        )

    #==========================================================================

    def testParentage(self):
        """Tests that our children were parented to our cd during init"""
        self.assertEqual(
            self.cd,
            self.media_ref.parent
        )

        self.assertEqual(
            self.cd,
            self.cc.parent
        )

    #==========================================================================

    def testParentageChange(self):
        """Tests that changing our cc or media_ref changes their parents"""
        cc2 = cdl_convert.ColorCorrectionRef('001')
        cc2.parent = 'bob'
        mr2 = cdl_convert.MediaRef('sdhjd.dpx')
        mr2.parent = 'jim'

        self.cd.cc = cc2
        self.cd.media_ref = mr2

        self.assertEqual(
            self.cd,
            cc2.parent
        )

        self.assertEqual(
            self.cd,
            mr2.parent
        )

    #==========================================================================

    def testMemberListDefault(self):
        """Tests that we've been entered into the member dictionary correctly"""
        self.assertEqual(
            {'uniqueId': [self.cd]},
            cdl_convert.ColorDecision.members
        )

    #==========================================================================

    def testMemberListOnIdChange(self):
        """Tests that our membership changes as our child cc changes"""
        self.assertEqual(
            {'uniqueId': [self.cd]},
            cdl_convert.ColorDecision.members
        )

        cc2 = cdl_convert.ColorCorrectionRef('001')
        self.cd.cc = cc2

        self.assertEqual(
            {'001': [self.cd]},
            cdl_convert.ColorDecision.members
        )

    #==========================================================================

    def testMemberListGrowing(self):
        """Tests that member list grows and changes correctly"""

        self.assertEqual(
            {'uniqueId': [self.cd]},
            cdl_convert.ColorDecision.members
        )

        ccr = cdl_convert.ColorCorrectionRef('uniqueId')
        cd2 = cdl_convert.ColorDecision(ccr)

        self.assertEqual(
            {'uniqueId': [self.cd, cd2]},
            cdl_convert.ColorDecision.members
        )

        cc2 = cdl_convert.ColorCorrection('betterId')
        cd3 = cdl_convert.ColorDecision(cc2)

        self.assertEqual(
            {'uniqueId': [self.cd, cd2], 'betterId': [cd3]},
            cdl_convert.ColorDecision.members
        )

        self.cd.cc = cc2

        self.assertEqual(
            {'uniqueId': [cd2], 'betterId': [cd3, self.cd]},
            cdl_convert.ColorDecision.members
        )

    #==========================================================================

    def testCC(self):
        """Tests that we return the color correct correctly"""
        self.assertEqual(
            self.cc,
            self.cd.cc
        )

    #==========================================================================

    def testIsRef(self):
        """Tests that is_ref responds correctly"""
        self.assertFalse(
            self.cd.is_ref
        )

        self.cd.cc = cdl_convert.ColorCorrectionRef('001')

        self.assertTrue(
            self.cd.is_ref
        )

    #==========================================================================

    def testMediaRef(self):
        """Tests that media ref returns"""
        self.assertEqual(
            self.media_ref,
            self.cd.media_ref
        )

        self.cd.media_ref = None

        self.assertEqual(
            None,
            self.cd.media_ref
        )

        self.media_ref.parent = 'bob'

        self.cd.media_ref = self.media_ref

        self.assertEqual(
            self.cd,
            self.cd.media_ref.parent
        )

    #==========================================================================

    def testResetMembers(self):
        """Tess that our membership resets correctly"""

        self.assertEqual(
            {'uniqueId': [self.cd]},
            cdl_convert.ColorDecision.members
        )

        cdl_convert.ColorDecision.reset_members()

        self.assertEqual(
            {},
              cdl_convert.ColorDecision.members
        )

    #==========================================================================

    def testSetParentage(self):
        """Sets reseting the parentage to point to our current frame"""

        self.assertEqual(
            self.cd,
            self.cc.parent
        )

        self.assertEqual(
            self.cd,
            self.cd.media_ref.parent
        )

        self.cc.parent = 'bob'
        self.media_ref.parent = 'joe'

        self.cd.set_parentage()

        self.assertEqual(
            self.cd,
            self.cc.parent
        )

        self.assertEqual(
            self.cd,
            self.cd.media_ref.parent
        )

# ColorNodeBase ===============================================================


class TestColorNodeBase(unittest.TestCase):
    """Tests the very simple base class ColorNodeBase"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.node = ColorNodeBase()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testDesc(self):
        """Tests that desc inherited"""

        self.assertTrue(
            hasattr(self.node, 'desc')
        )

        self.assertEqual(
            [],
            self.node.desc
        )

# MediaRef ====================================================================


class TestMediaRefProperties(unittest.TestCase):
    """Tests all aspects of the MediaRef class"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.directory = 'heeba/jeeba/race'
        self.filename = 'car.jpg'
        self.protocol = 'ftp'
        self.path = os.path.join(self.directory, self.filename)
        self.ref = self.protocol + '://' + self.path
        cc = cdl_convert.ColorCorrectionRef('001')
        self.parent = cdl_convert.ColorDecision(cc)
        self.mr = cdl_convert.MediaRef(
            ref_uri=self.ref,
            parent=self.parent
        )

    #==========================================================================

    def tearDown(self):
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testParent(self):
        """Tests that parent gets set correctly"""
        self.assertEqual(
            self.parent,
            self.mr.parent
        )

    #==========================================================================

    def testSeqDefaults(self):
        """Tests that seq attributes start uninitialized and return proper defaults"""
        # Before accessing sequence properties, _sequence_info should be None
        self.assertIsNone(self.mr._sequence_info)
        
        # Accessing is_seq should initialize _sequence_info and return False for non-sequences
        self.assertFalse(self.mr.is_seq)
        
        # After initialization, _sequence_info should exist
        self.assertIsNotNone(self.mr._sequence_info)
        
        # seqs should return empty list for non-sequences
        self.assertEqual([], self.mr.seqs)

    #==========================================================================

    def testMembership(self):
        """Tests that we were added to the member dictionary"""
        self.assertEqual(
            {self.ref: [self.mr]},
            cdl_convert.MediaRef.members
        )

    #==========================================================================

    def testDirectoryReturn(self):
        """Tests that directory returns correctly"""
        self.assertEqual(
            self.directory,
            self.mr.directory
        )

        self.mr.directory = 'burp'

        self.assertEqual(
            'burp',
            self.mr.directory
        )

    #==========================================================================

    @mock.patch('cdl_convert.MediaRef._reset_cached_properties')
    @mock.patch('cdl_convert.MediaRef._change_membership')
    def testDirectorySetString(self, mock_cm, mock_rcp):
        """Tests that directory sets with a string correctly"""
        self.assertEqual(
            self.directory,
            self.mr.directory
        )

        old_ref = self.mr.ref
        new_directory = 'dhsjkd/hahkad'
        self.mr.directory = new_directory

        self.assertEqual(
            new_directory,
            self.mr.directory
        )

        protocol = self.protocol + '://' if self.protocol else ''
        new_ref = protocol + os.path.join(new_directory, self.filename)

        self.assertEqual(
            new_ref,
            self.mr.ref
        )

        mock_cm.assert_called_once_with(
            old_ref=old_ref
        )
        mock_rcp.assert_called_once_with()

    #==========================================================================

    def testDirectorySetBadType(self):
        """Tests that directory doesn't set with a bad type"""
        def setDirectory():
            self.mr.directory = 12345

        self.assertRaises(
            TypeError,
            setDirectory
        )

    #==========================================================================

    @mock.patch('pathlib.Path.exists')
    def testExists(self, mock_exists):
        """Tests that exists returns correct information"""
        mock_exists.return_value = True

        self.assertTrue(
            self.mr.exists
        )

        mock_exists.assert_called_once_with()

        mock_exists.return_value = False

        self.assertFalse(
            self.mr.exists
        )

    #==========================================================================

    def testFilenameReturn(self):
        """Tests that filename returns correctly"""
        self.assertEqual(
            self.filename,
            self.mr.filename
        )

        self.mr.filename = 'burp'

        self.assertEqual(
            'burp',
            self.mr.filename
        )

    #==========================================================================

    @mock.patch('cdl_convert.MediaRef._reset_cached_properties')
    @mock.patch('cdl_convert.MediaRef._change_membership')
    def testFilenameSetString(self, mock_cm, mock_rcp):
        """Tests that filename sets with a string correctly"""
        self.assertEqual(
            self.filename,
            self.mr.filename
        )

        old_ref = self.mr.ref
        new_filename = 'bus.exr'
        self.mr.filename = new_filename

        self.assertEqual(
            new_filename,
            self.mr.filename
        )

        protocol = self.protocol + '://' if self.protocol else ''
        new_ref = protocol + os.path.join(self.directory, new_filename)

        self.assertEqual(
            new_ref,
            self.mr.ref
        )

        mock_cm.assert_called_once_with(
            old_ref=old_ref
        )
        mock_rcp.assert_called_once_with()

    #==========================================================================

    def testFilenameSetBadType(self):
        """Tests that filename doesn't set with a bad type"""
        def setFilename():
            self.mr.filename = 12345

        self.assertRaises(
            TypeError,
            setFilename
        )

    #==========================================================================

    @mock.patch('pathlib.Path.is_absolute')
    def testIsAbs(self, mock_abs):
        """Tests the is_abs property"""
        mock_abs.return_value = True

        self.assertTrue(
            self.mr.is_abs
        )

        mock_abs.assert_called_once_with()

        mock_abs.return_value = False

        self.assertFalse(
            self.mr.is_abs
        )

    #==========================================================================

    @mock.patch('pathlib.Path.is_dir')
    def testIsDir(self, mock_dir):
        """Tests the is_dir property"""
        mock_dir.return_value = True

        self.assertTrue(
            self.mr.is_dir
        )

        mock_dir.assert_called_once_with()

        mock_dir.return_value = False

        self.assertFalse(
            self.mr.is_dir
        )

    #==========================================================================

    @mock.patch('cdl_convert.MediaRef._get_sequences')
    def testIsSeq(self, mock_seq):
        """Tests the is_seq property returns is_seq and calls _get_sequences"""
        # Set up a mock sequence info to test caching behavior
        from cdl_convert.decision import SequenceInfo
        self.mr._sequence_info = SequenceInfo(is_sequence=True, sequences=['test'])

        self.assertEqual(
            True,
            self.mr.is_seq
        )

        self.assertFalse(
            mock_seq.called
        )

        # Reset to None to test lazy loading
        self.mr._sequence_info = None

        # This should trigger _get_sequences call
        _ = self.mr.is_seq

        mock_seq.assert_called_once_with()

    #==========================================================================

    @mock.patch('os.path.join')
    def testPathMock(self, mock_path):
        """Tests that path is called correctly"""
        mock_path.return_value = 'ed'
        self.assertEqual(
            'ed',
            self.mr.path
        )

        mock_path.assert_called_once_with(self.directory, self.filename)

    #==========================================================================

    def testPathNoMock(self):
        """Tests that path is joined correctly without mock"""
        self.assertEqual(
            os.path.join(self.directory, self.filename),
            self.mr.path
        )

    #==========================================================================

    def testProtocolReturn(self):
        """Tests that protocol returns correctly"""
        self.assertEqual(
            self.protocol,
            self.mr.protocol
        )

        self.mr.protocol = 'burp'

        self.assertEqual(
            'burp',
            self.mr.protocol
        )

    #==========================================================================

    @mock.patch('cdl_convert.MediaRef._reset_cached_properties')
    @mock.patch('cdl_convert.MediaRef._change_membership')
    def testProtocolSetString(self, mock_cm, mock_rcp):
        """Tests that protocol sets with a string correctly"""
        self.assertEqual(
            self.protocol,
            self.mr.protocol
        )

        old_ref = self.mr.ref
        new_protocol = 'edward'
        self.mr.protocol = new_protocol

        self.assertEqual(
            new_protocol,
            self.mr.protocol
        )

        protocol = new_protocol + '://'
        new_ref = protocol + os.path.join(self.directory, self.filename)

        self.assertEqual(
            new_ref,
            self.mr.ref
        )

        mock_cm.assert_called_once_with(
            old_ref=old_ref
        )
        mock_rcp.assert_called_once_with()

    #==========================================================================

    def testProtocolSetBadType(self):
        """Tests that protocol doesn't set with a bad type"""
        def setProtocol():
            self.mr.protocol = 12345

        self.assertRaises(
            TypeError,
            setProtocol
        )

    #==========================================================================

    def testProtocolTruncate(self):
        """Tests that protocol truncates the ://"""
        self.assertEqual(
            self.protocol,
            self.mr.protocol
        )

        self.mr.protocol = 'aladdin://'

        self.assertEqual(
            'aladdin',
            self.mr.protocol
        )

    #==========================================================================

    def testRef(self):
        """Tests that ref returns correctly"""
        self.assertEqual(
            self.ref,
            self.mr.ref
        )

    #==========================================================================

    @mock.patch('cdl_convert.MediaRef._reset_cached_properties')
    @mock.patch('cdl_convert.MediaRef._change_membership')
    def testSetRefWithProtocol(self, mock_cm, mock_rcp):
        """Tests that ref sets with a string correctly"""
        self.assertEqual(
            self.ref,
            self.mr.ref
        )

        new_ref = 'edward://' + os.path.join(
            'loves/to/eat/snow/in/the',
            'winter.#####.ned'
        )
        self.mr.ref = new_ref

        self.assertEqual(
            new_ref,
            self.mr.ref
        )

        self.assertEqual(
            'edward',
            self.mr.protocol
        )

        self.assertEqual(
            'loves/to/eat/snow/in/the',
            self.mr.directory
        )

        self.assertEqual(
            'winter.#####.ned',
            self.mr.filename
        )

        mock_cm.assert_called_once_with(
            old_ref=self.ref
        )
        mock_rcp.assert_called_once_with()

    #==========================================================================

    @mock.patch('cdl_convert.MediaRef._reset_cached_properties')
    @mock.patch('cdl_convert.MediaRef._change_membership')
    def testSetRefNoProtocol(self, mock_cm, mock_rcp):
        """Tests that ref sets with a string correctly"""
        self.assertEqual(
            self.ref,
            self.mr.ref
        )

        new_ref = os.path.join('/loves/to/eat/snow/in/the', 'winter.#####.ned')
        self.mr.ref = new_ref

        self.assertEqual(
            new_ref,
            self.mr.ref
        )

        self.assertEqual(
            '',
            self.mr.protocol
        )

        self.assertEqual(
            '/loves/to/eat/snow/in/the',
            self.mr.directory
        )

        self.assertEqual(
            'winter.#####.ned',
            self.mr.filename
        )

        mock_cm.assert_called_once_with(
            old_ref=self.ref
        )
        mock_rcp.assert_called_once_with()

    #==========================================================================

    def testSetRefBadType(self):
        def setRef():
            self.mr.ref = 12345

        self.assertRaises(
            TypeError,
            setRef
        )

    #==========================================================================

    @mock.patch('cdl_convert.MediaRef._get_sequences')
    def testSeq(self, mock_gs):
        """Tests the seq attribute makes the correct calls"""
        from cdl_convert.decision import SequenceInfo
        self.mr._sequence_info = SequenceInfo(is_sequence=True, sequences=['apple', 'banana'])

        self.assertEqual(
            'apple',
            self.mr.seq
        )

        # Should not call _get_sequences since we have cached data
        self.assertFalse(
            mock_gs.called
        )

        # Test non-sequence case
        self.mr._sequence_info = SequenceInfo(is_sequence=False, sequences=[])

        self.assertEqual(
            None,
            self.mr.seq
        )

        # Test that we pulled from the cache
        self.assertFalse(
            mock_gs.called
        )

    #==========================================================================

    @mock.patch('cdl_convert.MediaRef._get_sequences')
    def testSeqs(self, mock_gs):
        """Tests the seqs attribute makes the correct calls"""
        from cdl_convert.decision import SequenceInfo
        self.mr._sequence_info = SequenceInfo(is_sequence=True, sequences=['apple', 'banana'])

        self.assertEqual(
            ['apple', 'banana'],
            self.mr.seqs
        )

        # Should not call _get_sequences since we have cached data
        self.assertFalse(
            mock_gs.called
        )

        # Test non-sequence case
        self.mr._sequence_info = SequenceInfo(is_sequence=False, sequences=[])

        self.assertEqual(
            [],
            self.mr.seqs
        )

        # Test that we pulled from the cache
        self.assertFalse(
            mock_gs.called
        )


class TestMediaRefPropertiesOdd(TestMediaRefProperties):
    """Tests all aspects of the MediaRef class"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()
        self.directory = '/bicycle24/myHat/race_condition14'
        self.filename = '17438.hds356_######.exr'
        self.protocol = ''
        self.path = os.path.join(self.directory, self.filename)
        self.ref = self.path
        cc = cdl_convert.ColorCorrectionRef('001')
        self.parent = cdl_convert.ColorDecision(cc)
        self.mr = cdl_convert.MediaRef(
            ref_uri=self.ref,
            parent=self.parent
        )


class TestMediaRefChangeMembership(unittest.TestCase):
    """Tests the private method _change_membership"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.mr = cdl_convert.MediaRef('hello')

    def tearDown(self):
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testNormalOperation(self):
        """Tests that in normal circumstances, change membership works"""
        self.assertEqual(
            {'hello': [self.mr]},
            cdl_convert.MediaRef.members
        )

        self.mr._ref_info.filename = 'goodbye'
        self.mr._change_membership(old_ref='hello')

        self.assertEqual(
            {'goodbye': [self.mr]},
            cdl_convert.MediaRef.members
        )

    #==========================================================================

    def testMultipleNewRefs(self):
        """Tests appended to a list that already has a member"""
        self.mr2 = cdl_convert.MediaRef('goodbye')

        self.assertEqual(
            {'hello': [self.mr], 'goodbye': [self.mr2]},
            cdl_convert.MediaRef.members
        )

        self.mr._ref_info.filename = 'goodbye'
        self.mr._change_membership(old_ref='hello')

        self.assertEqual(
            {'goodbye': [self.mr2, self.mr]},
            cdl_convert.MediaRef.members
        )

    #==========================================================================

    def testMultipleOldRefs(self):
        """Tests removing from a list that still has a member"""
        self.mr2 = cdl_convert.MediaRef('hello')

        self.assertEqual(
            {'hello': [self.mr, self.mr2]},
            cdl_convert.MediaRef.members
        )

        self.mr._ref_info.filename = 'goodbye'
        self.mr._change_membership(old_ref='hello')

        self.assertEqual(
            {'hello': [self.mr2],'goodbye': [self.mr]},
            cdl_convert.MediaRef.members
        )

    #==========================================================================

    def testBrokenDict(self):
        """Tests that we don't fail just because we're not in the dict"""
        cdl_convert.reset_all()

        self.mr._ref_info.filename = 'goodbye'
        self.mr._change_membership(old_ref='hello')

        self.assertEqual(
            {'goodbye': [self.mr]},
            cdl_convert.MediaRef.members
        )


class TestMediaRefGetSequences(unittest.TestCase):
    """Tests the functionality of getting sequences"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.mr = cdl_convert.MediaRef('hello')
        self.file = 'TCM1L001_20140330.0830710.ari'
        self.seq = 'TCM1L001_20140330.#######.ari'
        self.files = [
            '.aliases',
            'pepperjack_corn.jpg',
            'TCM1L001_20140330.0830710.ari',
            'TCM1L001_20140330.0830711.ari',
            'TCM1L001_20140330.0830712.ari',
            'TCM1L001_20140330.0830713.ari',
            'TCM1L001_20140330.0830714.ari',
            'TCM1L014_20140330.0863186.ari',
            'TCM1L014_20140330.0863516.ari',
            'TCM1L014_20140330.0863916.ari',
            'TCM1L014_20140330.0864516.ari',
            'TCM1L014_20140330.0899516.ari',
            'TCM1L014_20140330.1863516.ari',
            'TCM1L014_20140330.2863516.ari',
            'TCM1L028_20140330.0926197.ari',
            'The best file of my life..ari',
        ]
        self.seqs = [
            'TCM1L001_20140330.#######.ari',
            'TCM1L014_20140330.#######.ari',
            'TCM1L028_20140330.#######.ari',
        ]

        self.is_seq = True

    #==========================================================================
    # TESTS
    #==========================================================================

    @mock.patch('os.path.isdir')
    def testSingleFile(self, mock_dir):
        """Tests a single file for being a sequence"""
        mock_dir.return_value = False

        self.mr.filename = self.file

        self.assertEqual(
            self.is_seq,
            self.mr.is_seq
        )

        self.assertEqual(
            self.seq,
            self.mr.seq
        )

        if self.seq:
            self.assertEqual(
                [self.seq],
                self.mr.seqs
            )
        else:
            self.assertEqual(
                [],
                self.mr.seqs
            )

    #==========================================================================

    @mock.patch('pathlib.Path.iterdir')
    @mock.patch('pathlib.Path.exists')
    @mock.patch('pathlib.Path.is_dir')
    def testDirExists(self, mock_dir, mock_exists, mock_iterdir):
        """Tests parsing a directory for files"""
        mock_dir.return_value = True
        mock_exists.return_value = True
        
        # Mock Path objects for the files
        mock_files = []
        for filename in self.files:
            mock_file = mock.Mock()
            mock_file.name = filename
            mock_file.is_file.return_value = True
            mock_files.append(mock_file)
        
        mock_iterdir.return_value = mock_files

        self.assertEqual(
            self.is_seq,
            self.mr.is_seq
        )

        if len(self.seqs) > 0:
            self.assertEqual(
                self.seqs[0],
                self.mr.seq
            )
        else:
            self.assertEqual(
                None,
                self.mr.seq
            )

        self.assertEqual(
            self.seqs,
            self.mr.seqs
        )

        mock_iterdir.assert_called_once_with()

    #==========================================================================

    @mock.patch('pathlib.Path.exists')
    @mock.patch('pathlib.Path.is_dir')
    @mock.patch('os.path.exists')
    @mock.patch('os.path.isdir')
    def testDirDoesNotExist(self, mock_os_isdir, mock_os_exists, mock_path_is_dir, mock_path_exists):
        """Tests what happens when directory doesn't exist"""
        # Mock both os.path and pathlib methods for cross-version compatibility
        mock_os_isdir.return_value = True
        mock_os_exists.return_value = False
        mock_path_is_dir.return_value = True
        mock_path_exists.return_value = False

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            self.mr._get_sequences
        )

        cdl_convert.config.config.halt_on_error = False

        self.assertEqual(
            False,
            self.mr.is_seq
        )

        self.assertEqual(
            [],
            self.mr.seqs
        )

        self.assertEqual(
            None,
            self.mr.seq
        )


class TestMediaRefGetSequencesNoSeqs(TestMediaRefGetSequences):
    """Tests the functionality of getting sequences"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.mr = cdl_convert.MediaRef('hello')
        self.file = 'TCM1L00120140.ari'
        self.seq = None
        self.files = [
            '.aliases',
            'pepperjack_corn.jpg',
            'TCM1L001_20140330.08307k10.ari',
            'The best file of my life..ari',
        ]
        self.seqs = []

        self.is_seq = False


class TestMediaRefGetSequencesCrazySeqs(TestMediaRefGetSequences):
    """Tests the functionality of getting sequences with odd names"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.mr = cdl_convert.MediaRef('hello')
        self.file = 'B002_C001_01101G_004.R3D'
        self.seq = 'B002_C001_01101G_###.R3D'
        self.files = [
            'B002_C001_01101G_001.R3D',
            'B002_C001_01101G_002.R3D',
            'B002_C001_01101G_003.R3D',
            'B002_C001_01101G_004.R3D',
            'TakeThis SequenceandShoveitupyour.8.exr',
            'A001C008_R402.ari',  # While these are technically an image seq
            'A001C008_R902.ari',  # we don't support them.
            'BB50A-05_A039.14278002315672351753261757362236126723618.ari'
        ]
        self.seqs = [
            'B002_C001_01101G_###.R3D',
            'TakeThis SequenceandShoveitupyour.#.exr',
            'BB50A-05_A039.#########################################.ari'
        ]

        self.is_seq = True


class TestMediaRefGetSequencesPercentDigit(TestMediaRefGetSequences):
    """Tests the functionality of getting seq match with %0d return"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.mr = cdl_convert.MediaRef('hello')
        self.file = 'B002 C001-01101G_%327864d.R3D'
        self.seq = 'B002 C001-01101G_%327864d.R3D'
        self.files = [
            'B002_C001_01101G_001.R3D',
            'B002_C001_01101G_002.R3D',
            'B002_C001_01101G_003.R3D',
            'B002_C001_01101G_004.R3D',
            'TakeThis SequenceandShoveitupyour.8.exr',
            'A001C008_R402.ari',  # While these are technically an image seq
            'A001C008_R902.ari',  # we don't support them.
            'BB50A-05_A039.14278002315672351753261757362236126723618.ari'
        ]
        self.seqs = [
            'B002_C001_01101G_###.R3D',
            'TakeThis SequenceandShoveitupyour.#.exr',
            'BB50A-05_A039.#########################################.ari'
        ]

        self.is_seq = True


class TestMediaRefGetSequencesPercentDigitUnderscore(TestMediaRefGetSequences):
    """Tests the functionality of getting seq match with %0d return"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.mr = cdl_convert.MediaRef('hello')
        self.file = 'TCM1L001_20140330.%05d.ari'
        self.seq = 'TCM1L001_20140330.%05d.ari'
        self.files = [
            '.aliases',
            'pepperjack_corn.jpg',
            'TCM1L001_20140330.0830710.ari',
            'TCM1L001_20140330.0830711.ari',
            'TCM1L001_20140330.0830712.ari',
            'TCM1L001_20140330.0830713.ari',
            'TCM1L001_20140330.0830714.ari',
            'TCM1L014_20140330.0863186.ari',
            'TCM1L014_20140330.0863516.ari',
            'TCM1L014_20140330.0863916.ari',
            'TCM1L014_20140330.0864516.ari',
            'TCM1L014_20140330.0899516.ari',
            'TCM1L014_20140330.1863516.ari',
            'TCM1L014_20140330.2863516.ari',
            'TCM1L028_20140330.0926197.ari',
            'The best file of my life..ari',
        ]
        self.seqs = [
            'TCM1L001_20140330.#######.ari',
            'TCM1L014_20140330.#######.ari',
            'TCM1L028_20140330.#######.ari',
        ]

        self.is_seq = True

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
            [],
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
            Decimal('1.0'),
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
            Decimal('12.3'),
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

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSat
        )

        cdl_convert.config.config.halt_on_error = False

        setSat()

        self.assertEqual(
            Decimal('0.0'),
            self.node.sat
        )

    #==========================================================================

    def testSetWithFloat(self):
        """Tests that we can set sat with a single float"""
        self.node.sat = 100.1

        self.assertEqual(
            Decimal('100.1'),
            self.node.sat
        )

    #==========================================================================

    def testSetWithNegativeFloat(self):
        """Tests that we can't set sat with a single negative float"""
        def setSat():
            self.node.sat = -20.1

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSat
        )

        cdl_convert.config.config.halt_on_error = False

        setSat()

        self.assertEqual(
            Decimal('0.0'),
            self.node.sat
        )

    #==========================================================================

    def testSetWithInt(self):
        """Tests that we can set sat with a single int"""
        self.node.sat = 2

        self.assertEqual(
            Decimal('2.0'),
            self.node.sat
        )

    #==========================================================================

    def testSetWithNegativeInt(self):
        """Tests that we can't set sat with a single negative float"""
        def setSat():
            self.node.sat = -20

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSat
        )

        cdl_convert.config.config.halt_on_error = False

        setSat()

        self.assertEqual(
            Decimal('0.0'),
            self.node.sat
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
            [],
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
            (Decimal('1.0'), Decimal('1.0'), Decimal('1.0')),
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
            (Decimal('12.3'), Decimal('12.3'), Decimal('12.3')),
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

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSlope
        )

        cdl_convert.config.config.halt_on_error = False

        setSlope()

        self.assertEqual(
            (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
            self.node.slope
        )

    #==========================================================================

    def testSetSlopeWithFloat(self):
        """Tests that we can set slope with a single float"""
        self.node.slope = 100.1

        self.assertEqual(
            (Decimal('100.1'), Decimal('100.1'), Decimal('100.1')),
            self.node.slope
        )

    #==========================================================================

    def testSetSlopeWithNegativeFloat(self):
        """Tests that we can't set slope with a single negative float"""
        def setSlope():
            self.node.slope = -20.1

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSlope
        )

        cdl_convert.config.config.halt_on_error = False

        setSlope()

        self.assertEqual(
            (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
            self.node.slope
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

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSlope
        )

        cdl_convert.config.config.halt_on_error = False

        setSlope()

        self.assertEqual(
            (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
            self.node.slope
        )

    #==========================================================================

    def testSlopeSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setSlope():
            self.node.slope = [-1.3782, 278.32, 0.738378233782]

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setSlope
        )

        cdl_convert.config.config.halt_on_error = False

        setSlope()

        self.assertEqual(
            (Decimal('0.0'), Decimal('278.32'), Decimal('0.738378233782')),
            self.node.slope
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
        slopeD = tuple([Decimal(str(i)) for i in slope])

        self.node.slope = slope

        self.assertEqual(
            slopeD,
            self.node.slope
        )

    #==========================================================================

    def testOffsetDefault(self):
        """Tests that offset starts off with a default value of 1.0"""
        self.assertEqual(
            (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
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
            (Decimal('12.3'), Decimal('12.3'), Decimal('12.3')),
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
            (Decimal('-20.0'), Decimal('-20.0'), Decimal('-20.0')),
            self.node.offset
        )

    #==========================================================================

    def testSetOffsetWithFloat(self):
        """Tests that we can set offset with a single float"""
        self.node.offset = 100.1

        self.assertEqual(
            (Decimal('100.1'), Decimal('100.1'), Decimal('100.1')),
            self.node.offset
        )

    #==========================================================================

    def testSetOffsetWithNegativeFloat(self):
        """Tests that we can set offset with a single negative float"""
        self.node.offset = -20.1

        self.assertEqual(
            (Decimal('-20.1'), Decimal('-20.1'), Decimal('-20.1')),
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
            (Decimal('-20.0'), Decimal('-20.0'), Decimal('-20.0')),
            self.node.offset
        )

    #==========================================================================

    def testOffsetSetNegative(self):
        """Tests that offset can be set to negative value"""
        offset = [-1.3782, 278.32, 0.738378233782]
        self.node.offset = offset
        offsetD = tuple([Decimal(str(i)) for i in offset])

        self.assertEqual(
            offsetD,
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
        offsetD = tuple([Decimal(str(i)) for i in offset])

        self.node.offset = offset

        self.assertEqual(
            offsetD,
            self.node.offset
        )

    #==========================================================================

    def testPowerDefault(self):
        """Tests that power starts off with a default value of 1.0"""
        self.assertEqual(
            (Decimal('1.0'), Decimal('1.0'), Decimal('1.0')),
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
            (Decimal('12.3'), Decimal('12.3'), Decimal('12.3')),
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

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setPower
        )

        cdl_convert.config.config.halt_on_error = False

        setPower()

        self.assertEqual(
            (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
            self.node.power
        )

    #==========================================================================

    def testSetPowerWithFloat(self):
        """Tests that we can set power with a single float"""
        self.node.power = 100.1

        self.assertEqual(
            (Decimal('100.1'), Decimal('100.1'), Decimal('100.1')),
            self.node.power
        )

    #==========================================================================

    def testSetPowerWithNegativeFloat(self):
        """Tests that we can't set power with a single negative float"""
        def setPower():
            self.node.power = -20.1

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setPower
        )

        cdl_convert.config.config.halt_on_error = False

        setPower()

        self.assertEqual(
            (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
            self.node.power
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

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setPower
        )

        cdl_convert.config.config.halt_on_error = False

        setPower()

        self.assertEqual(
            (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
            self.node.power
        )

    #==========================================================================

    def testPowerSetNegative(self):
        """Tests that ValueError raised if negative value"""
        def setPower():
            self.node.power = [-1.3782, 278.32, 0.738378233782]

        cdl_convert.config.config.halt_on_error = True

        self.assertRaises(
            ValueError,
            setPower
        )

        cdl_convert.config.config.halt_on_error = False

        setPower()

        self.assertEqual(
            (Decimal('0.0'), Decimal('278.32'), Decimal('0.738378233782')),
            self.node.power
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
        powerD = tuple([Decimal(str(i)) for i in power])

        self.node.power = power

        self.assertEqual(
            powerD,
            self.node.power
        )

#==============================================================================
# DATACLASS TESTS
#==============================================================================


class TestColorValues(unittest.TestCase):
    """Tests the ColorValues dataclass"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()

    def tearDown(self):
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testDefaultValues(self):
        """Tests ColorValues default values are unity"""
        from cdl_convert.correction import ColorValues
        cv = ColorValues()
        
        self.assertEqual(
            (Decimal('1.0'), Decimal('1.0'), Decimal('1.0')),
            cv.slope
        )
        self.assertEqual(
            (Decimal('0.0'), Decimal('0.0'), Decimal('0.0')),
            cv.offset
        )
        self.assertEqual(
            (Decimal('1.0'), Decimal('1.0'), Decimal('1.0')),
            cv.power
        )
        self.assertEqual(
            Decimal('1.0'),
            cv.saturation
        )
        self.assertTrue(cv.is_unity())

    #==========================================================================

    def testCustomValues(self):
        """Tests ColorValues with custom values"""
        from cdl_convert.correction import ColorValues
        cv = ColorValues(
            slope=(Decimal('1.2'), Decimal('1.1'), Decimal('1.0')),
            offset=(Decimal('0.1'), Decimal('-0.05'), Decimal('0.0')),
            power=(Decimal('0.9'), Decimal('1.0'), Decimal('1.1')),
            saturation=Decimal('1.2')
        )
        
        self.assertEqual(
            (Decimal('1.2'), Decimal('1.1'), Decimal('1.0')),
            cv.slope
        )
        self.assertEqual(
            (Decimal('0.1'), Decimal('-0.05'), Decimal('0.0')),
            cv.offset
        )
        self.assertEqual(
            (Decimal('0.9'), Decimal('1.0'), Decimal('1.1')),
            cv.power
        )
        self.assertEqual(
            Decimal('1.2'),
            cv.saturation
        )
        self.assertFalse(cv.is_unity())

    #==========================================================================

    def testValidationBadSlopeLength(self):
        """Tests ColorValues validation fails with wrong slope length"""
        from cdl_convert.correction import ColorValues
        
        def createBadColorValues():
            ColorValues(slope=(Decimal('1.0'), Decimal('1.0')))  # Only 2 values
        
        self.assertRaises(
            ValueError,
            createBadColorValues
        )

    #==========================================================================

    def testValidationNegativeSlope(self):
        """Tests ColorValues validation with negative slope values"""
        from cdl_convert.correction import ColorValues
        
        cdl_convert.config.config.halt_on_error = True
        
        def createBadColorValues():
            ColorValues(slope=(Decimal('-1.0'), Decimal('1.0'), Decimal('1.0')))
        
        self.assertRaises(
            ValueError,
            createBadColorValues
        )
        
        cdl_convert.config.config.halt_on_error = False

    #==========================================================================

    def testValidationNegativeSaturation(self):
        """Tests ColorValues validation with negative saturation"""
        from cdl_convert.correction import ColorValues
        
        cdl_convert.config.config.halt_on_error = True
        
        def createBadColorValues():
            ColorValues(saturation=Decimal('-1.0'))
        
        self.assertRaises(
            ValueError,
            createBadColorValues
        )
        
        cdl_convert.config.config.halt_on_error = False

    #==========================================================================

    def testToUnity(self):
        """Tests ColorValues to_unity method"""
        from cdl_convert.correction import ColorValues
        cv = ColorValues(
            slope=(Decimal('1.2'), Decimal('1.1'), Decimal('1.0')),
            saturation=Decimal('1.2')
        )
        
        unity = cv.to_unity()
        self.assertTrue(unity.is_unity())
        self.assertEqual(
            (Decimal('1.0'), Decimal('1.0'), Decimal('1.0')),
            unity.slope
        )
        self.assertEqual(
            Decimal('1.0'),
            unity.saturation
        )


class TestColorCorrectionDataclassIntegration(unittest.TestCase):
    """Tests ColorCorrection integration with ColorValues dataclass"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()
        self.cc = cdl_convert.ColorCorrection('test_cc')

    def tearDown(self):
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testGetColorValues(self):
        """Tests getting color values as ColorValues dataclass"""
        from cdl_convert.correction import ColorValues
        
        cv = self.cc.get_color_values()
        self.assertIsInstance(cv, ColorValues)
        self.assertTrue(cv.is_unity())

    #==========================================================================

    def testSetColorValues(self):
        """Tests setting color values from ColorValues dataclass"""
        from cdl_convert.correction import ColorValues
        
        new_values = ColorValues(
            slope=(Decimal('1.2'), Decimal('1.1'), Decimal('1.0')),
            offset=(Decimal('0.1'), Decimal('-0.05'), Decimal('0.0')),
            power=(Decimal('0.9'), Decimal('1.0'), Decimal('1.1')),
            saturation=Decimal('1.2')
        )
        
        self.cc.set_color_values(new_values)
        
        self.assertEqual(new_values.slope, self.cc.slope)
        self.assertEqual(new_values.offset, self.cc.offset)
        self.assertEqual(new_values.power, self.cc.power)
        self.assertEqual(new_values.saturation, self.cc.sat)

    #==========================================================================

    def testIsUnity(self):
        """Tests ColorCorrection is_unity method"""
        self.assertTrue(self.cc.is_unity())
        
        self.cc.slope = (Decimal('1.2'), Decimal('1.0'), Decimal('1.0'))
        self.assertFalse(self.cc.is_unity())

    #==========================================================================

    def testRoundTripColorValues(self):
        """Tests getting and setting color values maintains consistency"""
        from cdl_convert.correction import ColorValues
        
        # Set some non-unity values
        self.cc.slope = (Decimal('1.2'), Decimal('1.1'), Decimal('1.0'))
        self.cc.offset = (Decimal('0.1'), Decimal('-0.05'), Decimal('0.0'))
        self.cc.power = (Decimal('0.9'), Decimal('1.0'), Decimal('1.1'))
        self.cc.sat = Decimal('1.2')
        
        # Get as dataclass
        cv = self.cc.get_color_values()
        
        # Create new CC and set from dataclass
        cc2 = cdl_convert.ColorCorrection('test_cc2')
        cc2.set_color_values(cv)
        
        # Verify they match
        self.assertEqual(self.cc.slope, cc2.slope)
        self.assertEqual(self.cc.offset, cc2.offset)
        self.assertEqual(self.cc.power, cc2.power)
        self.assertEqual(self.cc.sat, cc2.sat)


class TestMediaRefInfo(unittest.TestCase):
    """Tests the MediaRefInfo dataclass"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()

    def tearDown(self):
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testDefaultValues(self):
        """Tests MediaRefInfo default values"""
        from cdl_convert.decision import MediaRefInfo
        mri = MediaRefInfo()
        
        self.assertEqual('', mri.protocol)
        self.assertEqual('', mri.directory)
        self.assertEqual('', mri.filename)
        self.assertEqual('.', mri.to_uri())

    #==========================================================================

    def testCustomValues(self):
        """Tests MediaRefInfo with custom values"""
        from cdl_convert.decision import MediaRefInfo
        mri = MediaRefInfo(
            protocol='http',
            directory='/path/to/files',
            filename='image.jpg'
        )
        
        self.assertEqual('http', mri.protocol)
        self.assertEqual('/path/to/files', mri.directory)
        self.assertEqual('image.jpg', mri.filename)

    #==========================================================================

    def testToUriWithProtocol(self):
        """Tests MediaRefInfo to_uri with protocol"""
        from cdl_convert.decision import MediaRefInfo
        mri = MediaRefInfo(
            protocol='http',
            directory='example.com/path',
            filename='file.jpg'
        )
        
        self.assertEqual('http://example.com/path/file.jpg', mri.to_uri())

    #==========================================================================

    def testToUriNoProtocol(self):
        """Tests MediaRefInfo to_uri without protocol"""
        from cdl_convert.decision import MediaRefInfo
        mri = MediaRefInfo(
            directory='path/to/files',
            filename='image.jpg'
        )
        
        self.assertEqual('path/to/files/image.jpg', mri.to_uri())

    #==========================================================================

    def testToUriNoFilename(self):
        """Tests MediaRefInfo to_uri with directory only"""
        from cdl_convert.decision import MediaRefInfo
        mri = MediaRefInfo(
            protocol='file',
            directory='/path/to/directory'
        )
        
        self.assertEqual('file:///path/to/directory', mri.to_uri())


class TestSequenceInfo(unittest.TestCase):
    """Tests the SequenceInfo dataclass"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()

    def tearDown(self):
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testDefaultValues(self):
        """Tests SequenceInfo default values"""
        from cdl_convert.decision import SequenceInfo
        si = SequenceInfo()
        
        self.assertFalse(si.is_sequence)
        self.assertEqual([], si.sequences)

    #==========================================================================

    def testCustomValues(self):
        """Tests SequenceInfo with custom values"""
        from cdl_convert.decision import SequenceInfo
        sequences = ['image.####.jpg', 'other.####.exr']
        si = SequenceInfo(is_sequence=True, sequences=sequences)
        
        self.assertTrue(si.is_sequence)
        self.assertEqual(sequences, si.sequences)
        self.assertEqual(2, len(si.sequences))

    #==========================================================================

    def testPostInitNoneSequences(self):
        """Tests SequenceInfo __post_init__ with None sequences"""
        from cdl_convert.decision import SequenceInfo
        si = SequenceInfo(is_sequence=True, sequences=None)
        
        self.assertTrue(si.is_sequence)
        self.assertEqual([], si.sequences)


class TestMediaRefDataclassIntegration(unittest.TestCase):
    """Tests MediaRef integration with dataclasses"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()

    def tearDown(self):
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testMediaRefUsesDataclass(self):
        """Tests MediaRef uses MediaRefInfo dataclass internally"""
        from cdl_convert.decision import MediaRefInfo
        
        mr = cdl_convert.MediaRef('http://example.com/path/file.jpg')
        
        self.assertTrue(hasattr(mr, '_ref_info'))
        self.assertIsInstance(mr._ref_info, MediaRefInfo)

    #==========================================================================

    def testMediaRefPropertiesFromDataclass(self):
        """Tests MediaRef properties work with dataclass"""
        mr = cdl_convert.MediaRef('http://example.com/path/file.jpg')
        
        self.assertEqual('http', mr.protocol)
        self.assertEqual('example.com/path', mr.directory)
        self.assertEqual('file.jpg', mr.filename)

    #==========================================================================

    def testMediaRefSequenceInfoCaching(self):
        """Tests MediaRef uses SequenceInfo for caching"""
        from cdl_convert.decision import SequenceInfo
        
        mr = cdl_convert.MediaRef('test.jpg')
        
        # Initially None
        self.assertIsNone(mr._sequence_info)
        
        # Access triggers lazy loading
        is_seq = mr.is_seq
        
        # Now should have SequenceInfo
        self.assertIsInstance(mr._sequence_info, SequenceInfo)
        self.assertEqual(is_seq, mr._sequence_info.is_sequence)

    #==========================================================================

    def testMediaRefPropertyChangesUpdateDataclass(self):
        """Tests changing MediaRef properties updates internal dataclass"""
        mr = cdl_convert.MediaRef('http://example.com/path/file.jpg')
        
        # Change protocol
        mr.protocol = 'https'
        self.assertEqual('https', mr._ref_info.protocol)
        self.assertEqual('https', mr.protocol)
        
        # Change directory
        mr.directory = 'newpath'
        self.assertEqual('newpath', mr._ref_info.directory)
        self.assertEqual('newpath', mr.directory)
        
        # Change filename
        mr.filename = 'newfile.jpg'
        self.assertEqual('newfile.jpg', mr._ref_info.filename)
        self.assertEqual('newfile.jpg', mr.filename)

    #==========================================================================

    def testMediaRefUriReconstruction(self):
        """Tests MediaRef URI reconstruction through dataclass"""
        mr = cdl_convert.MediaRef('http://example.com/path/file.jpg')
        
        # Verify original URI
        self.assertEqual('http://example.com/path/file.jpg', mr.ref)
        
        # Change components and verify URI updates
        mr.protocol = 'https'
        mr.directory = 'newpath'
        mr.filename = 'newfile.jpg'
        
        self.assertEqual('https://newpath/newfile.jpg', mr.ref)


#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
