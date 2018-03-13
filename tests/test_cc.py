#!/usr/bin/env python
"""
Tests the cc related functions of cdl_convert

REQUIREMENTS:

mock
"""

#==============================================================================
# IMPORTS
#==============================================================================

# Standard Imports
from decimal import Decimal
try:
    from unittest import mock
except ImportError:
    import mock
import os
import sys
import tempfile
import unittest
from xml.etree import ElementTree

# Grab our test's path and append the cdL_convert root directory

# There has to be a better method than:
# 1) Getting our current directory
# 2) Splitting into list
# 3) Splicing out the last 3 entries (filepath, test dir, tools dir)
# 4) Joining
# 5) Appending to our Python path.

sys.path.append('/'.join(os.path.realpath(__file__).split('/')[:-2]))

import cdl_convert

#==============================================================================
# GLOBALS
#==============================================================================

# We'll save out different and broken XMLs by hand.

# Parse XMLs ==================================================================

# Valid XMLs ==================================================================

CC_FULL = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="014_xf_seqGrade_v01">
    <Description>CC description 1</Description>
    <InputDescription>Input Desc Text</InputDescription>
    <Description>CC description 2</Description>
    <SOPNode>
        <Description>Sop description 1</Description>
        <Description>Sop description 2</Description>
        <Slope>1.014 1.0104 0.62</Slope>
        <Offset>-0.00315 -0.00124 0.3103</Offset>
        <Power>1.0 0.9983 1.0</Power>
        <Description>Sop description 3</Description>
    </SOPNode>
    <Description>CC description 3</Description>
    <SATNode>
        <Description>Sat description 1</Description>
        <Saturation>1.09</Saturation>
        <Description>Sat description 2</Description>
    </SATNode>
    <Description>CC description 4</Description>
    <ViewingDescription>Viewing Desc Text</ViewingDescription>
    <Description>CC description 5</Description>
</ColorCorrection>
"""

CC_BASIC = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="f51.200">
    <SopNode>
        <Slope>0.2331 0.678669 1.0758</Slope>
        <Offset>0.031 0.128 -0.096</Offset>
        <Power>1.8 0.97 0.961</Power>
    </SopNode>
    <SatNode>
        <Saturation>1.01</Saturation>
    </SatNode>
</ColorCorrection>
"""

# The following characters don't seem to be allowed in id fields:
CC_ODD = r"""<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="f55.100\\\\\//////">
    <Description>Raised saturation a little!?! ag... \/Offset</Description>
    <Description>Raised saturation a little!?! ag... \/Offset</Description>
    <InputDescription>METAL VIEWER!!! \/\/</InputDescription>
    <ViewingDescription>WOOD VIEWER!? ////</ViewingDescription>
    <SopNode>
        <Description>Raised saturation a little!?! ag... \/Offset</Description>
        <Slope>137829.329 4327890.9833 3489031.003</Slope>
        <Offset>-3424.011 -342789423.013 -4238923.11</Offset>
        <Power>3271893.993 .0000998 0.0000000000000000113</Power>
    </SopNode>
    <SatNode>
        <Saturation>1798787.01</Saturation>
    </SatNode>
</ColorCorrection>
"""

CC_BASIC_ORDER = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="f54.112">
    <ASC_SAT>
        <Saturation>1.01</Saturation>
    </ASC_SAT>
    <ASC_SOP>
        <Slope>0.2331 0.678669 1.0758</Slope>
        <Offset>0.031 0.128 -0.096</Offset>
        <Power>1.8 0.97 0.961</Power>
    </ASC_SOP>
</ColorCorrection>
"""

CC_BLANK_METADATA = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="burp_100.x12">
    <ViewingDescription></ViewingDescription>
    <Description></Description>
    <SOPNode>
        <Description></Description>
        <Slope>1.014 1.0104 0.62</Slope>
        <Offset>-0.00315 -0.00124 0.3103</Offset>
        <Power>1.0 0.9983 1.0</Power>
    </SOPNode>
    <Description></Description>
    <InputDescription></InputDescription>
    <SatNode>
        <Saturation>1.09</Saturation>
        <Description></Description>
    </SatNode>
    <Description></Description>
</ColorCorrection>
"""

