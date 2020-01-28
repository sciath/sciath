import os

import numpy as np

from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.launcher import _getLaunchStandardOutputFileNames
from sciath import sciath_test_status

class Verifier:
    """Base class for verification of a Test"""

    def __init__(self,test):
      self.test = test
      self.job = test.job
      self.c_name, self.o_name, self.e_name = _getLaunchStandardOutputFileNames(self.job)
      self.status = None
      self.report = []

    def getReport(self):
        return self.report

    def getStatus(self):
        return self.status

    def execute(self,output_path,exec_path=None):
        """ Relative to a given output path, fetch file, look at return code, check it matches that expected"""

        self.status = None
        self.report = []

        errorfile = os.path.join(output_path,self.c_name)
        if not os.path.isfile(errorfile) :
            self.report.append("[ReturnCodeDiff] File (" + errorfile + ") not found")
            self.status = sciath_test_status.job_not_run
            return

        with open(errorfile, 'r') as f:
            data = f.readlines()
        data = np.asarray(data,dtype=int)

        # special
        if not isinstance(self.job,JobSequence) and not isinstance(self.job,JobDAG):
            if self.job.exit_code_success != data[0]:
                self.status = sciath_test_status.not_ok
                return
            else:
                self.status = sciath_test_status.ok
                return

        else:
            jobs = self.job.getJobList()

            if len(data) != len(jobs):
                self.report.append("[ReturnCodeDiff] Mismatch in number of error codes found and jobs run. This should never happen.")
                exret = np.zeros(len(jobs))
                for j in range(0,len(jobs)):
                    exret[j] = int(jobs[j].exit_code_success)
                msg = "[ReturnCodeDiff] Expected return codes: " + str(exret)
                self.report.append(msg)
                msg = "[ReturnCodeDiff] Output return codes  : " + str(data)
                self.report.append(msg)
                self.report.append("[ReturnCodeDiff] Output file: " + errorfile)
                self.status = sciath_test_status.not_ok
                return

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
                if self.job.exit_code_success != data[-1]:
                    s = sciath_test_status.parent_and_depjob_failed
            if s != sciath_test_status.ok:
                msg = "[ReturnCodeDiff] Expected return codes: " + str(exret)
                self.report.append(msg)
                msg = "[ReturnCodeDiff] Output return codes  : " + str(data)
                self.report.append(msg)
                self.report.append("[ReturnCodeDiff] Output file: " + errorfile)

            self.status = s

        return
