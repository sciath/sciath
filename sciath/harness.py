""" SciATH Harness class """
from __future__ import print_function

import os
import sys
import argparse
import shutil
import datetime

import sciath
import sciath.launcher
import sciath.test_file
from sciath._sciath_io import (py23input, command_join, color_okay, color_fail,
                               color_warning, format_header, format_info,
                               format_subheader, print_info, print_header,
                               print_subheader, print_warning, print_error)
from sciath.verifier import SciATHVerifierMissingFileException
from sciath._test_run import _TestRun, _TestRunStatus
import sciath.report_tap


class SciATHHarnessInconsistentStateException(Exception):
    """ Exception for unexpected filesystem state """


def _color_from_status(status, string):  #pylint: disable=too-many-return-statements
    if status == _TestRunStatus.DEACTIVATED:
        return string
    if status == _TestRunStatus.PASS:
        return color_okay(string)
    if status == _TestRunStatus.FAIL:
        return color_fail(string)
    if status == _TestRunStatus.INCOMPLETE:
        return color_warning(string)
    if status == _TestRunStatus.NOT_LAUNCHED:
        return color_warning(string)
    if status == _TestRunStatus.UNKNOWN:
        return color_warning(string)
    if status == _TestRunStatus.SKIPPED:
        return color_warning(string)
    raise Exception("Unhandled status %s" % status)


