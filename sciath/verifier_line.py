import os
import re
import shutil

from sciath.verifier import ComparisonVerifier
from sciath import SCIATH_TEST_STATUS


class LineVerifier(ComparisonVerifier):
    """ An Verifier which compares sets of lines from expected and output files

        This is accomplished by defining a set of "rules". Each rule contains
        a regular expression to determine which lines to match, and a function
        to determine success when comparing the the set of matching lines
        from the two files.
    """

    def __init__(self, test, expected_file, output_file=None, comparison_file=None):
      super(LineVerifier, self).__init__(test, expected_file, output_file, comparison_file)
      self.rules = []

    def _compare_files(self, from_file, to_file):
        passing = True
        report = []
        for rule in self.rules:
            match_from = {}
            match_to = {}
            for [match, source_file] in [(match_from, from_file), (match_to, to_file)]:
                with open(source_file, 'r') as handle:
                    line_number = 0
                    for line in handle.readlines():
                        line_number += 1
                        if re.match(rule['re'],line):
                            match[line_number] = line
            rule_result, rule_report  = rule['function'](match_from, match_to)
            if passing and not rule_result:
                passing = False
                report.append('--- %s' % from_file)
                report.append('+++ %s' % to_file)
            if rule_report:
                report.append("Report for lines matching: '" + rule['re'] + "'")
                report.extend(rule_report)

        status = SCIATH_TEST_STATUS.ok if passing else SCIATH_TEST_STATUS.not_ok
        return status, report


def string_get_floats(line):
    r = []
    re_float = re.compile('[+-]?\d+.?\d*[eE]?[+-]?\d*')
    for word in line.split():
        match = re.search(re_float,word)
        if match:
            r.append(float(match.group()))
    return r


def compare_float_values_line(line_expected, line_out, abs_tol, rel_tol):
    assert abs_tol is not None or rel_tol is not None
    floats_expected = string_get_floats(line_expected.rstrip())
    floats_out = string_get_floats(line_out.rstrip())
    passing = True
    report = []
    if len(floats_expected) != len(floats_out):
        passing = False
        report.append('Wrong number of values found: %d instead of %d' % (len(floats_out), len(floats_expected)))
    else:
        for (float_expected, float_out) in zip(floats_expected, floats_out):
            if abs_tol is not None:
                abs_err = abs(float_out - float_expected)
                passing_abs = abs_err <= abs_tol
            if rel_tol is not None and (not abs_tol or not passing_abs):
                if float_expected == 0.0:  # allow to pass rtol an exact match of zero
                    rel_err = float('inf')
                    passing_rel = float_out == 0.0
                else:
                    rel_err = abs((float_out - float_expected)/float_expected)
                    passing_rel = rel_err <= rel_tol
            if (abs_tol is None or not passing_abs) and (rel_tol is None or not passing_rel):
                passing = False
                if abs_tol is not None and not passing_abs:
                     report.append('%g does not match expected %g to abs. tol. %g (abs. err %g)' % (float_out, float_expected, abs_tol, abs_err))
                if rel_tol is not None and not passing_rel:
                    report.append('%g does not match expected %g to rel. tol. %g (rel. err. %g)' % (float_out, float_expected, rel_tol, rel_err))
    return passing, report


def float_pairs_function(match_expected, match_out, abs_tol, rel_tol, max_err_count = 100):
    passing = True
    report = []
    err_count = 0
    if not match_expected:
        report.append('Expected file had no matches, so declaring failure')
        passing = False
        return passing, report
    for ((lineno_expected,line_expected), (lineno_out,line_out)) in zip(match_expected.items(), match_out.items()):
        line_passing, line_report = compare_float_values_line(line_expected, line_out, abs_tol, rel_tol)
        if not line_passing:
            passing = False
            report.append('Output line %d did not match line %d in expected output:' %(lineno_out, lineno_expected))
            report.extend(line_report)
            err_count = err_count + 1
            if err_count > max_err_count:
                report.append('Not checking any more lines after the first %d' % max_err_count)
    if len(match_expected) != len(match_out):
        passing = False
        report.append('Wrong number of matched lines: %d instead of %d' % (len(match_out), len(match_expected)))
    return passing, report


def key_and_float_rule(key, rel_tol=None, abs_tol=None):
    rel_tol_adjusted = 1e-6 if rel_tol is None and abs_tol is None else rel_tol
    rule = {}
    if key:
        rule['re'] = '^\s*'+re.escape(key) # match on lines starting with key after whitespace
    else:
        rule['re'] = '^' # match any line
    rule['function'] = lambda expected, output : float_pairs_function(expected, output, abs_tol, rel_tol_adjusted)
    return rule
