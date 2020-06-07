import os
import filecmp
import difflib
import shutil

from sciath.job import Job
from sciath.job import JobSequence
from sciath import sciath_test_status


class Verifier:
    """Base class for verification of a Test"""
    # Note: this should more properly be an abstract base class, but we delay this while still trying to support Python 2

    def __init__(self, test):
        self.test = test

    def execute(self, output_path=None, exec_path=None):
        """ Relative to a given output path, fetch file(s) and produce status,report

            Accepts an output path (where the Launcher puts the files it generates)
            and an execution path (where the Job was run from). Either might be
            required for verification: for instance, to check the error code
            collected by the Launcher, one needs the output path, and to compare
            with an output file generated by an executable, one needs the execution
            path.
        """
        raise NotImplementedError("Verifier implementations must override execute()")

    def update_expected(self, output_path=None, exec_path=None):
        """ Update reference files from output, if possible

            This function can be overridden to give a Verifier implementation
            the opportunity to update any reference files it refers to,
            from the output it usually examines. This is very useful for
            some implementations, as one can quickly generate or
            update reference files with the same tools used to run the tests.

            Note that if multiple tests refer to the same reference file,
            a given reference file may be updated several times, and so
            even in cases where verification is solely based on refernce files,
            updating may not be a guarantee that verification will succeed.

            """


class ExitCodeVerifier(Verifier):
    """ Verifier implementation which checks an error code """

    def __init__(self, test):
        super(ExitCodeVerifier,self).__init__(test)

    def execute(self, output_path, exec_path=None):
        """ Relative to a given output path, fetch file(s) and produce status,report """

        status = None
        report = []

        c_name, o_name, e_name = self.test.job.get_output_filenames()

        errorfile = os.path.join(output_path,c_name)
        if not os.path.isfile(errorfile) :
            report.append("[ReturnCodeDiff] File (" + errorfile + ") not found")
            status = sciath_test_status.job_not_run
            return status,report

        with open(errorfile, 'r') as f:
            data = f.readlines()

        # special
        if not isinstance(self.test.job,JobSequence):
            if self.test.job.exit_code_success != int(data[0]):
                status = sciath_test_status.not_ok
                return status,report
            else:
                status = sciath_test_status.ok
                return status,report

        else:
            jobs = self.test.job.getJobList()

            if len(data) != len(jobs):
                report.append("[ReturnCodeDiff] Mismatch in number of error codes found and jobs run. This should never happen.")
                exret = []
                for job in jobs:
                    exret.append(int(job.exit_code_success))
                msg = "[ReturnCodeDiff] Expected return codes: " + str(exret)
                report.append(msg)
                msg = "[ReturnCodeDiff] Output return codes  : " + str(data)
                report.append(msg)
                report.append("[ReturnCodeDiff] Output file: " + errorfile)
                status = sciath_test_status.not_ok
                return status,report

            L = len(data)
            anyChildrenFailed = False
            i = 0
            for j in range(0,L-1):
                j_job = jobs[i]
                if j_job.exit_code_success != data[i]:
                    anyChildrenFailed = True
                i += 1

            exret = []
            for job in jobs:
                exret.append(int(job.exit_code_success))

            s = sciath_test_status.ok
            if anyChildrenFailed == True:
                s = sciath_test_status.dependent_job_failed
                if self.test.job.exit_code_success != data[-1]:
                    s = sciath_test_status.parent_and_depjob_failed
            if s != sciath_test_status.ok:
                msg = "[ReturnCodeDiff] Expected return codes: " + str(exret)
                report.append(msg)
                msg = "[ReturnCodeDiff] Output return codes  : " + str(data)
                report.append(msg)
                report.append("[ReturnCodeDiff] Output file: " + errorfile)

            status = s

        return status,report


class ComparisonVerifier(Verifier):
    """ A :class:`Verifier` which compares an output file against a reference file """

    def __init__(self, test, expected_file, output_file=None, comparison_file=None):
        super(ComparisonVerifier, self).__init__(test)

        self.expected_file = expected_file

        if comparison_file and output_file:
            raise Exception('Cannot specify an output_file with a comparison_file')
        self.comparison_file = comparison_file

        c_name, o_name, e_name = self.test.job.get_output_filenames()
        if not output_file and not comparison_file:
            self.output_file = o_name[-1]
        # FIXME: I envision that there should only ever be one "output file" to consider. Having multiple stdout and stderr files just really doesn't seem worth the complication

    def execute(self, output_path=None, exec_path=None):
        report = []
        status = None

        if not os.path.isfile(self.expected_file) :
            status = sciath_test_status.expected_file_not_found
            report.append('[Comparison] Expected file missing: %s' % self.expected_file)
            return status, report

        from_file = self._from_file(output_path, exec_path)
        if not os.path.isfile(from_file) :
            status = sciath_test_status.output_file_not_found
            report.append('[Comparison] Output file missing: %s' % from_file)
            return status, report

        return self._compare_files(self.expected_file, from_file)

    def update_expected(self, output_path=None, exec_path=None):
        from_file = self._from_file(output_path, exec_path)
        if not os.path.isfile(from_file) :
            print('[SciATH] Cannot update: source file missing: %s' % from_file)
        else:
            # Does not create directories
            shutil.copyfile(from_file, self.expected_file)

    def _compare_files(self, from_file, to_file):
        if filecmp.cmp(from_file, to_file):
            return sciath_test_status.ok,[]
        else:
            with open(from_file, 'r') as from_handle:
                lines_from = from_handle.readlines()
            with open(to_file, 'r') as to_handle:
                lines_to = to_handle.readlines()
            report = []
            for line in difflib.unified_diff(lines_from, lines_to,
                                             fromfile=from_file,
                                             tofile=to_file):
                report.append(line.rstrip('\n'))
            return sciath_test_status.not_ok, report

    def _from_file(self, output_path=None, exec_path=None):
        """ Determine the full path to the file to compare against the expected file """
        if self.comparison_file:
            if not exec_path:
                raise Exception("exec_path must be provided, when a comparison file is specified")
            return os.path.join(exec_path, self.comparison_file)
        else:
            if not output_path:
                raise Exception("output_path must be provided, when comparing to an output file")
            return os.path.join(output_path, self.output_file)
