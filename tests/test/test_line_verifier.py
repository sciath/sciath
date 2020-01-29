#!/usr/bin/env python
import os

from sciath.job import Job
from sciath.launcher import Launcher
from sciath.test import Test
from sciath.verifier_line import VerifierLine

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

def main():
    output_path = os.path.join(os.getcwd(),'output')
    try:
        os.mkdir(output_path)
    except:
        pass

    launcher = Launcher()
    for t in [test1(output_path), test2(output_path)]:
        launcher.submitJob(t.job, output_path = output_path) # only makes sense on local machine
        status, report = t.verify(output_path = output_path)
        print(status)
        print(report)


if __name__ == "__main__":
    main()