CC_NO_SOP = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="burp_200.x15">
    <SatNode>
        <Description>I am a lovely sat node</Description>
        <Saturation>1.01</Saturation>
    </SatNode>
</ColorCorrection>
"""

CC_NO_SAT = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="burp_300.x35">
    <SopNode>
        <Slope>0.2331 0.678669 1.0758</Slope>
        <Offset>0.031 0.128 -0.096</Offset>
        <Power>1.8 0.97 0.961</Power>
    </SopNode>
</ColorCorrection>
"""

# Bad XMLs ====================================================================

CC_NO_ID = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection>
    <SopNode>
        <Slope>0.2331 0.678669 1.0758</Slope>
        <Offset>0.031 0.128 -0.096</Offset>
        <Power>1.8 0.97 0.961</Power>
    </SopNode>
    <SatNode>
        <Saturation>1.01</Saturation>
    </SatNode>
</ColorCorrection>
"""

CC_BLANK_ID = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="">
    <SopNode>
        <Slope>0.2331 0.678669 1.0758</Slope>
        <Offset>0.031 0.128 -0.096</Offset>
        <Power>1.8 0.97 0.961</Power>
    </SopNode>
    <SatNode>
        <Saturation>1.01</Saturation>
    </SatNode>
</ColorCorrection>
"""

CC_NEGATIVE_SLOPE = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="dsds">
    <SopNode>
        <Slope>-0.2331 0.678669 1.0758</Slope>
        <Offset>0.031 0.128 -0.096</Offset>
        <Power>1.8 0.97 0.961</Power>
    </SopNode>
    <SatNode>
        <Saturation>1.01</Saturation>
    </SatNode>
</ColorCorrection>
"""

# Write XMLs ==================================================================

CC_FULL_WRITE = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="014_xf_seqGrade_v01">
    <InputDescription>Input Desc Text</InputDescription>
    <ViewingDescription>Viewing Desc Text</ViewingDescription>
    <Description>CC description 1</Description>
    <Description>CC description 2</Description>
    <Description>CC description 3</Description>
    <Description>CC description 4</Description>
    <Description>CC description 5</Description>
    <SOPNode>
        <Description>Sop description 1</Description>
        <Description>Sop description 2</Description>
        <Description>Sop description 3</Description>
        <Slope>1.014 1.0104 0.62</Slope>
        <Offset>-0.00315 -0.00124 0.3103</Offset>
        <Power>1.0 0.9983 1.0</Power>
    </SOPNode>
    <SATNode>
        <Description>Sat description 1</Description>
        <Description>Sat description 2</Description>
        <Saturation>1.09</Saturation>
    </SATNode>
</ColorCorrection>
"""

# The following characters don't seem to be allowed in id fields:
CC_ODD_WRITE = r"""<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="f55.100">
    <InputDescription>METAL VIEWER!!! \/\/</InputDescription>
    <ViewingDescription>WOOD VIEWER!? ////</ViewingDescription>
    <Description>Raised saturation1 a little!?! ag... \/Offset</Description>
    <Description>Raised saturation2 a little!?! ag... \/Offset</Description>
    <SOPNode>
        <Description>Raised saturation a little!?! ag... \/Offset</Description>
        <Slope>137829.329 4327890.9833 3489031.003</Slope>
        <Offset>-3424.011 -342789423.013 -4238923.11</Offset>
        <Power>3271893.993 0.0000998 0.0000000000000000113</Power>
    </SOPNode>
    <SATNode>
        <Saturation>1798787.01</Saturation>
    </SATNode>
</ColorCorrection>
"""

CC_NO_SOP_WRITE = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="burp_200.x15">
    <SATNode>
        <Description>I am a lovely sat node</Description>
        <Saturation>1.0128109381</Saturation>
    </SATNode>
</ColorCorrection>
"""

CC_NO_SAT_WRITE = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="burp_300.x35">
    <SOPNode>
        <Slope>1.233321 0.678669 1.0758</Slope>
        <Offset>0.031 0.128 -0.096</Offset>
        <Power>1.8 0.97 0.961</Power>
    </SOPNode>
</ColorCorrection>
"""

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

# parse_cc ====================================================================


