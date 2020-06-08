#!/usr/bin/env python

# "Command line" use of the Harness

from sciath.harness import Harness
from sciath.test import Test
from sciath.job import Job

test1 = Test(Job(['echo','Hello, I am Test #1']),'test1')
test2 = Test(Job(['printf','Hello, I am Test #2\n']),'test2')
test3 = Test(Job(['touch','test3.dat']),'test3')
test4 = Test(Job(['grep','foo','bar']),'test4') # should fail
test_list = [test1,test2,test3,test4]

harness = Harness(test_list)
harness.run_from_args()
