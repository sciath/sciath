#!/usr/bin/env python
import os
import errno

from sciath.launcher import Launcher
from sciath.test import Test
from sciath.job import Job
from sciath.task import Task

OUTPUT_PATH = os.path.join(os.getcwd(),'output')
VERBOSITY = 0
job_launcher = Launcher()
job_launcher.verbosity_level = VERBOSITY

def test_print(test, output_path):
    status,report = test.verifier.execute(output_path = output_path)
    rep = [test.name] + status
    print(rep)
    for l in report:
        print(l)

# Default verifier (check error code)
def test1(): # result: pass
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' , 'echo ""' ]

    t = Test(Job(Task(cmd), 'Test_1'))
    job_launcher.submit_job( t.job, output_path = OUTPUT_PATH )
    t.verify(output_path = OUTPUT_PATH)
    test_print(t, output_path = OUTPUT_PATH)
    return t

def test2(): # result: pass
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' ]

    t = Test( Job(Task(cmd), 'Test_2'))
    job_launcher.submit_job( t.job, output_path = OUTPUT_PATH )
    t.verify(output_path = OUTPUT_PATH)
    test_print(t, output_path = OUTPUT_PATH)
    return t

def test3(): # result: fail
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' ]

    t = Test(Job(Task(cmd), 'Test_3'))
    t.verifier.set_exit_codes_success([1])
    job_launcher.submit_job( t.job, output_path = OUTPUT_PATH )
    t.verify(output_path = OUTPUT_PATH)
    test_print(t, output_path = OUTPUT_PATH)
    return t

def test4(): # result: pass
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' ]

    t = Test(Job(Task(cmd), 'Test_4'))
    job_launcher.submit_job( t.job, output_path = OUTPUT_PATH )
    return t


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise


def main():
    mkdir_p(OUTPUT_PATH)

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