class TestParseCCBasic(unittest.TestCase):
    """Tests parsing a cc xml"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.cdl_test_id = "014_xf_seqGrade_v01"
        self.desc = [
            'CC description 1', 'CC description 2', 'CC description 3',
            'CC description 4', 'CC description 5'
        ]
        self.input_desc = 'Input Desc Text'
        self.viewing_desc = 'Viewing Desc Text'

        self.sop_node_desc = [
            'Sop description 1', 'Sop description 2', 'Sop description 3'
        ]
        self.slope = decimalize(1.014, 1.0104, 0.62)
        self.offset = decimalize(-0.00315, -0.00124, 0.3103)
        self.power = decimalize(1.0, 0.9983, 1.0)
        self.sat_node_desc = [
            'Sat description 1', 'Sat description 2'
        ]
        self.sat = Decimal('1.09')

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_FULL))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)

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

    def testId(self):
        """Tests that id was set to id attrib"""
        self.assertEqual(
            self.cdl_test_id,
            self.cdl.id
        )

    #==========================================================================

    def testDesc(self):
        """Tests that desc was set to desc element"""
        self.assertEqual(
            self.desc,
            self.cdl.desc
        )

    #==========================================================================

    def testInputDesc(self):
        """Tests that input description was set"""
        self.assertEqual(
            self.input_desc,
            self.cdl.input_desc
        )

    #==========================================================================

    def testViewingDesc(self):
        """Tests that viewing description was set"""
        self.assertEqual(
            self.viewing_desc,
            self.cdl.viewing_desc
        )

    #==========================================================================

    def testSopDesc(self):
        """Tests that desc was set to sop node's desc element"""
        self.assertEqual(
            self.sop_node_desc,
            self.cdl.sop_node.desc
        )

    #==========================================================================

    def testSatDesc(self):
        """Tests that desc was set to sat node's desc element"""
        self.assertEqual(
            self.sat_node_desc,
            self.cdl.sat_node.desc
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

#==============================================================================


class TestParseCCOdd(TestParseCCBasic):
    """Tests parsing a cc xml with odd values"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.cdl_test_id = "f55.100"  # This will have been _sanitized()
        self.desc = [
            'Raised saturation a little!?! ag... \/Offset',
            'Raised saturation a little!?! ag... \/Offset',
        ]
        self.input_desc = 'METAL VIEWER!!! \/\/'
        self.viewing_desc = 'WOOD VIEWER!? ////'

        self.sop_node_desc = [
            'Raised saturation a little!?! ag... \/Offset'
        ]
        self.slope = decimalize(137829.329, 4327890.9833, 3489031.003)
        self.offset = decimalize(-3424.011, -342789423.013, -4238923.11)
        self.power = decimalize(3271893.993, .0000998, 0.0000000000000000113)
        self.sat_node_desc = []
        self.sat = Decimal('1798787.01')

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_ODD))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)

#==============================================================================


class TestParseCCBasic(TestParseCCBasic):
    """Tests parsing a cc xml with minimal values"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.cdl_test_id = "f51.200"
        self.desc = []
        self.input_desc = None
        self.viewing_desc = None

        self.sop_node_desc = []
        self.slope = decimalize(0.2331, 0.678669, 1.0758)
        self.offset = decimalize(0.031, 0.128, -0.096)
        self.power = decimalize(1.8, 0.97, 0.961)
        self.sat_node_desc = []
        self.sat = Decimal('1.01')

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_BASIC))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)

#==============================================================================


class TestParseCCBasicOrder(TestParseCCBasic):
    """Tests parsing a cc xml with minimal, but out of order values"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.cdl_test_id = "f54.112"
        self.desc = []
        self.input_desc = None
        self.viewing_desc = None

        self.sop_node_desc = []
        self.slope = decimalize(0.2331, 0.678669, 1.0758)
        self.offset = decimalize(0.031, 0.128, -0.096)
        self.power = decimalize(1.8, 0.97, 0.961)
        self.sat_node_desc = []
        self.sat = Decimal('1.01')

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_BASIC_ORDER))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)

#==============================================================================


class TestParseCCBlankMetadata(TestParseCCBasic):
    """Tests parsing a cc xml with blank metadata fields"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.cdl_test_id = "burp_100.x12"
        self.desc = []
        self.input_desc = None
        self.viewing_desc = None

        self.sop_node_desc = []
        self.slope = decimalize(1.014, 1.0104, 0.62)
        self.offset = decimalize(-0.00315, -0.00124, 0.3103)
        self.power = decimalize(1.0, 0.9983, 1.0)
        self.sat_node_desc = []
        self.sat = Decimal('1.09')

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_BLANK_METADATA))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)

