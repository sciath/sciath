""" SciATH LineVerifier class """
import re
import collections

from sciath.verifier import ComparisonVerifier


class LineVerifier(ComparisonVerifier):
    """ An Verifier which compares sets of lines from expected and output files

        This is accomplished by defining a set of "rules". Each rule contains
        a regular expression to determine which lines to match, and a function
        to determine success when comparing the the set of matching lines
        from the two files.
    """

    def __init__(self, test, expected_file, output_file=None, comparison_file=None):
        super(LineVerifier, self).__init__(test, expected_file, output_file,
                                           comparison_file)
        self.rules = []

    def _compare_files(self, from_file, to_file):
        report = []
        passing = True
        for rule in self.rules:
            match_from = collections.OrderedDict()
            match_to = collections.OrderedDict()
            for match, source_file in [(match_from, from_file), (match_to, to_file)]:
                with open(source_file, 'r') as handle:
                    for line_number, line in enumerate(handle.readlines(), 1):
                        if re.match(rule['re'], line):
                            match[line_number] = line
            rule_passing, rule_report = rule['function'](match_from, match_to)
            if passing and not rule_passing:
                passing = False
                report.append('--- %s' % from_file)
                report.append('+++ %s' % to_file)
            if rule_report:
                report.append("Report for lines matching: '" + rule['re'] + "'")
                report.extend(rule_report)
        return passing, report


def string_get_floats(line):
    """ Extracts floating point numbers from a string """
    result = []
    re_float = re.compile(r'[+-]?\d+.?\d*[eE]?[+-]?\d*')
    for word in line.split():
        match = re.search(re_float, word)
        if match:
            result.append(float(match.group()))
    return result


def compare_float_values_line(line_expected, line_out, abs_tol, rel_tol):
    """ Compares floating point numbers on a pair of lines """
    assert abs_tol is not None or rel_tol is not None
    floats_expected = string_get_floats(line_expected.rstrip())
    floats_out = string_get_floats(line_out.rstrip())
    passing = True
    report = []
    if len(floats_expected) != len(floats_out):
        passing = False
        report.append('Wrong number of values found: %d instead of %d' %
                      (len(floats_out), len(floats_expected)))
    else:
        for (float_expected, float_out) in zip(floats_expected, floats_out):
            if abs_tol is not None:
                abs_err = abs(float_out - float_expected)
                passing_abs = abs_err <= abs_tol
            if rel_tol is not None and (abs_tol is None or not passing_abs):
                if float_expected == 0.0:  # allow to pass rtol an exact match of zero
                    rel_err = float('inf')
                    passing_rel = float_out == 0.0
                else:
                    rel_err = abs((float_out - float_expected) / float_expected)
                    passing_rel = rel_err <= rel_tol
            if (abs_tol is None or not passing_abs) and (rel_tol is None or not passing_rel):
                passing = False
                if abs_tol is not None and rel_tol is not None:
                    report.append(
                        '%g != %g to abs. tol. %g (abs. err %g) or rel. tol %g (rel. err %g)'
                        % (float_out, float_expected, abs_tol, abs_err, rel_tol, rel_err))
                elif abs_tol is not None:
                    report.append(
                        '%g != %g to abs. tol. %g (abs. err %g)'
                        % (float_out, float_expected, abs_tol, abs_err))
                else:
                    report.append(
                        '%g != %g to rel. tol. %g (rel. err. %g)'
                        % (float_out, float_expected, rel_tol, rel_err))
    return passing, report


def float_pairs_function(match_expected,
                         match_out,
                         abs_tol,
                         rel_tol,
                         max_err_count=100):
    """ Compares all floating point numbers, looking for abs. or rel. tol """
    passing = True
    report = []
    err_count = 0
    if not match_expected:
        report.append('Expected file had no matches, so declaring failure')
        passing = False
        return passing, report
    for ((lineno_expected, line_expected),
         (lineno_out, line_out)) in zip(match_expected.items(), match_out.items()):
        line_passing, line_report = compare_float_values_line(
            line_expected, line_out, abs_tol, rel_tol)
        if not line_passing:
            passing = False
            report.append(
                'Output line %d did not match line %d in expected output:' %
                (lineno_out, lineno_expected))
            report.extend(line_report)
            err_count = err_count + 1
            if err_count > max_err_count:
                report.append('Not checking any more lines after the first %d' %
                              max_err_count)
    if len(match_expected) != len(match_out):
        passing = False
        report.append('Wrong number of matched lines: %d instead of %d' %
                      (len(match_out), len(match_expected)))
    return passing, report


def key_and_float_rule(key=None, rel_tol=None, abs_tol=None):
    """ A rule to match lines starting with a key, comparing all numbers as floats

        Preceding whitespace is accepted in matching the key. If the key is
        not provided, all lines are matched.
    """
    rel_tol_adjusted = 1e-6 if rel_tol is None and abs_tol is None else rel_tol
    rule = {}
    if key:
        rule['re'] = r'^\s*' + re.escape(key)
    else:
        rule['re'] = r'^'  # match any line
    rule['function'] = lambda expected, output: float_pairs_function(
        expected, output, abs_tol, rel_tol_adjusted)
    return rule
