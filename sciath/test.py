
import os
import numpy as np
from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.verifier import Verifier
from sciath.launcher import _getLaunchStandardOutputFileNames


class Test:
    def __init__(self,job,name,**kwargs):
        self.job = job
        self.name = name

        if self.name is None:
            message = '[SciATH error] Test constructor requires a valid name is provided.'
            raise RuntimeError(message)

        # Overide job name. Since test requires a name, and launcher requires a job to have a name,
        # this overide ensures test.job will go through the launcher without error.
        job.name = self.name

        self.verifier = Verifier(self,**kwargs)

    def getReport(self):
        return self.verifier.getReport()

    def getStatus(self):
        return self.verifier.getStatus()

    def test_print(self):
        # TODO this function is only used for testing and can probably be removed (especially since this is a class which isn't supposed to directly print anything)
        rep = [self.name] + self.getStatus()
        print(rep)
        for l in self.getReport():
            print(l)

    def verify(self,output_path):
        self.verifier.execute(output_path)
