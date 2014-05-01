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

# We'll save out different and broken XMLs by hand.

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

CC_BASIC_ODD = r"""<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrection id="f55.100">
    <Description>Raised saturation a little!?! ag... \/Offset</Description>
    <Description>Raised saturation a little!?! ag... \/Offset</Description>
    <InputDescription>METAL VIEWER!!! \/\/</InputDescription>
    <ViewingDescription>WOOD VIEWER!? \\\\////</ViewingDescription>
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
    </ASC_SATe>
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

'''
class TestParseCCBasic(unittest.TestCase):
    """Tests parsing a cc xml"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope = (1.329, 0.9833, 1.003)
        self.offset = (0.011, 0.013, 0.11)
        self.power = (.993, .998, 1.0113)
        self.sat = 1.01
        self.id = 'cc23678'
        self.desc = "Raised saturation a little, adjusted gamma"

        self.file = buildCC(self.id, self.desc, self.slope, self.offset,
                            self.power, self.sat)

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)[0]

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
        """Tests that id was set to id attrib"""
        self.assertEqual(
            self.id,
            self.cdl.id
        )

    #==========================================================================

    def testDesc(self):
        """Tests that desc was set to desc element"""
        self.assertEqual(
            [self.desc, ],
            self.cdl.desc
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


class TestParseCCOdd(TestParseCCBasic):
    """Tests parsing a cc xml with odd values"""

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
        self.id = 'cc23678_who_what_where.period_are__cool__so_is_youz66867868'
        # Note that including < in desc WILL break XML parsing. We should
        # probably have a function that sanitizes those type of fields
        # when we write to XML
        self.desc = r"Raised saturation a little!?! adjusted gamma... \/Offset"

        self.file = buildCC(self.id, self.desc, self.slope, self.offset,
                            self.power, self.sat)

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)[0]


class TestParseCCJustSat(TestParseCCBasic):
    """Tests parsing a cc xml with no SOP values"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.sat = 1.01
        self.id = 'cc23678'
        self.desc = "Raised saturation a little, adjusted gamma"

        self.file = buildCC(self.id, self.desc, sat=self.sat)

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)[0]

    #==========================================================================
    # TESTS
    #==========================================================================

    def testSlope(self):
        """Tests that slope is still at defaults"""
        self.assertEqual(
            (1.0, 1.0, 1.0),
            self.cdl.slope
        )

    #==========================================================================

    def testOffset(self):
        """Tests that offset is still at defaults"""
        self.assertEqual(
            (0.0, 0.0, 0.0),
            self.cdl.offset
        )

    #==========================================================================

    def testPower(self):
        """Tests that power is still at defaults"""
        self.assertEqual(
            (1.0, 1.0, 1.0),
            self.cdl.power
        )


class TestParseCCJustSOP(TestParseCCBasic):
    """Tests parsing a cc xml with no sat value"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope = (1.329, 0.9833, 1.003)
        self.offset = (0.011, 0.013, 0.11)
        self.power = (.993, .998, 1.0113)
        self.id = 'cc23678'
        self.desc = "Raised saturation a little, adjusted gamma"

        self.file = buildCC(self.id, self.desc, self.slope, self.offset,
                            self.power)

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)[0]

    #==========================================================================
    # TESTS
    #==========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        self.assertEqual(
            1.0,
            self.cdl.sat
        )


class TestParseCCNoSlope(TestParseCCBasic):
    """Tests parsing a cc xml with no slope value"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.offset = (0.011, 0.013, 0.11)
        self.power = (.993, .998, 1.0113)
        self.sat = 1.23
        self.id = 'cc23678'
        self.desc = "Raised saturation a little, adjusted gamma"

        self.file = buildCC(self.id, self.desc, offset=self.offset,
                            power=self.power, sat=self.sat)

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)[0]

    #==========================================================================
    # TESTS
    #==========================================================================

    def testSlope(self):
        """Tests that slope is still at default"""
        self.assertEqual(
            (1.0, 1.0, 1.0),
            self.cdl.slope
        )


class TestParseCCNoOffset(TestParseCCBasic):
    """Tests parsing a cc xml with no offset value"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope = (0.011, 0.013, 0.11)
        self.power = (.993, .998, 1.0113)
        self.sat = 1.23
        self.id = 'cc23678'
        self.desc = "Raised saturation a little, adjusted gamma"

        self.file = buildCC(self.id, self.desc, slope=self.slope,
                            power=self.power, sat=self.sat)

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)[0]

    #==========================================================================
    # TESTS
    #==========================================================================

    def testOffset(self):
        """Tests that offset is still at default"""
        self.assertEqual(
            (0.0, 0.0, 0.0),
            self.cdl.offset
        )


class TestParseCCNoPower(TestParseCCBasic):
    """Tests parsing a cc xml with no power value"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.slope = (.993, .998, 1.0113)
        self.offset = (0.011, 0.013, 0.11)
        self.sat = 1.23
        self.id = 'cc23678'
        self.desc = "Raised saturation a little, adjusted gamma"

        self.file = buildCC(self.id, self.desc, offset=self.offset,
                            slope=self.slope, sat=self.sat)

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)[0]

    #==========================================================================
    # TESTS
    #==========================================================================

    def testPower(self):
        """Tests that power is still at defaults"""
        self.assertEqual(
            (1.0, 1.0, 1.0),
            self.cdl.power
        )


class TestParseCCEmptyElems(TestParseCCBasic):
    """Tests parsing a cc xml with empty SOP and Sat nodes"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.id = 'cc23678'
        self.desc = "Raised saturation a little, adjusted gamma"

        self.file = buildCC(self.id, self.desc, emptySop=True, emptySat=True)

        # Build our cc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(self.file))
            self.filename = f.name

        self.cdl = cdl_convert.parse_cc(self.filename)[0]

    #==========================================================================
    # TESTS
    #==========================================================================

    def testSlope(self):
        """Tests that slope is still at defaults"""
        self.assertEqual(
            (1.0, 1.0, 1.0),
            self.cdl.slope
        )

    #==========================================================================

    def testOffset(self):
        """Tests that offset is still at defaults"""
        self.assertEqual(
            (0.0, 0.0, 0.0),
            self.cdl.offset
        )

    #==========================================================================

    def testPower(self):
        """Tests that power is still at defaults"""
        self.assertEqual(
            (1.0, 1.0, 1.0),
            self.cdl.power
        )

    #==========================================================================

    def testSat(self):
        """Tests that sat was set correctly"""
        self.assertEqual(
            1.0,
            self.cdl.sat
        )


class TestParseCCExceptions(unittest.TestCase):
    """Tests parse_cc's response to some bad xml files"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.file = None

    #==========================================================================

    def tearDown(self):
        if self.file:
            os.remove(self.file)

    #==========================================================================
    # TESTS
    #==========================================================================

    def testNoId(self):
        """Tests that not finding an id attrib raises ValueError"""
        xml = buildCC(emptySop=True, emptySat=True)

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

    def testBadXML(self):
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
'''
#==============================================================================
# FUNCTIONS
#==============================================================================


#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
