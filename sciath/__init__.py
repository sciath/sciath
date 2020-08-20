""" SciATH: Scientific Application Test Harness """
from sciath._sciath_io import NamedColors

def version():
    """ Return major, minor, patch version as integers """
    return 0, 6, 0

__version__ = version()

# A default set of colors
SCIATH_COLORS = NamedColors()
