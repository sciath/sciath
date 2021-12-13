#!/usr/bin/env python
import os
import errno

from sciath.launcher import Launcher
from sciath.test import Test
from sciath.job import Job
from sciath.task import Task
from sciath.verifier import ComparisonVerifier
from sciath._sciath_io import command_join

this_dir = os.path.dirname(os.path.realpath(__file__))

OUTPUT_PATH = os.path.join(os.getcwd(), 'output')
EXEC_PATH = os.getcwd()
job_launcher = Launcher()


def test_print_pre(test, exec_path, launch_command):
    print("[%s] Executing from %s" % (test.job.name, exec_path))
    print(command_join(launch_command))


def test_print_post(test, output_path):
    passing, info, report = test.verifier.execute(output_path=output_path)
    print('[%s] %r %s' % (test.name, passing, info))
    for line in report:
        print(line)


def test1_ud():  # result: pass
    cmd = ['sh', os.path.join(this_dir, 'write_test1_ud.sh')]

    t = Test(Job(Task(cmd), 'Test_1_ud'))
    t.verifier = ComparisonVerifier(t, os.path.join(this_dir, "t1.expected"))

    success, info, report, data = job_launcher.prepare_job(
        t.job, output_path=OUTPUT_PATH, exec_path=EXEC_PATH)
    test_print_pre(t, exec_path=EXEC_PATH, launch_command=data.launch_command)
    job_launcher.submit_job(data)
    t.verify(output_path=OUTPUT_PATH)
    test_print_post(t, output_path=OUTPUT_PATH)
    return t


def test2_ud():  # result: fail
    cmd = ['sh', os.path.join(this_dir, 'write_test2_ud.sh')]

    t = Test(Job(Task(cmd), 'Test_2_ud'))
    t.verifier = ComparisonVerifier(t, os.path.join(this_dir, "t1.expected"))

    success, info, report, data = job_launcher.prepare_job(
        t.job, output_path=OUTPUT_PATH, exec_path=EXEC_PATH)
    test_print_pre(t, exec_path=EXEC_PATH, launch_command=data.launch_command)
    job_launcher.submit_job(data)
    t.verify(output_path=OUTPUT_PATH)
    test_print_post(t, output_path=OUTPUT_PATH)
    return t


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def main():
    mkdir_p(OUTPUT_PATH)

    # test using unix-diff verifierr
    t1_ud = test1_ud()
    t2_ud = test2_ud()

    # clean up
    clean_up = False
    if clean_up:
        for t in [t1_ud, t2_ud]:
            job_launcher.clean(t.job, output_path=OUTPUT_PATH)


main()
