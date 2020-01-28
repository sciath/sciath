#!/usr/bin/env python
import os

from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.launcher import Launcher
from sciath.test import Test
from sciath.verifier_unixdiff import VerifierUnixDiff

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

# Default verifier (check error code)
def test1(): # result: pass
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' , 'echo ""' ]

    t = Test(Job(cmd, 'Test_1'))
    job_launcher.submitJob( t.job, output_path = OUTPUT_PATH )
    t.verify(output_path = OUTPUT_PATH)
    test_print(t, output_path = OUTPUT_PATH)
    return t

def test2(): # result: pass
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' ]

    t = Test( Job(cmd, 'Test_2'))
    job_launcher.submitJob( t.job, output_path = OUTPUT_PATH )
    t.verify(output_path = OUTPUT_PATH)
    test_print(t, output_path = OUTPUT_PATH)
    return t

def test3(): # result: fail
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' ]

    t = Test(Job(cmd, 'Test_3', exitCode = 1))
    job_launcher.submitJob( t.job, output_path = OUTPUT_PATH )
    t.verify(output_path = OUTPUT_PATH)
    test_print(t, output_path = OUTPUT_PATH)
    return t

def test4(): # result: pass
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' ]

    t = Test(Job(cmd, 'Test_4'))
    job_launcher.submitJob( t.job, output_path = OUTPUT_PATH )
    return t



def main():
    try:
        os.mkdir(OUTPUT_PATH)
    except:
        pass

    # test using default verifier
    t1 = test1()
    t2 = test2()
    t3 = test3()

    # test with staged submit/verify
    t4 = test4()
    t4.verify(output_path = OUTPUT_PATH)
    test_print(t4, output_path = OUTPUT_PATH)
    job_launcher.clean(t4.job, output_path = OUTPUT_PATH)

    tests = [t1,t2,t3,t4]
    for t in tests:
        job_launcher.clean(t.job, output_path = OUTPUT_PATH)


main()
