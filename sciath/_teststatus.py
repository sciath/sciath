class SciathTestStatusDefinition:

    def __init__(self, SCIATH_COLORS):
        self.status_color_type = {
            "pass": SCIATH_COLORS.OK,
            "fail": SCIATH_COLORS.FAIL,
            "skip": SCIATH_COLORS.WARNING,
            "deactivated": SCIATH_COLORS.ENDC,
        }
        self.set_status_type()

    def set_status_type(self):
        self.ok = [
            'pass',
            'verification was successful',
        ]
        self.not_ok = [
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
        self.resources_invalid_gpu = [
            'skip',
            'resource request cannot be satisifed - no GPU info provided',
        ]
        self.resources_invalid_mpiranks_per_node = [
            'skip',
            'resource request cannot be satisifed - insufficient mpiranks-per-node',
        ]
