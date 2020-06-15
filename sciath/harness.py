from __future__ import print_function

import os
import sys
import argparse
import shutil

import sciath
import sciath.launcher
import sciath._test_file
from sciath import sciath_colors
from sciath._sciath_io import py23input

class _TestRunStatus:
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
            self.report = []

class Harness:
    """ :class:`Harness` is the central user-facing class in SciATH.

    It manages a set of tests, and thus includes:

    * A set of uniquely-named :class:`Test` objects
    * A :class:`Launcher`
    * Tools for running and verifying a test suite
    * Tools for managing "sandboxing" (managing directories in which to run tests)


    It is the exclusive location within SciATH for

    * Printing to stdout
    * Information about where to launch :class:`Job`s from, passed to included `Launcher`s

    A :class:`Harness` object's state is confined to the state of a list of internal
    :class:`_TestRun` objects.
    """

    _sandbox_sentinel_filename = '.sciath_sandbox'

    def __init__(self, tests=[]):
        self.launcher = None # Created when needed
        self.testruns = []
        for test in tests:
            self.add_test(test)

    def add_test(self, test):
        if test.name in [testrun.test.name for testrun in self.testruns]:
            raise Exception("Duplicate test name %s" % test.name)
        self.testruns.append(_TestRun(test))

    def add_tests_from_file(self, filename):
        for test in sciath._test_file.create_tests_from_file(filename):
            self.add_test(test)

    def clean(self):
        if self.launcher is None:
            self.launcher = sciath.launcher.Launcher()

        # Clean all tests
        if self.testruns:
            print(sciath_colors.HEADER+'[ *** Cleanup *** ]'+sciath_colors.ENDC)
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
        self.clean()

        if self.launcher is None:
            self.launcher = sciath.launcher.Launcher()

        if self.testruns:
            print(sciath_colors.HEADER + '[ *** Executing Tests *** ]' + sciath_colors.ENDC)
            self.launcher.view()
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
        failed_names = []
        if self.testruns:
            report_header_printed = False
            for testrun in self.testruns:
                if testrun.report:
                    if not report_header_printed:
                        print(sciath_colors.HEADER+'[ *** Verification Reports *** ]'+sciath_colors.ENDC)
                        report_header_printed = True
                    print('%s[Report for %s]%s' % (sciath_colors.SUBHEADER,testrun.test.name,sciath_colors.ENDC))
                    for line in testrun.report:
                        print(line)
            print(sciath_colors.HEADER+'[ *** Summary *** ]'+sciath_colors.ENDC)
            for testrun in self.testruns:
                if testrun.status == 'fail':
                    failed_names.append(testrun.test.name)
                print(sciath.sciath_test_status.status_color_type[testrun.status], end='')
                print('[%s]  %s' %(testrun.test.name, testrun.status), end='')
                print(sciath_colors.ENDC, end='')
                if testrun.status_info:
                    print(' (' + testrun.status_info + ')', end='')
                print()
            print()
            if self.determine_overall_success():
                print(sciath_colors.OK + "SUCCESS" + sciath_colors.ENDC)
            else:
                print(sciath_colors.FAIL + "FAILURE" + sciath_colors.ENDC)
                if failed_names:
                    print('To re-run failed tests, use e.g.')
                    print('  -t ' + ','.join(failed_names))
        else:
            print("No tests")

    def run_from_args(self):
        """ Perform one or more actions, based on command line options

        This essentially defines the "main" function for the typical
        use of SciATH.
        """

        parser = argparse.ArgumentParser(description='SciATH')
        parser.add_argument('-c', '--configure', help='Configure queuing system information', required=False, action='store_true')
        parser.add_argument('-t', '--test-subset', help='Comma-separated list of test names', required=False)
        parser.add_argument('-p', '--purge-output', help='Delete generated output', required=False, action='store_true')
        parser.add_argument('-f', '--error-on-test-failure', help='Return exit code of 1 if any test failed', required=False, action='store_true')
        parser.add_argument('-d', '--configure-default', help='Write default queuing system config file (no mpi, no queuing system)', required=False, action='store_true')
        parser.add_argument('-l', '--list', help='List all registered tests and exit', required=False, action='store_true')
        parser.add_argument('-w','--conf-file',help='Use provided configuration file instead of the default',required=False)
        parser.add_argument('--no-colors',help='Deactivate colored output',required=False,action='store_true')
        parser.add_argument('-i', '--input-file', help='Parse a file to add tests to the harness', required=False)
        parser.add_argument('-u', '--update-expected', help='When well-defined, update reference files with current output before verifying', required=False, action='store_true')
        stage_skip_group = parser.add_mutually_exclusive_group()
        stage_skip_group.add_argument('-v', '--verify', help='Perform test verification, and not execution', required=False, action='store_true')
        stage_skip_group.add_argument('-e','--execute', help='Perform test execution, and not verification', required=False, action='store_true')
        args,unknown = parser.parse_known_args()

        if args.no_colors:
            sciath.sciath_colors.set_colors(use_bash = False)

        if args.update_expected:
            print("[SciATH] You have provided an argument to updated expected files.")
            print("[SciATH] This will attempt to OVERWRITE your expected files!")
            if py23input("[SciATH] Are you sure? Type 'y' to continue: ")[0] not in ['y','Y']:
                print("[SciATH] Aborting.")
                return

        if args.input_file:
            self.add_tests_from_file(args.input_file)

        if args.list:
            self.print_all_tests()
            return

        if args.test_subset:
            self._activate_tests_from_argument(args.test_subset)

        if args.configure_default:
            sciath.launcher.Launcher.writeDefaultDefinition(args.conf_file)
            return

        self.launcher = sciath.launcher.Launcher(args.conf_file)

        if args.configure:
            self.launcher.configure()

        if args.purge_output:
            self.clean()
            return

        if not args.verify:
            self.execute()

        if args.update_expected:
            self.update_expected()

        if args.execute or (not args.verify and self.launcher.useBatch):
            if self.testruns:
                print('[SciATH] Not verifying or reporting')
        else:
            self.verify()
            self.report()

        if args.error_on_test_failure:
            if not self.determine_overall_success():
                sys.exit(1)

    def update_expected(self):
        """ Give each active test the chance to update its reference output """
        if self.testruns:
            print(sciath_colors.HEADER + '[ *** Updating Expected Output *** ]' + sciath_colors.ENDC)
        for testrun in self.testruns:
            if testrun.active:
                if hasattr(testrun.test.verifier, 'update_expected'):
                    print('[ -- Updating output for Test:',testrun.test.name,'-- ]')
                    testrun.test.verifier.update_expected(testrun.output_path, testrun.exec_path)
                else:
                    print('[ -- Output updated not supported for Test:',testrun.test.name,'-- ]')

    def verify(self):
        """ Update the status of all test runs """
        for testrun in self.testruns:
            if testrun.active:
                status, testrun.report = testrun.test.verify(testrun.output_path, testrun.exec_path)
                verifier_status = status[0]
                verifier_info = status[1]
                if verifier_status == 'pass':
                    testrun.status = _TestRunStatus.PASS
                    testrun.status_info = verifier_info
                elif verifier_status == 'fail':
                    testrun.status = _TestRunStatus.FAIL
                    testrun.status_info = verifier_info
                elif verifier_status == 'skip':
                    testrun.status = _TestRunStatus.SKIPPED
                    testrun.status_info = verifier_info
                else:
                    testrun.status = _TestRunStatus.FAIL
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
