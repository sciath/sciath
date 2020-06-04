import os
import re

from sciath.verifier import Verifier
from sciath import sciath_test_status

class VerifierLine(Verifier):

    def __init__(self, test, expected_file, output_file = None):
      Verifier.__init__(self, test)
      self.expected_file = expected_file
      c_name, o_name, e_name = self.test.job.get_output_filenames()
      if output_file is None:
          self.output_file = o_name[-1]
      self.rules = []

    def execute(self, output_path, exec_path = None):
        passing = True
        report = ''
        for rule in self.rules:

            if not os.path.isfile(self.expected_file):
                status = sciath_test_status.expected_file_not_found
                break
            output_file_full = os.path.join(output_path,self.output_file)
            if not os.path.isfile(output_file_full):
                status = sciath_test_status.output_file_not_found
                break
            match_out = {}
            match_expected = {}
            for [match, filename] in [(match_out, output_file_full),(match_expected,self.expected_file)]:
                with open(filename,'r') as f:
                    line_number = 0
                    for line in f.readlines():
                        line_number = line_number + 1
                        if re.match(rule['re'],line):
                            match[line_number] = line
            rule_result, rule_report  = rule['function'](match_expected, match_out)
            passing = passing and rule_result
            if rule_report:
                report = report + 'Report for lines matching: \'' + rule['re'] + '\'\n'
                report = report + rule_report

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
    floats_out      = string_get_floats(line_out.rstrip())
    passing = True
    report = ''
    for (float_expected, float_out) in zip(floats_expected, floats_out):
        if float_expected == 0.0 and float_out != 0.0:
            passing = False
            report = report + 'expected value of 0.0 must be matched exactly (not checking the rest of the line)\n'
            break
        if abs(float_out - float_expected)/abs(float_expected) > rel_tol:
             passing = False
             report = report + 'expected value of ' + str(float_expected) + ' does not match output value ' + str(float_out) + ' to relative tolerance ' + str(rel_tol)
             break
    if passing and len(floats_expected) != len(floats_out):
        passing = False
        report = report + 'Wrong number of values found: ' + len(floats_out) + ' instead of ' + len(floats_expected)
    return passing, report

def float_rel_pairs_function(match_expected, match_out, rel_tol, max_err_count = 100):
    passing = True
    report = ''
    err_count = 0
    for ((lineno_expected,line_expected), (lineno_out,line_out)) in zip(match_expected.items(), match_out.items()):
        line_passing, line_report = compare_float_values_rel(line_expected, line_out, rel_tol)
        if not line_passing:
            passing = False
            report = report + '(l.' + str(lineno_expected) + '/' + str(lineno_out) + ') Lines did not match: ' + line_report

            err_count = err_count + 1
            if err_count > max_err_count:
                report = report + 'Not checking any more lines after the first ' + max_err_count + '\n'
    if len(match_expected) != len(match_out):
        passing = False
        report = report + 'Output and expected had different numbers of matches. Expected ' + len(match_expected) + ' but found ' + len(match_out) + '\n'
    return passing, report

def key_and_float_rule(key,rel_tol=1e-6):
    rule = {}
    rule['re'] = '^'+re.escape(key) # match on lines starting with key
    rule['function'] = lambda e,o : float_rel_pairs_function(e,o,rel_tol=rel_tol)
    return rule