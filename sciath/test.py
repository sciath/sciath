
import os
import numpy as np
from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.verifier import Verifier
from sciath.launcher import _getLaunchStandardOutputFileNames


class Test:
    def __init__(self, job, name = None):
        self.job = job
        if name is not None:
            self.name = name
        else:
            if job.named_by_default:
                raise Exception("[SciATH error] to create a Test, you must either name the Test or the Job explicitly")
            self.name = job.name
        self.verifier = Verifier(self)

    def getReport(self):
        return self.verifier.getReport()

    def getStatus(self):
        return self.verifier.getStatus()

    def verify(self,output_path):
        self.verifier.execute(output_path)
