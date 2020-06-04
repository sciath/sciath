#!/usr/bin/env python
import os

from sciath.job import Job
from sciath.launcher import Launcher
from sciath.test import Test
from sciath.verifier_line import VerifierLine, key_and_float_rule

this_dir = os.path.dirname(os.path.realpath(__file__))

def comparison_function(match_expected, match_out):
    """ Simply check that the same number of matches are found in expected and output files"""
    n_expected = len(match_expected)
    n_found = len(match_out)
    passing = n_found == n_expected
    report = None if passing else 'Failure: Different numbers of matching lines found: ' + str(n_expected) + ' expected but ' + str(n_found) + ' found'
    return passing, report

def test1(output_path):
    cmd = ['printf' , '  key 1.0 2 -3.4 1e10\nx\n\n  key 1.0\n  key  \nkey\nkey 1e-10 3.0 4.0\n  key 1e-12\n']
    name = 'Line1'
    t = Test(Job(cmd, name))
    v = VerifierLine(t, expected_file = os.path.join(this_dir,"./expected/line1.expected"))
    v.rules.append({'re':'  key', 'function':comparison_function})
    t.verifier = v
    return t

# The same, but fails
def test2(output_path):
    cmd = ['printf' , 'should fail\nx\n\n  key 1.0\n  key  \nkey\nkey 1e-10 3.0 4.0\n  key 1e-12\n']
    name = 'Line2'
    t = Test(Job(cmd, name))
    v = VerifierLine(t, expected_file = os.path.join(this_dir,"./expected/line1.expected"))
    v.rules.append({'re':'  key', 'function':comparison_function})
    t.verifier = v
    return t

# Compare floats. Should pass with default tol
def test3(output_path):
    cmd = ['printf' , '  key 2.0 2 -3.4 1e10\nx\n\n  key 1.0\n  key  \nkey\nkey 1e-10 1.0 4.0\n  key 1e-12\n']
    name = 'Line3'
    t = Test(Job(cmd, name))
    v = VerifierLine(t, expected_file = os.path.join(this_dir,"./expected/line1.expected"))
    v.rules.append(key_and_float_rule('  key'))
    t.verifier = v
    return t

# Compare floats. Should fail
def test4(output_path):
    cmd = ['printf' , '  key 7.0 2 -3.4 1e10\nx\n\n  key 1.0\n  key  \nkey\nkey 1e10 1.0 4.0\n  key 1e-12\n']
    name = 'Line4'
    t = Test(Job(cmd, name))
    v = VerifierLine(t, expected_file = os.path.join(this_dir,"./expected/line1.expected"))
    v.rules.append(key_and_float_rule('  key'))
    t.verifier = v
    return t

# Compare floats. Should fail
def test5(output_path):
    cmd = ['printf' , '  key 2.0 2 -3.4 1e10\nx\n\n  key 1.0\n  key  \nkey\nkey 1e10 1.0 4.0\n  key 1e+12\n']
    name = 'Line5'
    t = Test(Job(cmd, name))
    v = VerifierLine(t, expected_file = os.path.join(this_dir,"./expected/line1.expected"))
    v.rules.append(key_and_float_rule('  key'))
    t.verifier = v
    return t

def main():
    output_path = os.path.join(os.getcwd(),'output')
    os.makedirs(output_path, exist_ok = True)

    launcher = Launcher()
    for t in [test1(output_path), test2(output_path), test3(output_path), test4(output_path), test5(output_path)]:
        launcher.submitJob(t.job, output_path = output_path)
        status, report = t.verify(output_path = output_path) # only makes sense if submitJob blocks
        print(status)
        print(report)


if __name__ == "__main__":
    main()
