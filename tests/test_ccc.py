#!/usr/bin/env python
"""
Tests the ccc related functions of cdl_convert

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

# parse_ccc ===================================================================

CCC_FULL = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrectionCollection xmlns="urn:ASC:CDL:v1.01">
    <Description>CCC description 1</Description>
    <InputDescription>CCC Input Desc Text</InputDescription>
    <Description>CCC description 2</Description>
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
    <ColorCorrection id="f55.100">
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
    <Description>CCC description 3</Description>
    <ViewingDescription>CCC Viewing Desc Text</ViewingDescription>
    <Description>CCC description 4</Description>
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
    <ColorCorrection id="burp_200.x15">
        <SatNode>
            <Description>I am a lovely sat node</Description>
            <Saturation>1.01</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="burp_300.x35">
        <SopNode>
            <Slope>0.2331 0.678669 1.0758</Slope>
            <Offset>0.031 0.128 -0.096</Offset>
            <Power>1.8 0.97 0.961</Power>
        </SopNode>
    </ColorCorrection>
</ColorCorrectionCollection>
"""

CCC_ODD = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrectionCollection>
    <Description></Description>
    <InputDescription></InputDescription>
    <Description>CCC description 1</Description>
    <Description></Description>
    <Description></Description>
    <Description></Description>
    <ColorCorrection id="014_xf_seqGrade_v01">
        <SOPNode>
            <Description>Sop description 1</Description>
            <Description>Sop description 2</Description>
            <Slope>1.014 1.0104 0.62</Slope>
            <Offset>-0.00315 -0.00124 0.3103</Offset>
            <Power>1.0 0.9983 1.0</Power>
            <Description>Sop description 3</Description>
        </SOPNode>
    </ColorCorrection>
    <ColorCorrection id="f51.200">
        <SopNode>
            <Slope>0.2331 0.678669 1.0758</Slope>
            <Offset>0.031 0.128 -0.096</Offset>
            <Power>1.8 0.97 0.961</Power>
        </SopNode>
    </ColorCorrection>
    <Description>Raised1 saturation a little!?! ag... \/Offset</Description>
    <Description>Raised2 saturation a little!?! ag... \/Offset</Description>
    <ColorCorrection id="f55.100">
        <SatNode>
            <Saturation>1798787.01</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="f54.112">
        <ASC_SAT>
            <Saturation>1.01</Saturation>
        </ASC_SAT>
    </ColorCorrection>
    <ViewingDescription></ViewingDescription>
    <ColorCorrection id="burp_200.x15">
        <SatNode>
            <Description>I am a lovely sat node</Description>
            <Saturation>1.01</Saturation>
        </SatNode>
    </ColorCorrection>
</ColorCorrectionCollection>
"""

# write_ccc ===================================================================

CCC_FULL_WRITE = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrectionCollection xmlns="urn:ASC:CDL:v1.01">
    <InputDescription>CCC Input Desc Text</InputDescription>
    <ViewingDescription>CCC Viewing Desc Text</ViewingDescription>
    <Description>CCC description 1</Description>
    <Description>CCC description 2</Description>
    <Description>CCC description 3</Description>
    <Description>CCC description 4</Description>
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
        <SatNode>
            <Description>Sat description 1</Description>
            <Description>Sat description 2</Description>
            <Saturation>1.09</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="f51.200">
        <SOPNode>
            <Slope>0.2331 0.678669 1.0758</Slope>
            <Offset>0.031 0.128 -0.096</Offset>
            <Power>1.8 0.97 0.961</Power>
        </SOPNode>
        <SatNode>
            <Saturation>1.01</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="f55.100">
        <InputDescription>METAL VIEWER!!! \/\/</InputDescription>
        <ViewingDescription>WOOD VIEWER!? ////</ViewingDescription>
        <Description>Raised saturation a little!?! ag... \/Offset</Description>
        <Description>Raised saturation a little!?! ag... \/Offset</Description>
        <SOPNode>
            <Description>Raised saturation a little!?! ag... \/Offset</Description>
            <Slope>137829.329 4327890.9833 3489031.003</Slope>
            <Offset>-3424.011 -342789423.013 -4238923.11</Offset>
            <Power>3271893.993 0.0000998 0.0000000000000000113</Power>
        </SOPNode>
        <SatNode>
            <Saturation>1798787.01</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="f54.112">
        <SOPNode>
            <Slope>0.2331 0.678669 1.0758</Slope>
            <Offset>0.031 0.128 -0.096</Offset>
            <Power>1.8 0.97 0.961</Power>
        </SOPNode>
        <SatNode>
            <Saturation>1.01</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="burp_100.x12">
        <SOPNode>
            <Slope>1.014 1.0104 0.62</Slope>
            <Offset>-0.00315 -0.00124 0.3103</Offset>
            <Power>1.0 0.9983 1.0</Power>
        </SOPNode>
        <SatNode>
            <Saturation>1.09</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="burp_200.x15">
        <SatNode>
            <Description>I am a lovely sat node</Description>
            <Saturation>1.01</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="burp_300.x35">
        <SOPNode>
            <Slope>0.2331 0.678669 1.0758</Slope>
            <Offset>0.031 0.128 -0.096</Offset>
            <Power>1.8 0.97 0.961</Power>
        </SOPNode>
    </ColorCorrection>
</ColorCorrectionCollection>
"""

