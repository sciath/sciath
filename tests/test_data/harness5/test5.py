#!/usr/bin/env python

import os

import sciath.harness
import sciath.test
import sciath.job
import sciath.task
import sciath.verifier_line

this_dir = os.path.dirname(os.path.realpath(__file__))

command = ['printf', 'The first number is 1.1\nThe second number is 1.01\n']
task = sciath.task.Task(command)
job = sciath.job.Job(task)
test = sciath.test.Test(job, 'test')
verifier = sciath.verifier_line.LineVerifier(test,
                                             expected_file=os.path.join(
                                                 this_dir, 'test.expected'))
verifier.rules.append(
    sciath.verifier_line.key_and_float_rule('The first number is'))
verifier.rules.append(
    sciath.verifier_line.key_and_float_rule('The second number is'))
test.verifier = verifier

harness = sciath.harness.Harness([test])
harness.run_from_args()
