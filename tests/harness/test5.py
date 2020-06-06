#!/usr/bin/env python

# A test using a LineVerifier

import os

import sciath.harness
import sciath.test
import sciath.job
import sciath.verifier_line


this_dir = os.path.dirname(os.path.realpath(__file__))

command = ['echo','The first number is 1.1\nThe second number is 1.01']
job = sciath.job.Job(command)
test = sciath.test.Test(job,'test')
verifier = sciath.verifier_line.LineVerifier(test, expected_file = os.path.join(this_dir,'test5_data','test.expected'))
verifier.rules.append(sciath.verifier_line.key_and_float_rule('The first number is'))
verifier.rules.append(sciath.verifier_line.key_and_float_rule('The second number is'))
test.verifier = verifier

harness = sciath.harness.Harness([test])
harness.run_from_args()