CCC_FULL_WRITE_CDL = """<?xml version="1.0" encoding="UTF-8"?>
<ColorDecisionList xmlns="urn:ASC:CDL:v1.01">
    <InputDescription>CCC Input Desc Text</InputDescription>
    <ViewingDescription>CCC Viewing Desc Text</ViewingDescription>
    <Description>CCC description 1</Description>
    <Description>CCC description 2</Description>
    <Description>CCC description 3</Description>
    <Description>CCC description 4</Description>
    <ColorDecision>
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
            <SatNode>
                <Description>Sat description 1</Description>
                <Description>Sat description 2</Description>
                <Saturation>1.09</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="f51.200">
            <SOPNode>
                <Slope>0.2331 0.678669 1.0758</Slope>
                <Offset>0.031 0.128 -0.096</Offset>
                <Power>1.8 0.97 0.961</Power>
            </SOPNode>
            <SatNode>
                <Saturation>1.01</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="f55.100">
            <InputDescription>METAL VIEWER!!! \/\/</InputDescription>
            <ViewingDescription>WOOD VIEWER!? ////</ViewingDescription>
            <Description>Raised saturation a little!?! ag... \/Offset</Description>
            <Description>Raised saturation a little!?! ag... \/Offset</Description>
            <SOPNode>
                <Description>Raised saturation a little!?! ag... \/Offset</Description>
                <Slope>137829.329 4327890.9833 3489031.003</Slope>
                <Offset>-3424.011 -342789423.013 -4238923.11</Offset>
                <Power>3271893.993 0.0000998 0.0000000000000000113</Power>
            </SOPNode>
            <SatNode>
                <Saturation>1798787.01</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="f54.112">
            <SOPNode>
                <Slope>0.2331 0.678669 1.0758</Slope>
                <Offset>0.031 0.128 -0.096</Offset>
                <Power>1.8 0.97 0.961</Power>
            </SOPNode>
            <SatNode>
                <Saturation>1.01</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="burp_100.x12">
            <SOPNode>
                <Slope>1.014 1.0104 0.62</Slope>
                <Offset>-0.00315 -0.00124 0.3103</Offset>
                <Power>1.0 0.9983 1.0</Power>
            </SOPNode>
            <SatNode>
                <Saturation>1.09</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="burp_200.x15">
            <SatNode>
                <Description>I am a lovely sat node</Description>
                <Saturation>1.01</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="burp_300.x35">
            <SOPNode>
                <Slope>0.2331 0.678669 1.0758</Slope>
                <Offset>0.031 0.128 -0.096</Offset>
                <Power>1.8 0.97 0.961</Power>
            </SOPNode>
        </ColorCorrection>
    </ColorDecision>
</ColorDecisionList>
"""

