from __future__ import print_function

import os
import sys


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


class NamedColors:
    """ Color codes to use for SciATH output """
    def __init__(self):
        self.set_colors()

    def set_colors(self, use_bash=True):
        self.HEADER = '\033[35m' if use_bash else ''
        self.SUBHEADER = '\033[36m' if use_bash else ''
        self.OK = '\033[32m' if use_bash else ''
        self.WARNING = '\033[93m' if use_bash else ''
        self.FAIL = '\033[91m' if use_bash else ''
        self.ENDC = '\033[0m' if use_bash else ''
