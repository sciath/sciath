import os
import re
import shutil

from sciath.verifier import ComparisonVerifier
from sciath import sciath_test_status


class LineVerifier(ComparisonVerifier):

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

        status = sciath_test_status.ok if passing else sciath_test_status.not_ok
        return status, report

# Helper functions to generate rules

# Developer note: the below is largely a proof of concept and is likely to change.

def string_get_floats(line):
    r = []
    re_float = re.compile('[+-]?\d+.?\d*[eE]?[+-]?\d*')
    for word in line.split():
        match = re.search(re_float,word)
        if match:
            r.append(float(match.group()))
    return r


def compare_float_values_rel(line_expected, line_out, rel_tol):
    floats_expected = string_get_floats(line_expected.rstrip())
    floats_out = string_get_floats(line_out.rstrip())
    passing = True
    report = []
    for (float_expected, float_out) in zip(floats_expected, floats_out):
        if float_expected == 0.0:
            if float_out != 0.0:
                passing = False
                report.append('expected value of 0.0 must be matched exactly')
        elif abs(float_out - float_expected)/abs(float_expected) > rel_tol:
             passing = False
             report.append('expected value of %g does not match output value %g to rel. tol. %g' % (float_expected, float_out, rel_tol))
    if len(floats_expected) != len(floats_out):
        passing = False
        report.append('Wrong number of values found: %d instead of %d' % (len(floats_out), len(floats_expected)))
    return passing, report


def float_rel_pairs_function(match_expected, match_out, rel_tol, max_err_count = 100):
    passing = True
    report = []
    err_count = 0
    for ((lineno_expected,line_expected), (lineno_out,line_out)) in zip(match_expected.items(), match_out.items()):
        line_passing, line_report = compare_float_values_rel(line_expected, line_out, rel_tol)
        if not line_passing:
            passing = False
            report.append('(l.' + str(lineno_expected) + '/' + str(lineno_out) + ') Lines did not match:')
            report.extend(line_report)

            err_count = err_count + 1
            if err_count > max_err_count:
                report.append('Not checking any more lines after the first %d' % max_err_count)
    if len(match_expected) != len(match_out):
        passing = False
        report.append('Wrong number of matched lines: %d instead of %d' % (len(match_out), len(match_expected)))
    return passing, report


def key_and_float_rule(key,rel_tol=1e-6):
    rule = {}
    if key:
        rule['re'] = '^'+re.escape(key) # match on lines starting with key
    else:
        rule['re'] = '^' # match any line
    rule['function'] = lambda e,o : float_rel_pairs_function(e,o,rel_tol=rel_tol)
    return rule
