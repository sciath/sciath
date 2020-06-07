

class SciathTestStatusDefinition:
    def __init__(self,sciath_colors):
        self.status_color_type = {
            "pass" : sciath_colors.OK,
            "fail" : sciath_colors.FAIL,
            "warn" : sciath_colors.WARNING,
            "skip" : sciath_colors.WARNING,
            "deactivated" : sciath_colors.ENDC, }
        self.set_status_type()

    def set_status_type(self):
        self.ok     = [ 'pass' , 'verification was successful' ]
        self.not_ok = [ 'fail' , 'verification failed' ]

        self.job_not_run              = [ 'fail' , 'test.job has not executed - sentinal file not found' ]
        self.file_not_found           = [ 'fail' , 'file not found' ]
        self.dependent_job_failed     = [ 'warn' , 'test passed, at least one dependent job returned non-success error code' ]
        self.parent_and_depjob_failed = [ 'fail' , 'test failed, at least one dependent one failed' ]

        self.expected_file_not_found   = [ 'fail' , 'expected/comparison file not found' ]
        self.expected_file_incomplete  = [ 'fail' , 'problem with expected/comparison file' ]
        self.expected_file_missing_key = [ 'fail' , 'expected/comparison file missing key' ]
        self.expected_file_wrong_value = [ 'fail' , 'expected/comparison file contains wrong (key,value) pair' ]

        self.output_file_not_found   = [ 'fail' , 'output file not found' ]
        self.output_file_missing_key = [ 'fail' , 'output file missing key' ]
        self.output_file_wrong_value = [ 'fail' , 'output file contains wrong (key,value) pair' ]

        self.resources_invalid     = [ 'skip' , 'resource request cannot be satisifed' ]
        self.resources_invalid_mpi = [ 'skip' , 'resource request cannot be satisifed - no MPI exec provided' ]
        self.resources_invalid_gpu = [ 'skip' , 'resource request cannot be satisifed - no GPU info provided' ]
        self.resources_invalid_mpiranks_per_node = [ 'skip' , 'resource request cannot be satisifed - insufficient mpiranks-per-node' ]
