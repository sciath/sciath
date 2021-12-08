""" SciATH colors for printing """


class NamedColors:  #pylint: disable=too-few-public-methods
    """ Color codes to use for SciATH output """

    def __init__(self):
        self.set_colors()

    def set_colors(self, use_bash=True):
        """ Set color codes, based on whether or not bash colors are used """
        self.header = '\033[35m' if use_bash else ''
        self.subheader = '\033[36m' if use_bash else ''
        self.okay = '\033[32m' if use_bash else ''
        self.warning = '\033[33m' if use_bash else ''
        self.error = '\033[91m' if use_bash else ''
        self.fail = '\033[91m' if use_bash else ''
        self.endc = '\033[0m' if use_bash else ''
