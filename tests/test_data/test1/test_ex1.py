#!/usr/bin/env python
import os
import errno

from sciath.launcher import Launcher
from sciath.test import Test
from sciath.job import Job
from sciath.task import Task
from sciath._sciath_io import command_join

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


# Default verifier (check error code)
def test1():  # result: pass
    cmd = ['printf', '"aBc\nkspits=30\n"']

    t = Test(Job(Task(cmd), 'Test_1'))
    success, info, report, data = job_launcher.prepare_job(
        t.job, output_path=OUTPUT_PATH, exec_path=EXEC_PATH)
    test_print_pre(t, exec_path=EXEC_PATH, launch_command=data.launch_command)
    job_launcher.submit_job(data)
    t.verify(output_path=OUTPUT_PATH)
    test_print_post(t, output_path=OUTPUT_PATH)
    return t


def test2():  # result: pass
    cmd = ['printf', 'aBc\nkspits=30\n']

    t = Test(Job(Task(cmd), 'Test_2'))
    success, info, report, data = job_launcher.prepare_job(
        t.job, output_path=OUTPUT_PATH, exec_path=EXEC_PATH)
    test_print_pre(t, exec_path=EXEC_PATH, launch_command=data.launch_command)
    job_launcher.submit_job(data)
    t.verify(output_path=OUTPUT_PATH)
    test_print_post(t, output_path=OUTPUT_PATH)
    return t


def test3():  # result: fail
    cmd = ['printf', 'aBc\nkspits=30\n']

    t = Test(Job(Task(cmd), 'Test_3'))
    t.verifier.set_exit_codes_success([1])
    success, info, report, data = job_launcher.prepare_job(
        t.job, output_path=OUTPUT_PATH, exec_path=EXEC_PATH)
    test_print_pre(t, exec_path=EXEC_PATH, launch_command=data.launch_command)
    job_launcher.submit_job(data)
    t.verify(output_path=OUTPUT_PATH)
    test_print_post(t, output_path=OUTPUT_PATH)
    return t


def test4():  # result: pass
    cmd = ['printf', 'aBc\nkspits=30\n']

    t = Test(Job(Task(cmd), 'Test_4'))
    success, info, report, data = job_launcher.prepare_job(
        t.job, output_path=OUTPUT_PATH, exec_path=EXEC_PATH)
    test_print_pre(t, exec_path=EXEC_PATH, launch_command=data.launch_command)
    job_launcher.submit_job(data)
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

    # test using default verifier
    t1 = test1()
    t2 = test2()
    t3 = test3()

    # test with staged submit/verify
    t4 = test4()
    t4.verify(output_path=OUTPUT_PATH)
    test_print_post(t4, output_path=OUTPUT_PATH)

    # Clean up after all jobs
    for t in (t1, t2, t3, t4):
        job_launcher.clean(t.job, output_path=OUTPUT_PATH)


main()