#==============================================================================


class TestParseCCNoSop(TestParseCCBasic):
    """Tests parsing a cc xml with no SOP data"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.cdl_test_id = "burp_200.x15"
        self.desc = []
        self.input_desc = None
        self.viewing_desc = None

        self.sop_node_desc = []
        self.slope = decimalize(1.0, 1.0, 1.0)
        self.offset = decimalize(0.0, 0.0, 0.0)
        self.power = decimalize(1.0, 1.0, 1.0)
        self.sat_node_desc = ['I am a lovely sat node']
        self.sat = Decimal('1.01')

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_NO_SOP))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)

        # We need to call a SOP value to initialize the SOP subnode
        self.cdl.slope

#==============================================================================


class TestParseCCNoSat(TestParseCCBasic):
    """Tests parsing a cc xml with no sat data"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.cdl_test_id = "burp_300.x35"
        self.desc = []
        self.input_desc = None
        self.viewing_desc = None

        self.sop_node_desc = []
        self.slope = decimalize(0.2331, 0.678669, 1.0758)
        self.offset = decimalize(0.031, 0.128, -0.096)
        self.power = decimalize(1.8, 0.97, 0.961)
        self.sat_node_desc = []
        self.sat = Decimal('1.0')

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_NO_SAT))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)

        # We need to call a SAT value to initialize the SAT subnode
        self.cdl.sat

#==============================================================================


class TestParseCCExceptions(unittest.TestCase):
    """Tests parse_cc's response to some bad xml files"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.file = None

    #==========================================================================

    def tearDown(self):
        cdl_convert.reset_all()
        if self.file:
            os.remove(self.file)

    #==========================================================================
    # TESTS
    #==========================================================================

    def testNoId(self):
        """Tests that not finding an id attrib works"""

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_NO_ID))
            self.file = f.name

        cc = cdl_convert.parse_cc(self.file)
        self.assertEqual(
            '001',
            cc.id
        )

    #==========================================================================

    def testNotColorCorrection(self):
        """Tests that an XML with a root tag that's not ColorCorrection"""
        xml = "<ColorBlurection>\n</ColorBlurection>\n"


        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(xml))
            self.file = f.name

        self.assertRaises(
            ValueError,
            cdl_convert.parse_cc,
            self.file
        )

    #==========================================================================

    def testEmptyColorCorrection(self):
        """Tests that an empty XML raises ValueError"""
        xml = '<ColorCorrection id="hdjshd">\n</ColorCorrection>\n'

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(xml))
            self.file = f.name

        self.assertRaises(
            ValueError,
            cdl_convert.parse_cc,
            self.file
        )

    #==========================================================================

    def testBlankId(self):
        """Tests that a blank id field ValueError"""

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_BLANK_ID))
            self.file = f.name

        cdl_convert.config.HALT_ON_ERROR = True

        self.assertRaises(
            ValueError,
            cdl_convert.parse_cc,
            self.file
        )

        cdl_convert.config.HALT_ON_ERROR = False

        cdl = cdl_convert.parse_cc(self.file)

        self.assertEqual(
            '001',
            cdl.id
        )

    #==========================================================================

    def testNegativeSlope(self):
        """Tests that a negative slope raises a ValueError"""

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CC_NEGATIVE_SLOPE))
            self.file = f.name

        cdl_convert.config.HALT_ON_ERROR = True

        self.assertRaises(
            ValueError,
            cdl_convert.parse_cc,
            self.file
        )

        cdl_convert.config.HALT_ON_ERROR = False
        cdl_convert.reset_all()

        cdl = cdl_convert.parse_cc(self.file)

        self.assertEqual(
            decimalize(0.0, 0.678669, 1.0758),
            cdl.slope,
        )

# write_cc ====================================================================


