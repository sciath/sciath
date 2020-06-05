import os
import sys
import argparse
import shutil
from enum import Enum # Before Python 3.4, you need the enum34 (NOT enum) module

import sciath
from sciath.test import Test
from sciath.launcher import Launcher

class _TestRunStatus(Enum):
    DEACTIVATED             = 'deactivated'  # Test skipped intentionally
    UNKNOWN                 = 'unknown'      # Neither checked for completion nor verified
    NOT_LAUNCHED            = 'not launched' # Launcher reports test has not been launched
    INCOMPLETE              = 'incomplete'   # Launcher reports test run incomplete
    COMPLETE_AND_UNVERIFIED = 'unverified'   # Launcher reports complete, yet verification not performed
    SKIPPED                 = 'skipped'      # Test skipped because Launcher reports of lack of resources
    JOB_INVALID             = 'invalid job'  # Launcher reports test's Job is incorrectly specified
    TEST_INVALID            = 'invalid test' # Verifier reports test/verification is badly specified
    PASS                    = 'pass'         # Verifier confirms pass
    FAIL                    = 'fail'         # Verifier confirms fail

class _TestRun:
        """ A private class which adds state about a specific "run" of a Test.

        It contains a Test object, which should be thought of as the stateless
        information about a test case, provided by a user. In addition, it
        contains information managed by the Harness, such as a location to run
        from, information collected from the Launcher (to use for output), etc.
        """

        def __init__(self,test):
            self.active = True
            self.test = test
            self.output_path = os.path.join(os.getcwd(),test.name + '_output')
            self.exec_path = os.path.join(self.output_path,'sandbox')
            self.sandbox = True
            self.status = _TestRunStatus.UNKNOWN
            self.status_info = ''

