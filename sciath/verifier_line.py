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