class TestWriteCCFull(unittest.TestCase):
    """Tests full writing of CC XML"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()
        self.cdl = cdl_convert.ColorCorrection("014_xf_seqGrade_v01", '')
        self.cdl.desc = [
            'CC description 1', 'CC description 2', 'CC description 3',
            'CC description 4', 'CC description 5'
        ]
        self.cdl.input_desc = 'Input Desc Text'
        self.cdl.viewing_desc = 'Viewing Desc Text'

        self.cdl.slope = (1.014, 1.0104, 0.62)
        self.cdl.offset = (-0.00315, -0.00124, 0.3103)
        self.cdl.power = (1.0, 0.9983, 1.0)
        self.cdl.sop_node.desc = [
            'Sop description 1', 'Sop description 2', 'Sop description 3'
        ]

        self.cdl.sat = 1.09
        self.cdl.sat_node.desc = [
            'Sat description 1', 'Sat description 2'
        ]

        self.target_xml_root = enc(CC_FULL_WRITE)
        self.target_xml = enc('\n'.join(CC_FULL_WRITE.split('\n')[1:]))

    #==========================================================================

    def tearDown(self):
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def test_root_xml(self):
        """Tests that root_xml returns the full XML as expected"""
        self.assertEqual(
            self.target_xml_root,
            self.cdl.xml_root
        )

    #==========================================================================

    def test_base_xml(self):
        """Tests that the xml atrib returns the XML minus root as expected"""
        self.assertEqual(
            self.target_xml,
            self.cdl.xml
        )

    #==========================================================================

    def test_element(self):
        """Tests that the element returned is an etree type"""
        self.assertEqual(
            'ColorCorrection',
            self.cdl.element.tag
        )

    #==========================================================================

    def test_write(self):
        """Tests writing the cc itself"""
        mockOpen = mock.mock_open()

        self.cdl._file_out = 'bobs_big_file.cc'

        with mock.patch(builtins + '.open', mockOpen, create=True):
            cdl_convert.write_cc(self.cdl)

        mockOpen.assert_called_once_with('bobs_big_file.cc', 'wb')

        mockOpen().write.assert_called_once_with(self.target_xml_root)


class TestWriteCCOdd(TestWriteCCFull):
    """Tests odd writing of CC XML"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()
        self.cdl = cdl_convert.ColorCorrection("f55.100", '')
        self.cdl.desc = [
            'Raised saturation1 a little!?! ag... \/Offset',
            'Raised saturation2 a little!?! ag... \/Offset',
        ]
        self.cdl.input_desc = 'METAL VIEWER!!! \/\/'
        self.cdl.viewing_desc = 'WOOD VIEWER!? ////'

        self.cdl.slope = (137829.329, 4327890.9833, 3489031.003)
        self.cdl.offset = (-3424.011, -342789423.013, -4238923.11)
        self.cdl.power = (3271893.993, .0000998, 0.0000000000000000113)
        self.cdl.sop_node.desc = [
            'Raised saturation a little!?! ag... \/Offset'
        ]

        self.cdl.sat = 1798787.01
        self.cdl.sat_node.desc = []

        self.target_xml_root = enc(CC_ODD_WRITE)
        self.target_xml = enc('\n'.join(CC_ODD_WRITE.split('\n')[1:]))


class TestWriteCCNoSop(TestWriteCCFull):
    """Tests writing a CC XML with no SOP node"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()
        self.cdl = cdl_convert.ColorCorrection("burp_200.x15", '')

        self.cdl.sat = 1.0128109381
        self.cdl.sat_node.desc = ['I am a lovely sat node']

        self.target_xml_root = enc(CC_NO_SOP_WRITE)
        self.target_xml = enc('\n'.join(CC_NO_SOP_WRITE.split('\n')[1:]))


class TestWriteCCNoSat(TestWriteCCFull):
    """Tests writing a CC XML with no SAT node"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()
        self.cdl = cdl_convert.ColorCorrection("burp_300.x35", '')

        self.cdl.slope = (1.233321, 0.678669, 1.0758)
        self.cdl.offset = (0.031, 0.128, -0.096)
        self.cdl.power = (1.8, 0.97, 0.961)

        self.target_xml_root = enc(CC_NO_SAT_WRITE)
        self.target_xml = enc('\n'.join(CC_NO_SAT_WRITE.split('\n')[1:]))

#==============================================================================
# FUNCTIONS
#==============================================================================


def decimalize(*args):
    """Converts a list of floats/ints to Decimal list"""
    return tuple([Decimal(str(i)) for i in args])

#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
