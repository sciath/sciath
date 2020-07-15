""" Test Status definitions """
class SciathTestStatusDefinition: #pylint: disable=too-few-public-methods,too-many-instance-attributes
    """ SciATH test statuses """

    def __init__(self, SCIATH_COLORS):
        self.status_color_type = {
            "pass": SCIATH_COLORS.okay,
            "fail": SCIATH_COLORS.fail,
            "skip": SCIATH_COLORS.warning,
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

        self.job_not_run = [
            'fail',
            'test.job has not executed - sentinal file not found',
        ]
        self.file_not_found = [
            'fail',
            'file not found',
        ]

        self.expected_file_not_found = [
            'fail',
            'expected/comparison file not found',
        ]
        self.expected_file_incomplete = [
            'fail',
            'problem with expected/comparison file',
        ]
        self.expected_file_missing_key = [
            'fail',
            'expected/comparison file missing key',
        ]
        self.expected_file_wrong_value = [
            'fail',
            'expected/comparison file contains wrong (key,value) pair',
        ]

        self.output_file_not_found = [
            'fail',
            'output file not found',
        ]
        self.output_file_missing_key = [
            'fail',
            'output file missing key',
        ]
        self.output_file_wrong_value = [
            'fail',
            'output file contains wrong (key,value) pair',
        ]

        self.resources_invalid = [
            'skip',
            'resource request cannot be satisifed',
        ]
        self.resources_invalid_mpi = [
            'skip',
            'resource request cannot be satisifed - no MPI exec provided',
        ]
