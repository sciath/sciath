import os
import argparse
import shutil

import sciath
from sciath.test import Test
from sciath.launcher import Launcher

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
            self.output_path = test.name + '_output'
            self.exec_path = os.path.join(self.output_path,'sandbox')
            self.sandbox = True

class Harness:

    sandbox_sentinel_filename = '.sciath_sandbox'

    def __init__(self,test_list):
        self._create_testruns_from_tests(test_list)
        self.launcher = None # Created when needed

    def clean(self):
        if self.launcher is None:
            self.launcher = Launcher()

        # Clean all tests
        for testrun in self.testruns:
            if testrun.active:
                print('[ -- Removing output for Test:',testrun.test.name,'-- ]')
                self.launcher.clean(testrun.test.job, output_path=testrun.output_path)
                if testrun.sandbox and os.path.exists(testrun.exec_path):
                    sentinel_file = os.path.join(testrun.exec_path,self.sandbox_sentinel_filename)
                    if not os.path.exists(sentinel_file):
                        raise Exception('[SciATH] did not find expected sentinel file ' + sentinel_file)
                    shutil.rmtree(testrun.exec_path)

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
                    sentinel_file = os.path.join(testrun.exec_path,self.sandbox_sentinel_filename)
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
        for testrun in self.testruns:
            print(testrun.test.name,":",testrun.test.getStatus())

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

        self.verify()

        self.report()

        if args.error_on_test_failure:
            raise Exception("Exit on failure option not implemented")

    def verify(self):
        for testrun in self.testruns:
            if testrun.active:
                testrun.test.verifier.execute(testrun.output_path)

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

    def _create_testruns_from_tests(self,test_list):
        """ Create a list of _TestRuns from a list of Tests"""
        self.testruns = [_TestRun(test) for test in test_list]
