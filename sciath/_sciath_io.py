""" SciATH logic and definitions for input and output """
from __future__ import print_function

import os
import sys
from sciath import SCIATH_COLORS


def py23input(prompt):
    """ Returns user input, as Python 3 input() """
    if sys.version_info[0] == 2:
        user_input = raw_input(prompt)  # pylint: disable=undefined-variable
    else:
        user_input = input(prompt)
    return user_input


def _remove_file_if_it_exists(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def command_join(command):
    """ Converts a command (as for subprocess.run()) to a copy-pasteable string

    Do something similar to shlex.join (Python 3.8+), attempting to quote arguments
    that contain spaces, and escape newlines in the result. """

    joined = ' '.join(
        ["'" + term + "'" if ' ' in term else term for term in command])
    joined = joined.replace('\n', '\\n')
    return joined


# Functions which color strings
def color_error(string):
    """ Colors a string as an error """
    return "%s%s%s" % (SCIATH_COLORS.error, string, SCIATH_COLORS.endc)


def color_fail(string):
    """ Colors a string as a failure """
    return "%s%s%s" % (SCIATH_COLORS.fail, string, SCIATH_COLORS.endc)


def color_header(string):
    """ Colors a string as a SciATH header """
    return "%s%s%s" % (SCIATH_COLORS.header, string, SCIATH_COLORS.endc)


def color_info(string):
    """ Colors a string as SciATH info """
    return string


def color_okay(string):
    """ Colors a string as okay """
    return "%s%s%s" % (SCIATH_COLORS.okay, string, SCIATH_COLORS.endc)


def color_subheader(string):
    """ Colors a string as a SciATH subheader """
    return "%s%s%s" % (SCIATH_COLORS.subheader, string, SCIATH_COLORS.endc)


def color_warning(string):
    """ Colors a string as a warning """
    return "%s%s%s" % (SCIATH_COLORS.warning, string, SCIATH_COLORS.endc)


# Functions which format strings
def format_error(string):
    """ Formats a string as a SciATH error """
    return color_error("[SciATH] Error: %s" % string)


def format_header(string):
    """ Formats a string as a SciATH header """
    return color_header("[*** %s ***]" % string)


def format_info(string):
    """ Formats a string as SciATH info """
    return color_info("[SciATH] %s" % string)


def format_subheader(string):
    """ Formats a string as a SciATH subheader """
    return color_subheader("[%s]" % string)


def format_warning(string):
    """ Formats a string as a SciATH warning """
    return color_warning("[SciATH] Warning: %s" % string)


# Functions which format and print strings
def print_error(string, **kwargs):
    """ Prints a string as a SciATH error """
    print(format_error(string), **kwargs)


def print_info(string, **kwargs):
    """ Prints a string as SciATH information """
    print(format_info(string), **kwargs)


def print_header(string, **kwargs):
    """ Prints a string as a SciATH header """
    print(format_header(string), **kwargs)


def print_subheader(string, **kwargs):
    """ Prints a string as a SciATH subheader """
    print(format_subheader(string), **kwargs)


def print_warning(string, **kwargs):
    """ Prints a string as a SciATH warning """
    print(format_warning(string), **kwargs)
