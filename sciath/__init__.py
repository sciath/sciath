import os
import sys
import argparse
import math as math
import re

import sciath
from sciath._sciath_io import NamedColors
from sciath._teststatus import SciathTestStatusDefinition

def getVersion() :
    """ Returns major, minor, patch version as integers """
    return 0, 6, 0

__version__ = getVersion()

# A default set of colors
sciath_colors = NamedColors()

# Default codes/status/message/colors for test verification
sciath_test_status = SciathTestStatusDefinition(sciath_colors)
