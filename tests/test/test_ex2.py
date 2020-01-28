#!/usr/bin/env python
import os

from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.launcher import Launcher
from sciath.test import Test
from sciath.verifier_unixdiff import VerifierUnixDiff

this_dir = os.path.dirname(os.path.realpath(__file__))

OUTPUT_PATH = os.path.join(os.getcwd(),'output')
VERBOSITY = 0
job_launcher = Launcher()
job_launcher.setVerbosityLevel(VERBOSITY)

def test_print(test, output_path):
    status,report = test.verifier.execute(output_path = output_path)
    rep = [test.name] + status
    print(rep)
    for l in report:
        print(l)

def test1_ud(): # result: pass
    cmd = ['sh' , os.path.join(this_dir,'write_test1_ud.sh') ]

    t = Test(Job(cmd, 'Test_1_ud'))
    t.verifier = VerifierUnixDiff(t, os.path.join(this_dir,"./expected/t1.expected"))

    job_launcher.submitJob( t.job, output_path = OUTPUT_PATH, exec_path = OUTPUT_PATH )
    t.verify(output_path = OUTPUT_PATH)
    test_print(t, output_path = OUTPUT_PATH)
    return t

def test2_ud(): # result: fail
    cmd = ['sh' , os.path.join(this_dir,'write_test2_ud.sh') ]

    t = Test(Job(cmd, 'Test_2_ud'))
    t.verifier = VerifierUnixDiff(t, os.path.join(this_dir,"./expected/t1.expected"))

    job_launcher.submitJob( t.job, output_path = OUTPUT_PATH, exec_path = OUTPUT_PATH )
    t.verify(output_path = OUTPUT_PATH)
    test_print(t, output_path = OUTPUT_PATH)
    return t


def main():
    try:
        os.mkdir(OUTPUT_PATH)
    except:
        pass

    # test using unix-diff verifierr
    t1_ud = test1_ud()
    t2_ud = test2_ud()

    # clean up
    clean_up = False
    if clean_up:
        for t in [t1_ud,t2_ud]:
            job_launcher.clean(t.job, output_path = OUTPUT_PATH)

main()
