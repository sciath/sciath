""" Generate a report in TAP format from the Harness """

from sciath._test_run import _TestRunStatus


def _testrun_status_to_ok_and_comment(status):  #pylint: disable=too-many-return-statements
    """ Returns whether a test run is "ok" or "not ok" and a comment to append.

        This comment can be a meaningful TAP directive like "#SKIP".
    """

    if status == _TestRunStatus.DEACTIVATED:
        return "ok", "#SKIP"
    if status == _TestRunStatus.PASS:
        return "ok", ""
    if status == _TestRunStatus.FAIL:
        return "not ok", ""
    if status == _TestRunStatus.INCOMPLETE:
        return "not ok", "(Incomplete) "
    if status == _TestRunStatus.NOT_LAUNCHED:
        return "not ok", "(Not Launched)"
    if status == _TestRunStatus.UNKNOWN:
        return "not ok", ""
    if status == _TestRunStatus.SKIPPED:
        return "not ok", "(skipped but not deactivated)"
    raise Exception("Unhandled status %s" % status)


def print_tap(harness):
    """ Print a TAP-compatible report from a :class:`Harness`

        Note that SciATH's notion of "deactivated" (intentionally skipped) corresponds
        to TAP's notion of "skipped", and SciATH's "skipped" status indicates
        failure, in that a requested test was not able to run.
    """

    print("1..%d" % len(harness.testruns))
    test_number = 0
    for testrun in harness.testruns:
        test_number += 1
        ok_string, comment = _testrun_status_to_ok_and_comment(testrun.status)
        print("%s %d %s %s" %
              (ok_string, test_number, testrun.test.job.name, comment))
