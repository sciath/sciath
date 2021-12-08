""" An internal class defining a particular execution of a Test """

import os


class _TestRunStatus:  #pylint: disable=too-few-public-methods
    DEACTIVATED = 'deactivated'  # Test skipped intentionally
    UNKNOWN = 'unknown'
    NOT_LAUNCHED = 'not launched'  # Launcher reports test run not launched
    INCOMPLETE = 'incomplete'  # Launcher reports test run incomplete
    SKIPPED = 'skipped'  # Test skipped: Launcher reports of lack of resources
    PASS = 'pass'  # Verifier confirms pass
    FAIL = 'fail'  # Verifier confirms fail


class _TestRun:  #pylint: disable=too-few-public-methods, too-many-instance-attributes
    """ A private class which adds state about a specific "run" of a Test.

        It contains a Test object, which should be thought of as the stateless
        information about a test case, provided by a user. In addition, it
        contains information managed by the Harness, such as a location to run
        from, information collected from the Launcher (to use for output), etc.
        """

    def __init__(self, test):
        self.active = True
        self.test = test
        self.output_path = os.path.join(os.getcwd(), test.name + '_output')
        self.exec_path = os.path.join(self.output_path, 'sandbox')
        self.sandbox = True
        self.status = _TestRunStatus.UNKNOWN
        self.status_info = ''
        self.report = []
