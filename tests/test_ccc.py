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

import cdl_convert.cdl_convert as cdl_convert

#==============================================================================
# GLOBALS
#==============================================================================

CCC_FULL = """<?xml version="1.0" encoding="UTF-8"?>
<ColorCorrectionCollection>
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

#==============================================================================
# RUNNER
#==============================================================================
if __name__ == '__main__':
    unittest.main()