CCC_ODD_WRITE = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrectionCollection xmlns="urn:ASC:CDL:v1.01">
    <Description>CCC description 1</Description>
    <Description>Raised1 saturation a little!?! ag... \/Offset</Description>
    <Description>Raised2 saturation a little!?! ag... \/Offset</Description>
    <ColorCorrection id="014_xf_seqGrade_v01">
        <SOPNode>
            <Description>Sop description 1</Description>
            <Description>Sop description 2</Description>
            <Description>Sop description 3</Description>
            <Slope>1.014 1.0104 0.62</Slope>
            <Offset>-0.00315 -0.00124 0.3103</Offset>
            <Power>1.0 0.9983 1.0</Power>
        </SOPNode>
    </ColorCorrection>
    <ColorCorrection id="f51.200">
        <SOPNode>
            <Slope>0.2331 0.678669 1.0758</Slope>
            <Offset>0.031 0.128 -0.096</Offset>
            <Power>1.8 0.97 0.961</Power>
        </SOPNode>
    </ColorCorrection>
    <ColorCorrection id="f55.100">
        <SatNode>
            <Saturation>1798787.01</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="f54.112">
        <SatNode>
            <Saturation>1.01</Saturation>
        </SatNode>
    </ColorCorrection>
    <ColorCorrection id="burp_200.x15">
        <SatNode>
            <Description>I am a lovely sat node</Description>
            <Saturation>1.01</Saturation>
        </SatNode>
    </ColorCorrection>
</ColorCorrectionCollection>
"""

CCC_ODD_WRITE_CDL = """<?xml version="1.0" encoding="UTF-8"?>
<ColorDecisionList xmlns="urn:ASC:CDL:v1.01">
    <Description>CCC description 1</Description>
    <Description>Raised1 saturation a little!?! ag... \/Offset</Description>
    <Description>Raised2 saturation a little!?! ag... \/Offset</Description>
    <ColorDecision>
        <ColorCorrection id="014_xf_seqGrade_v01">
            <SOPNode>
                <Description>Sop description 1</Description>
                <Description>Sop description 2</Description>
                <Description>Sop description 3</Description>
                <Slope>1.014 1.0104 0.62</Slope>
                <Offset>-0.00315 -0.00124 0.3103</Offset>
                <Power>1.0 0.9983 1.0</Power>
            </SOPNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="f51.200">
            <SOPNode>
                <Slope>0.2331 0.678669 1.0758</Slope>
                <Offset>0.031 0.128 -0.096</Offset>
                <Power>1.8 0.97 0.961</Power>
            </SOPNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="f55.100">
            <SatNode>
                <Saturation>1798787.01</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="f54.112">
            <SatNode>
                <Saturation>1.01</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
    <ColorDecision>
        <ColorCorrection id="burp_200.x15">
            <SatNode>
                <Description>I am a lovely sat node</Description>
                <Saturation>1.01</Saturation>
            </SatNode>
        </ColorCorrection>
    </ColorDecision>
