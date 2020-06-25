""" SciATH Test class """
import sciath.verifier


class Test:
    """ :class:`Test` describes a test case in a test suite.

    It is simply a collection of data about such a case, not about any particular "run" of it.

    Thus, it contains:

    * A :class:`Job`, describing how to execute the required operations
    * A name
    * An implementation of the abstract base class :class:`Verifier`, defining
    how to determine success
    * A set of group tags

    """
    def __init__(self, job, name=None):
        self.job = job
        if name is not None:
            self.name = name
        else:
            if job.named_by_default:
                raise Exception("[SciATH error] to create a Test, you must either "
                                "name the Test or the Job explicitly")
            self.name = job.name
        self.verifier = sciath.verifier.ExitCodeVerifier(self)
        self.groups = set()

    def add_group(self, group):
        """ Tag the test with a space-free string """
        if ' ' in group:
            raise Exception('[SciATH] group names cannot have spaces')
        self.groups.add(group)

    def verify(self, output_path=None, exec_path=None):
        """ Return a status and a report, relative to an output and execution path """
        status, report = self.verifier.execute(output_path, exec_path)
        return status, report
