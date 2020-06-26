""" SciATH Verifier class """
from __future__ import print_function

import os
import filecmp
import difflib
import shutil
import errno

from sciath import SCIATH_TEST_STATUS


class Verifier(object):  # pylint: disable=bad-option-value,too-few-public-methods,useless-object-inheritance
    """Base class for verification of a Test"""

    def __init__(self, test):
        self.test = test

    def execute(self, output_path, exec_path=None):
        """ Relative to a given output path, fetch file(s) and produce status,report

            Accepts an output path (where the Launcher puts the files it generates)
            and an execution path (where the Job was run from). Either might be
            required for verification: for instance, to check the error code
            collected by the Launcher, one needs the output path, and to compare
            with an output file generated by an executable, one needs the execution
            path.
        """
        raise NotImplementedError("Verifier implementations must override execute()")


class ExitCodeVerifier(Verifier):
    """ Verifier implementation which checks exit codes """

    def __init__(self, test):
        super(ExitCodeVerifier, self).__init__(test)
        self.exit_codes_success = [0] * test.job.number_tasks()

    def execute(self, output_path, exec_path=None):
        """ Relative to a given output path, fetch file(s) and produce status,report """

        status = None
        report = []

        exit_code_name = self.test.job.get_output_filenames()[0]

        exit_code_file = os.path.join(output_path, exit_code_name)
        if not os.path.isfile(exit_code_file):
            report.append("[ReturnCodeDiff] File (" + exit_code_file + ") not found")
            status = SCIATH_TEST_STATUS.job_not_run
            return status, report

        with open(exit_code_file, 'r') as handle:
            exit_codes = [int(line) for line in handle.readlines()]

        if exit_codes != self.exit_codes_success:
            report.append("[ExitCodeDiff] Expected exit code(s): " + str(self.exit_codes_success))
            report.append("[ExitCodeDiff] Output exit code(s)  : " + str(exit_codes))
            status = SCIATH_TEST_STATUS.not_ok
        else:
            status = SCIATH_TEST_STATUS.ok
        return status, report

    def set_exit_codes_success(self, exit_codes_success):
        """ Sets a single exit code per Task to interpret as success """
        if len(exit_codes_success) != self.test.job.number_tasks():
            raise Exception('You must provide one exit code per Task')
        for code in exit_codes_success:
            if not isinstance(code, int):
                raise Exception('Exit codes must be integers')
        self.exit_codes_success = exit_codes_success


class ComparisonVerifier(Verifier):
    """ A :class:`Verifier` which compares an output file against a reference file """

    def __init__(self, test, expected_file, output_file=None, comparison_file=None):
        super(ComparisonVerifier, self).__init__(test)

        self.expected_file = expected_file

        if comparison_file and output_file:
            raise Exception('Cannot specify an output_file with a comparison_file')
        self.comparison_file = comparison_file

        exit_code_name, o_name, e_name = self.test.job.get_output_filenames()
        if not output_file and not comparison_file:
            self.output_file = o_name[-1]

    def execute(self, output_path=None, exec_path=None):
        report = []
        status = None

        if not os.path.isfile(self.expected_file):
            status = SCIATH_TEST_STATUS.expected_file_not_found
            report.append('[Comparison] Expected file missing: %s' % self.expected_file)
            return status, report

        from_file = self._from_file(output_path, exec_path)
        if not os.path.isfile(from_file):
            status = SCIATH_TEST_STATUS.output_file_not_found
            report.append('[Comparison] Output file missing: %s' % from_file)
            return status, report

        passing, report = self._compare_files(self.expected_file, from_file)
        status =  SCIATH_TEST_STATUS.ok if passing else SCIATH_TEST_STATUS.not_ok
        return status, report

    def update_expected(self, output_path=None, exec_path=None):
        """ Update reference files from output

            Note that if multiple tests refer to the same reference file,
            a given reference file may be updated several times, and so
            even in cases where verification is solely based on reference files,
            updating may not be a guarantee that verification will succeed.

            """
        from_file = self._from_file(output_path, exec_path)
        if not os.path.isfile(from_file):
            print('[SciATH] Cannot update: source file missing: %s' % from_file)
        else:
            try:
                shutil.copy(from_file, self.expected_file)
            except IOError as io_err:
                if io_err.errno != errno.ENOENT:
                    raise
                os.makedirs(os.path.dirname(self.expected_file))
                shutil.copyfile(from_file, self.expected_file)

    def _compare_files(self, from_file, to_file):  # pylint: disable=no-self-use
        passing = True
        report = []
        if filecmp.cmp(from_file, to_file):
            return passing, report
        else:
            with open(from_file, 'r') as from_handle:
                lines_from = from_handle.readlines()
            with open(to_file, 'r') as to_handle:
                lines_to = to_handle.readlines()
            for line in difflib.unified_diff(lines_from, lines_to,
                                             fromfile=from_file,
                                             tofile=to_file):
                report.append(line.rstrip('\n'))
            passing = False
        return passing, report

    def _from_file(self, output_path=None, exec_path=None):
        """ Determine the full path to the file to compare against the expected file """
        if self.comparison_file:
            if not exec_path:
                raise Exception("exec_path must be provided, when a comparison file is specified")
            path = os.path.join(exec_path, self.comparison_file)
        else:
            if not output_path:
                raise Exception("output_path must be provided, when comparing to an output file")
            path = os.path.join(output_path, self.output_file)
        return path
