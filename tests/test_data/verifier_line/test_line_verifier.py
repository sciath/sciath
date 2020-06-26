#!/usr/bin/env python
import os
import errno

from sciath.launcher import Launcher
from sciath.test import Test
from sciath.job import Job
from sciath.task import Task
from sciath.verifier_line import LineVerifier, key_and_float_rule

this_dir = os.path.dirname(os.path.realpath(__file__))

def comparison_function(match_expected, match_out):
    """ Simply check that the same number of matches are found in expected and output files"""
    n_expected = len(match_expected)
    n_found = len(match_out)
    passing = n_found == n_expected
    report = [] if passing else ['Failure: Different numbers of matching lines found: %d instead of %d' % (n_found, n_expected)]
    return passing, report

def test1(output_path):
    cmd = ['printf' , '  key 1.0 2 -3.4 1e10\nx\n\n  key 1.0\n  key  \nkey\nkey 1e-10 3.0 4.0\n  key 1e-12\n']
    name = 'Line1'
    t = Test(Job(Task(cmd), name))
    v = LineVerifier(t, expected_file = os.path.join(this_dir,"expected"))
    v.rules.append({'re':'  key', 'function':comparison_function})
    t.verifier = v
    return t

# The same, but fails
def test2(output_path):
    cmd = ['printf' , 'should fail\nx\n\n  key 1.0\n  key  \nkey\nkey 1e-10 3.0 4.0\n  key 1e-12\n']
    name = 'Line2'
    t = Test(Job(Task(cmd), name))
    v = LineVerifier(t, expected_file = os.path.join(this_dir,"expected"))
    v.rules.append({'re':'  key', 'function':comparison_function})
    t.verifier = v
    return t

# Compare floats. Should pass with default tol
def test3(output_path):
    cmd = ['printf' , '  key 2.0 2 -3.4 1e10\nx\n\n  key 1.0\n  key  \nkey\nkey 1e-10 1.0 4.0\n  key 1e-12\n']
    name = 'Line3'
    t = Test(Job(Task(cmd), name))
    v = LineVerifier(t, expected_file = os.path.join(this_dir,"expected"))
    v.rules.append(key_and_float_rule('  key'))
    t.verifier = v
    return t

# Compare floats. Should fail
def test4(output_path):
    cmd = ['printf' , '  key 7.0 2 -3.4 1e10\nx\n\n  key 1.0\n  key  \nkey\nkey 1e10 1.0 4.0\n  key 1e-12\n']
    name = 'Line4'
    t = Test(Job(Task(cmd), name))
    v = LineVerifier(t, expected_file = os.path.join(this_dir,"expected"))
    v.rules.append(key_and_float_rule('  key'))
    t.verifier = v
    return t

# Compare floats. Should fail
def test5(output_path):
    cmd = ['printf' , '  key 2.0 2 -3.4 1e10\nx\n\n  key 1.0\n  key  \nkey\nkey 1e10 1.0 4.0\n  key 1e+12\n']
    name = 'Line5'
    t = Test(Job(Task(cmd), name))
    v = LineVerifier(t, expected_file = os.path.join(this_dir,"expected"))
    v.rules.append(key_and_float_rule('  key'))
    t.verifier = v
    return t


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise


def main():
    output_path = os.path.join(os.getcwd(),'output')
    mkdir_p(output_path)

    launcher = Launcher()
    for t in [test1(output_path), test2(output_path), test3(output_path), test4(output_path), test5(output_path)]:
        launcher.submit_job(t.job, output_path = output_path)
        status, report = t.verify(output_path = output_path) # only makes sense if submit_job blocks
        print(status)
        for line in report:
            print(line)


if __name__ == "__main__":
    main()
