import os

import numpy as np

from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath import sciath_test_status


class Verifier:
    """Base class for verification of a Test"""
    # Note: this should more properly be an abstract base class, but we delay this while still trying to support Python 2

    def __init__(self,test):
        self.test = test

    def execute(self,output_path,exec_path = None):
        """ Relative to a given output path, fetch file(s) and produce status,report """
        raise NotImplementedError("Verifier implementations must override execute()")

class VerifierExitCode(Verifier):
    """ Verifier implementation which checks an error code """

    def __init__(self, test):
        Verifier.__init__(self, test)

    def execute(self, output_path, exec_path = None):
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
        data = np.asarray(data,dtype=int)

        # special
        if not isinstance(self.test.job,JobSequence) and not isinstance(self.test.job,JobDAG):
            if self.test.job.exit_code_success != data[0]:
                status = sciath_test_status.not_ok
                return status,report
            else:
                status = sciath_test_status.ok
                return status,report

        else:
            jobs = self.test.job.getJobList()

            if len(data) != len(jobs):
                report.append("[ReturnCodeDiff] Mismatch in number of error codes found and jobs run. This should never happen.")
                exret = np.zeros(len(jobs))
                for j in range(0,len(jobs)):
                    exret[j] = int(jobs[j].exit_code_success)
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

            exret = np.copy(data)
            for j in range(0,L):
                exret[j] = int(jobs[j].exit_code_success)

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