</ColorDecisionList>
"""

CCC_BAD_TAG = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrectionBollection xmlns="urn:ASC:CDL:v1.01">
    <Description>CCC description 1</Description>
    <Description>Raised1 saturation a little!?! ag... \/Offset</Description>
    <Description>Raised2 saturation a little!?! ag... \/Offset</Description>
    <ColorCorrection id="014_xf_seqGrade_v01">
        <SOPNode>
            <Description>Sop description 1</Description>
            <Description>Sop description 2</Description>
            <Description>Sop description 3</Description>
            <Slope>1.014 1.0104 0.62</Slope>
            <Offset>-0.00315 -0.00124 0.3103</Offset>
            <Power>1.0 0.9983 1.0</Power>
        </SOPNode>
    </ColorCorrection>
    <ColorCorrection id="f51.200">
        <SOPNode>
            <Slope>0.2331 0.678669 1.0758</Slope>
            <Offset>0.031 0.128 -0.096</Offset>
            <Power>1.8 0.97 0.961</Power>
        </SOPNode>
    </ColorCorrection>
    <ColorCorrection id="f55.100">
        <SATNode>
            <Saturation>1798787.01</Saturation>
        </SATNode>
    </ColorCorrection>
    <ColorCorrection id="f54.112">
        <SATNode>
            <Saturation>1.01</Saturation>
        </SATNode>
    </ColorCorrection>
    <ColorCorrection id="burp_200.x15">
        <SATNode>
            <Description>I am a lovely sat node</Description>
            <Saturation>1.01</Saturation>
        </SATNode>
    </ColorCorrection>
</ColorCorrectionBollection>
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


class TestParseCCCFull(unittest.TestCase):
    """Tests a full CCC parse"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.desc = [
            'CCC description 1',
            'CCC description 2',
            'CCC description 3',
            'CCC description 4'
        ]
        self.input_desc = 'CCC Input Desc Text'
        self.viewing_desc = 'CCC Viewing Desc Text'
        self.color_correction_ids = [
            '014_xf_seqGrade_v01',
            'f51.200',
            'f55.100',
            'f54.112',
            'burp_100.x12',
            'burp_200.x15',
            'burp_300.x35'
        ]

        # Build our ccc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CCC_FULL))
            self.filename = f.name

        self.node = cdl_convert.parse_ccc(self.filename)

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

    def test_file_in(self):
        """Tests that the input_file has been set to the file in value"""
        self.assertEqual(
            self.filename,
            self.node.file_in
        )

    #==========================================================================

    def test_type(self):
        """Makes sure type is still set to ccc"""
        self.assertEqual(
            'ccc',
            self.node.type
        )

    #==========================================================================

    def test_descs(self):
        """Tests that the desc fields have been set correctly"""
        self.assertEqual(
            self.desc,
            self.node.desc
        )

    #==========================================================================

    def test_viewing_desc(self):
        """Tests that the viewing desc has been set correctly"""
        self.assertEqual(
            self.viewing_desc,
            self.node.viewing_desc
        )

    #==========================================================================

    def test_input_desc(self):
        """Tests that the input desc has been set correctly"""
        self.assertEqual(
            self.input_desc,
            self.node.input_desc
        )

    #==========================================================================

    def test_parse_results(self):
        """Tests that the parser picked up all the cc's"""
        id_list = [i.id for i in self.node.color_corrections]
        self.assertEqual(
            self.color_correction_ids,
            id_list
        )


