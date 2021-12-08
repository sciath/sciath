""" SciATH: Scientific Application Test Harness """
from sciath._sciath_colors import NamedColors

__version__ = (0, 13, 0)

# A default set of colors
SCIATH_COLORS = NamedColors()


def no_colors():
    """ Deactivate text coloring """
    SCIATH_COLORS.set_colors(use_bash=False)