class Harness:
    """ :class:`Harness` is the central user-facing class in SciATH.

    It manages a set of tests, and thus includes:

    * A set of uniquely-named :class:`Test` objects
    * A :class:`Launcher`
    * Tools for running and verifying a test suite
    * Tools for managing "sandboxing" (managing directories in which to run tests)


    It is the exclusive location within SciATH for

    * Printing to stdout
    * Information about where to launch ``Jobs`` from, passed to included ``Launcher``

    A :class:`Harness` object's state is confined to the state of a list of internal
    :class:`_TestRun` objects.
    """

    _sandbox_sentinel_filename = '.sciath_sandbox'

    def __init__(self,tests):
        self.launcher = None # Created when needed
        self.testruns = []
        for test in tests:
            self.add_test(test)

    def add_test(self, test):
        self.testruns.append(_TestRun(test))

    def clean(self):
        if self.launcher is None:
            self.launcher = Launcher()

        # Clean all tests
        for testrun in self.testruns:
            if testrun.active:
                print('[ -- Removing output for Test:',testrun.test.name,'-- ]')
                self.launcher.clean(testrun.test.job, output_path=testrun.output_path)
                if testrun.sandbox and os.path.exists(testrun.exec_path):
                    sentinel_file = os.path.join(testrun.exec_path,self._sandbox_sentinel_filename)
                    if not os.path.exists(sentinel_file):
                        raise Exception('[SciATH] did not find expected sentinel file ' + sentinel_file)
                    shutil.rmtree(testrun.exec_path)

    def determine_overall_success(self):
        for testrun in self.testruns:
            if testrun.status not in [_TestRunStatus.DEACTIVATED, _TestRunStatus.PASS] :
                return False
        return True

    def execute(self):
        # Always clean before executing
        self.clean()

        if self.launcher is None:
            self.launcher = Launcher()

        for testrun in self.testruns:
            if testrun.active:
                if not os.path.exists(testrun.output_path):
                    os.makedirs(testrun.output_path)
                if not os.path.exists(testrun.exec_path):
                    os.makedirs(testrun.exec_path)
                if testrun.sandbox:
                    sentinel_file = os.path.join(testrun.exec_path,self._sandbox_sentinel_filename)
                    if os.path.exists(sentinel_file):
                        raise Exception("[SciATH] Unexpected sentinel file " + sentinel_file)
                    with open(sentinel_file,'w'):
                        pass
                self.launcher.submitJob(
                        testrun.test.job,
                        output_path=testrun.output_path,
                        exec_path = testrun.exec_path)

    def print_all_tests(self):
        for testrun in self.testruns:
            print(testrun.test.name)

    def report(self):
        """ Compile results into a report and print """
        for testrun in self.testruns:
            print(testrun.test.name,":",testrun.status.value,'('+testrun.status_info+')' if testrun.status_info else '')
        if self.determine_overall_success():
            print("Overall Success!")
        else:
            print("TEST SUCCESS NOT CONFIRMED")

    def run_from_args(self):
        """ Perform one or more actions, based on command line options

        This essentially defines the "main" function for the typical
        use of SciATH.
        """

        parser = argparse.ArgumentParser(description='SciATH')
        parser.add_argument('-v', '--verify', help='Perform test verification (and not execution)', required=False, action='store_true')
        parser.add_argument('-c', '--configure', help='Configure queuing system information', required=False, action='store_true')
        parser.add_argument('-t', '--test-subset', help='Comma-separated list of test names', required=False)
        parser.add_argument('-p', '--purge-output', help='Delete generated output', required=False, action='store_true')
        parser.add_argument('-f', '--error-on-test-failure', help='Return exit code of 1 if any test failed', required=False, action='store_true')
        parser.add_argument('-d', '--configure-default', help='Write default queuing system config file (no mpi, no queuing system)', required=False, action='store_true')
        parser.add_argument('-l', '--list', help='List all registered tests and exit', required=False, action='store_true')
        parser.add_argument('-w','--conf-file',help='Use provided configuration file instead of the default',required=False)
        parser.add_argument('--no-colors',help='Deactivate colored output',required=False,action='store_true')
        args,unknown = parser.parse_known_args()

        if args.no_colors:
            sciath.sciath_colors.set_colors(use_bash = False)

        if args.list:
            self.print_all_tests()
            return

        if args.test_subset:
            self._activate_tests_from_argument(args.test_subset)

        if args.configure_default:
            Launcher.writeDefaultDefinition(args.conf_file)
            return

        self.launcher = Launcher(args.conf_file)

        if args.configure:
            self.launcher.configure()

        if args.purge_output:
            self.clean()
            return

        if not args.verify:
            self.execute()

        if not args.verify and self.launcher.useBatch:
            # TODO instead test something like self.launcher.is_blocking(), to make it easier to have a local batch system
            print('Not verifying or reporting, since there is a queue')
        else:
            self.verify()
            self.report()

        if args.error_on_test_failure:
            if not self.determine_overall_success():
                sys.exit(1)

    def verify(self):
        """ Update the status of all test runs """
        for testrun in self.testruns:
            if testrun.active:
                # TODO Need to ask the launcher if the job is completed and update the status, before passing to the verifier
                status,report = testrun.test.verifier.execute(testrun.output_path)
                # TODO report is not currently used (use when improving reporting)
                verifier_status = status[0]
                verifier_info = status[1]
                if verifier_status == 'pass':
                    testrun.status = _TestRunStatus.PASS
                    testrun.status_info = verifier_info
                elif verifier_status in ['fail','warn']: # TODO get rid of warn?
                    testrun.status = _TestRunStatus.FAIL
                    testrun.status_info = verifier_info
                elif verifier_status == 'skip':
                    testrun.status = _TestRunStatus.SKIP
                    testrun.status_info = verifier_info
                else:
                    testrun.status = _TestRunStatus.INVALID
                    testrun.status_info = "Verifier returned unrecognized status and info: " + verifier_status + ", " + verifier_info
            else:
                testrun.status = _TestRunStatus.DEACTIVATED

    def _activate_tests_from_argument(self, test_subset_arg):
        test_subset_names = test_subset_arg.split(',')
        for testrun in self.testruns:
            testrun.active = False
        for name in test_subset_names:
            found = False
            for testrun in self.testruns:
                if name == testrun.test.name:
                    testrun.active = True
                    found = True
                    break
