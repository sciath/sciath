import os
import sys
import argparse
import numpy as np
import math as math
import re

import sciath
from sciath._io import NamedColors

def getVersion() :
  """
  Returns major,minor,patch version as integers
  """
  return 0,4,4

__version__ = getVersion()

# A default set of colors
sciath_colors = NamedColors()

def default_colors_set_use_bash(use_bash):
    sciath.sciath_colors = NamedColors(use_bash)
