import os

import numpy as np

from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.verifier import VerifierExitCode


class Test:
    """ :class:`Test` describes a test case in a test suite.

    It is simply a collection of data about such a case, not about any particular "run" of it.

    Thus, it contains:

    * A :class:`Job`, describing how to execute the required operations
    * A name (inherited from the :class:`Job`, if not specified)
    * An implementation of the abstract base class :class:`Verifier`, defining how to determine success
    * A set of tags

    """
    def __init__(self, job, name = None):
        self.job = job
        if name is not None:
            self.name = name
        else:
            if job.named_by_default:
                raise Exception("[SciATH error] to create a Test, you must either name the Test or the Job explicitly")
            self.name = job.name
        self.verifier = VerifierExitCode(self)

    def verify(self,output_path):
        status,report = self.verifier.execute(output_path)
        return status,report