class Harness:
    """ :class:`Harness` is the central user-facing class in SciATH.

    It manages a set of tests, and thus includes:

    * A set of uniquely-named :class:`Test` objects
    * A :class:`Launcher`
    * Tools for running and verifying a test suite
    * Tools for managing "sandboxing" (managing directories in which to run tests)


    It is the exclusive location within SciATH for

    * Printing to stdout
    * Information about where to launch :class:`Job`s from, passed to included `Launcher`

    A :class:`Harness` object's state is confined to the state of a list of internal
    :class:`_TestRun` objects, and the state of the included :class:`Launcher`.
    """

    _pager = 'less'
    _report_filename = 'sciath_test_report.txt'
    _sandbox_sentinel_filename = '.sciath_sandbox'

    def __init__(self, tests=None):
        self.launcher = None  # Created when needed
        self.testruns = []
        if tests:
            for test in tests:
                self.add_test(test)
        self.report_filename_full = os.path.join(os.getcwd(),
                                                 self._report_filename)
        self.quiet = False  # quiet means only print specifically-requested output

    def add_test(self, test):
        """ Add a Test to be run with the harness """
        if test.name in [testrun.test.name for testrun in self.testruns]:
            raise Exception("Duplicate test name %s" % test.name)
        self.testruns.append(_TestRun(test))

    def add_tests_from_file(self, filename):
        """ Read a file to add Tests to be run with the harness """
        for test in sciath.test_file.create_tests_from_file(filename):
            self.add_test(test)

    def clean(self):
        """ Remove all output from all Tests, preparing or a re-run """
        if self.launcher is None:
            self.launcher = sciath.launcher.Launcher()

        if self.testruns:
            if not self.quiet:
                print_header("Cleanup")
        for testrun in self.testruns:
            if testrun.active:
                if not self.quiet:
                    print_info("Removing output for Test: %s" %
                               testrun.test.name)
                self.launcher.clean(testrun.test.job,
                                    output_path=testrun.output_path)
                if testrun.sandbox and os.path.exists(testrun.exec_path):
                    sentinel_file = os.path.join(
                        testrun.exec_path, self._sandbox_sentinel_filename)
                    if not os.path.exists(sentinel_file):
                        raise SciATHHarnessInconsistentStateException(
                            '[SciATH] did not find expected sentinel file ' +
                            sentinel_file)
                    shutil.rmtree(testrun.exec_path)

    def determine_overall_success(self):
        """ Returns a boolean value to denote overall success of the test suite """
        for testrun in self.testruns:
            if testrun.status not in [
                    _TestRunStatus.DEACTIVATED, _TestRunStatus.PASS
            ]:
                return False
        return True

    def execute(self):
        """ Execute all tests """
        self.clean()

        if self.launcher is None:
            self.launcher = sciath.launcher.Launcher()

        if self.testruns:
            if not self.quiet:
                print()
                print_header("Executing Tests")
                print(self.launcher)
        for testrun in self.testruns:
            if testrun.active:
                if not os.path.exists(testrun.output_path):
                    os.makedirs(testrun.output_path)
                if not os.path.exists(testrun.exec_path):
                    os.makedirs(testrun.exec_path)
                if testrun.sandbox:
                    sentinel_file = os.path.join(
                        testrun.exec_path, self._sandbox_sentinel_filename)
                    if os.path.exists(sentinel_file):
                        raise SciATHHarnessInconsistentStateException(
                            "[SciATH] Unexpected sentinel file %s" %
                            sentinel_file)
                    with open(sentinel_file, 'w'):
                        pass
                if not self.quiet:
                    print_subheader("Executing %s" % testrun.test.job.name,
                                    end="")
                    print("from %s" % testrun.exec_path)
                    print(
                        command_join(
                            self.launcher.launch_command(
                                testrun.test.job, testrun.output_path)))
                success, info, report = self.launcher.submit_job(
                    testrun.test.job,
                    output_path=testrun.output_path,
                    exec_path=testrun.exec_path)
                if not success:
                    testrun.status = _TestRunStatus.SKIPPED
                    testrun.status_info = info
                    testrun.report = report

    def print_all_tests(self):
        """ Display information about all tests """
        for testrun in self.testruns:
            info_string = [testrun.test.name]
            if testrun.test.groups:
                info_string.append(' (')
                info_string.append(', '.join(testrun.test.groups))
                info_string.append(')')
            print(''.join(info_string))

    def report(self):  #pylint: disable=too-many-branches
        """ Compile results into a report and print to stdout and file """
        report = []
        failed_names = []
        if self.testruns:
            report_header_printed = False
            for testrun in self.testruns:
                if testrun.report:
                    if not report_header_printed:
                        report.append('')
                        report.append(format_header("Verification Reports"))
                        report_header_printed = True
                    report.append(
                        format_subheader("Report for %s" % testrun.test.name))
                    for line in testrun.report:
                        report.append(line)
                    stdout_filename = os.path.join(
                        testrun.output_path, testrun.test.job.stdout_filename)
                    if os.path.isfile(stdout_filename) and os.stat(
                            stdout_filename).st_size != 0:
                        report.append('check stdout file:')
                        report.append('    %s %s' %
                                      (self._pager, stdout_filename))
                    stderr_filename = os.path.join(
                        testrun.output_path, testrun.test.job.stderr_filename)
                    if os.path.isfile(stderr_filename) and os.stat(
                            stderr_filename).st_size != 0:
                        report.append(
                            color_warning("check non-empty stderr file:"))
                        report.append('    %s %s' %
                                      (self._pager, stderr_filename))
            report.append('')
            report.append(format_header("Summary"))
            for testrun in self.testruns:
                if testrun.status == _TestRunStatus.FAIL:
                    failed_names.append(testrun.test.name)
                line = [
                    _color_from_status(
                        testrun.status,
                        "[%s]  %s" % (testrun.test.name, testrun.status))
                ]
                if testrun.status_info:
                    line.append(' (' + testrun.status_info + ')')
                report.append(''.join(line))
            report.append('')
            if any((testrun.active for testrun in self.testruns)):
                if self.determine_overall_success():
                    report.append(color_okay("SUCCESS"))
                else:
                    report.append(color_fail("FAILURE"))
                    if failed_names:
                        report.append('To re-run failed tests, use e.g.')
                        report.append('  -t ' + ','.join(failed_names))
            else:
                report.append("No tests active")
        else:
            report.append("No tests")
        if not self.quiet:
            for line in report:
                print(line)

        self._report_to_file(report)
        if not self.quiet:
            print('\nReport written to file:\n  %s' %
                  (self.report_filename_full))

    def _report_to_file(self, report):
        """ Dumps a report, as a list of lines (no new-lines) to file

            Prepends additional information, so that the file can be
            sent elsewhere or referred to later
        """
        with open(self.report_filename_full, 'w') as handle:
            handle.write(
                datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S') + '\n')
            handle.write(str(self.launcher) + '\n')
            handle.write('\n'.join(report) + '\n')

    def run_from_args(self):  #pylint: disable=too-many-branches
        """ Perform one or more actions, based on command line options

        This essentially defines the "main" function for the typical
        use of SciATH.
        """
        args = _parse_args()

        if args.no_colors:
            sciath.no_colors()

        if args.quiet or args.tap:
            self.quiet = True

        if args.update_expected:
            print_info(
                "You have provided an argument to updated expected files.")
            print_info("This will attempt to OVERWRITE your expected files!")
            user_input = None
            while not user_input:
                user_input = py23input(
                    format_info("Are you sure? Type 'y' to continue: "))
            if user_input[0] not in ['y', 'Y']:
                print_info("Aborting.")
                return

        if args.input_files:
            for input_file in args.input_files:
                try:
                    self.add_tests_from_file(input_file)
                except sciath.test_file.SciATHTestFileException as exception:
                    print_error("There was a problem reading tests from %s:" %
                                input_file,
                                file=sys.stderr)
                    print(exception, file=sys.stderr)
                    return

        if args.list:
            self.print_all_tests()
            return

        if args.test:
            self._activate_tests_from_list(args.test)

        if args.group or args.exclude_group:
            self._activate_test_groups(args.group, args.exclude_group)

        if args.configure_default:
            sciath.launcher.Launcher.write_default_definition(args.conf_file)
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
            try:
                self.update_expected()
            except SciATHVerifierMissingFileException as exception:
                print_warning("Update of expected file failed:")
                print_info(exception)
                print_warning("Not updating")
                return

        if args.execute or (not args.verify and not self.launcher.blocking):
            if self.testruns:
                if not self.quiet:
                    print_info("Not verifying or reporting")
        else:
            self.verify()
            self.report()

        if args.tap:
            sciath.report_tap.print_tap(self)

        if args.error_on_test_failure:
            if not self.determine_overall_success():
                sys.exit(1)

    def update_expected(self):
        """ Give each active test the chance to update its reference output """
        if self.testruns:
            if not self.quiet:
                print_header("Updating Expected Output")
        for testrun in self.testruns:
            if testrun.active:
                if hasattr(testrun.test.verifier, 'update_expected'):
                    if not self.quiet:
                        print_info("Updating output for Test: %s" %
                                   testrun.test.name)
                    testrun.test.verifier.update_expected(
                        testrun.output_path, testrun.exec_path)
                else:
                    if not self.quiet:
                        print_info("Output updated not supported for Test: %s" %
                                   testrun.test.name)

    def verify(self):
        """ Updates the status of all test runs """
        for testrun in self.testruns:
            if not testrun.active:
                testrun.status = _TestRunStatus.DEACTIVATED
                continue
            if testrun.status == _TestRunStatus.SKIPPED:
                continue
            if not sciath.launcher.job_launched(testrun.test.job,
                                                testrun.output_path):
                testrun.status = _TestRunStatus.NOT_LAUNCHED
                continue
            if not sciath.launcher.job_complete(testrun.test.job,
                                                testrun.output_path):
                testrun.status = _TestRunStatus.INCOMPLETE
                continue

            passing, testrun.status_info, testrun.report = testrun.test.verify(
                testrun.output_path, testrun.exec_path)
            testrun.status = _TestRunStatus.PASS if passing else _TestRunStatus.FAIL

    def _activate_tests_from_list(self, tests):
        """ Deactivate test runs not named in a list

        For backwards compatibility, each entry may be a comma-separated list.
        """
        tests_flat = []
        for test in tests:
            tests_flat.extend(test.split(","))
        for testrun in self.testruns:
            if testrun.test.name not in tests_flat:
                testrun.active = False

    def _activate_test_groups(self, only_groups, exclude_groups):
        """ Deactivate tests not in only_groups and all tests in exclude_groups
        """
        for testrun in self.testruns:
            if only_groups and not testrun.test.groups.intersection(
                    only_groups):
                testrun.active = False
            if testrun.test.groups.intersection(exclude_groups):
                testrun.active = False


def _parse_args():
    parser = argparse.ArgumentParser(description='SciATH')
    parser.add_argument('input_files',
                        help='YAML file[s] to add tests to the harness',
                        nargs='*',
                        default=None)
    parser.add_argument('-c',
                        '--configure',
                        help='Configure queuing system information',
                        required=False,
                        action='store_true')
    parser.add_argument(
        '-t',
        '--test',
        help='Run only this test and those from other -t/--test arguments',
        required=False,
        action='append')
    parser.add_argument('-p',
                        '--purge-output',
                        help='Delete generated output',
                        required=False,
                        action='store_true')
    parser.add_argument('-f',
                        '--error-on-test-failure',
                        help='Return exit code of 1 if any test failed',
                        required=False,
                        action='store_true')
    parser.add_argument('-d',
                        '--configure-default',
                        help='Write default queuing system config file',
                        required=False,
                        action='store_true')
    parser.add_argument('-l',
                        '--list',
                        help='List all registered tests and exit',
                        required=False,
                        action='store_true')
    parser.add_argument('-w',
                        '--conf-file',
                        help='Use provided configuration file',
                        required=False)
    parser.add_argument('--no-colors',
                        help='Deactivate colored output',
                        required=False,
                        action='store_true')
    parser.add_argument(
        '-u',
        '--update-expected',
        help='When well-defined, update reference files with current output',
        required=False,
        action='store_true')
    stage_skip_group = parser.add_mutually_exclusive_group()
    stage_skip_group.add_argument(
        '-v',
        '--verify',
        help='Perform test verification, and not execution',
        required=False,
        action='store_true')
    stage_skip_group.add_argument(
        '-e',
        '--execute',
        help='Perform test execution, and not verification',
        required=False,
        action='store_true')
    parser.add_argument(
        '-g',
        '--group',
        help='Exclude tests not in this or any other -g/--group argument',
        required=False,
        action='append')
    parser.add_argument('-x',
                        '--exclude-group',
                        help='Exclude tests in this group',
                        required=False,
                        action='append')
    parser.add_argument(
        '--tap',
        help='Print TAP-compatible output, and activate quiet mode.',
        required=False,
        action='store_true')
    parser.add_argument(
        '-q',
        '--quiet',
        help='Only print information requested by other options',
        required=False,
        action='store_true')
    return parser.parse_args()
