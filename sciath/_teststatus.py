# TODO this whole thing needs to go! (see notes)
""" Test Status definitions """
class SciathTestStatusDefinition: #pylint: disable=too-few-public-methods,too-many-instance-attributes
    """ SciATH test statuses """

    def __init__(self, SCIATH_COLORS):
        self.status_color_type = {
            "pass": SCIATH_COLORS.okay,
            "fail": SCIATH_COLORS.fail,
            "skip": SCIATH_COLORS.warning,
            "incomplete": SCIATH_COLORS.warning,
            "not launched": SCIATH_COLORS.warning,
            "deactivated": SCIATH_COLORS.endc,
        }
        self._set_status_type()

    def _set_status_type(self):
        self.okay = [
            'pass',
            'verification was successful',
        ]
        self.not_okay = [
            'fail',
            'verification failed',
        ]
        self.expected_file_not_found = [
            'fail',
            'expected/comparison file not found',
        ]

        self.output_file_not_found = [
            'fail',
            'output file not found',
        ]
