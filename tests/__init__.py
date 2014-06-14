#!/usr/bin/env python
"""Collects all the various tests into one big test suite"""

from test_cdl_convert import *
from test_classes import *
from test_ale import *
from test_cc import *
from test_ccc import *
from test_cdl import *
from test_flex import *
from test_rnh_cdl import *


if __name__ == '__main__':
    unittest.main()

