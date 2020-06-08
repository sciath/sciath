#!/usr/bin/env python

# "Command line" use of the Harness, with all tests passing

from sciath.harness import Harness
from sciath.test import Test
from sciath.job import Job

test1 = Test(Job(['echo','Hello, I am Test #1']),'test1')
test2 = Test(Job(['printf','Hello, I am Test #2\n']),'test2')
test_list = [test1,test2]

harness = Harness(test_list)
harness.run_from_args()