class TestParseCCCOdd(TestParseCCCFull):
    """Tests an odd CCC parse"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.desc = [
            'CCC description 1',
            'Raised1 saturation a little!?! ag... \/Offset',
            'Raised2 saturation a little!?! ag... \/Offset',
        ]
        self.input_desc = None
        self.viewing_desc = None
        self.color_correction_ids = [
            '014_xf_seqGrade_v01',
            'f51.200',
            'f55.100',
            'f54.112',
            'burp_200.x15',
        ]

        # Build our ccc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CCC_ODD))
            self.filename = f.name

        self.node = cdl_convert.parse_ccc(self.filename)


class TestParseCCCExceptions(unittest.TestCase):
    """Tests that we run into the correct exceptions with bad XMLs"""

    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        self.filename = None

    def tearDown(self):
        if self.filename:
            os.remove(self.filename)
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def testBadTag(self):
        """Tests that a bad root tag raises a ValueError"""

        # Build our ccc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CCC_BAD_TAG))
            self.filename = f.name

        self.assertRaises(
            ValueError,
            cdl_convert.parse_ccc,
            self.filename,
        )

    #==========================================================================

    def testEmptyCCC(self):
        """Tests that an empty CCC file raises a ValueError"""

        emptyCCC = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<ColorCorrectionCollection xmlns="urn:ASC:CDL:v1.01">\n'
                    '</ColorCorrectionCollection>')

        # Build our ccc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(emptyCCC))
            self.filename = f.name

        self.assertRaises(
            ValueError,
            cdl_convert.parse_ccc,
            self.filename,
        )


class TestWriteCCCFull(unittest.TestCase):
    """Tests a full write of the CCC file

    This is an integration style test. If parse_ccc stops working, this stops
    working.

    """
    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Build our ccc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CCC_FULL))
            self.filename = f.name

        self.ccc = cdl_convert.parse_ccc(self.filename)

        self.target_xml_root = enc(CCC_FULL_WRITE)
        self.target_xml = enc('\n'.join(CCC_FULL_WRITE.split('\n')[1:]))

    #==========================================================================

    def tearDown(self):
        os.remove(self.filename)
        cdl_convert.reset_all()

    #==========================================================================
    # TESTS
    #==========================================================================

    def test_root_xml(self):
        """Tests that root_xml returns the full XML as expected"""
        self.assertEqual(
            self.target_xml_root,
            self.ccc.xml_root
        )

    #==========================================================================

    def test_base_xml(self):
        """Tests that the xml atrib returns the XML minus root as expected"""
        self.assertEqual(
            self.target_xml,
            self.ccc.xml
        )

    #==========================================================================

    def test_element(self):
        """Tests that the element returned is an etree type"""
        self.assertEqual(
            'ColorCorrectionCollection',
            self.ccc.element.tag
        )

    #==========================================================================

    def test_write(self):
        """Tests writing the ccc itself"""
        mockOpen = mock.mock_open()

        self.ccc._file_out = 'bobs_big_file.ccc'

        with mock.patch(builtins + '.open', mockOpen, create=True):
            cdl_convert.write_ccc(self.ccc)

        mockOpen.assert_called_once_with('bobs_big_file.ccc', 'wb')

        mockOpen().write.assert_called_once_with(self.target_xml_root)


class TestWriteCCCFullAsCDL(TestWriteCCCFull):
    """Tests a full write of the CCC file as a CDL

    This is an integration style test. If parse_ccc stops working, this stops
    working.

    """
    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Build our ccc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CCC_FULL))
            self.filename = f.name

        self.ccc = cdl_convert.parse_ccc(self.filename)
        self.ccc.set_to_cdl()

        self.target_xml_root = enc(CCC_FULL_WRITE_CDL)
        self.target_xml = enc('\n'.join(CCC_FULL_WRITE_CDL.split('\n')[1:]))

    #==========================================================================

    def test_element(self):
        """Tests that the element returned is an etree type"""
        self.assertEqual(
            'ColorDecisionList',
            self.ccc.element.tag
        )

    #==========================================================================

    def test_write(self):
        """Tests writing the ccc itself"""
        mockOpen = mock.mock_open()

        self.ccc._file_out = 'bobs_big_file.cdl'

        with mock.patch(builtins + '.open', mockOpen, create=True):
            cdl_convert.write_cdl(self.ccc)

        mockOpen.assert_called_once_with('bobs_big_file.cdl', 'wb')

        mockOpen().write.assert_called_once_with(self.target_xml_root)


class TestWriteCCCOdd(TestWriteCCCFull):
    """Tests an odd write of the CCC file

    This is an integration style test. If parse_ccc stops working, this stops
    working.

    """
    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        cdl_convert.reset_all()

        # Build our ccc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CCC_ODD))
            self.filename = f.name

        self.ccc = cdl_convert.parse_ccc(self.filename)

        self.target_xml_root = enc(CCC_ODD_WRITE)
        self.target_xml = enc('\n'.join(CCC_ODD_WRITE.split('\n')[1:]))


class TestWriteCCCOddAsCDL(TestWriteCCCFullAsCDL):
    """Tests a full write of the CCC file as a CDL

    This is an integration style test. If parse_ccc stops working, this stops
    working.

    """
    #==========================================================================
    # SETUP & TEARDOWN
    #==========================================================================

    def setUp(self):
        # Build our ccc
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(enc(CCC_ODD))
            self.filename = f.name

        self.ccc = cdl_convert.parse_ccc(self.filename)
        self.ccc.set_to_cdl()

        self.target_xml_root = enc(CCC_ODD_WRITE_CDL)
        self.target_xml = enc('\n'.join(CCC_ODD_WRITE_CDL.split('\n')[1:]))

#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
