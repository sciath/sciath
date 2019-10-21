#!/usr/bin/env python
# An example where an executable creates an output file with a standardized name
# (perhaps not good software practice but common, and can happen unintentionally)
# This example is run using individual "sandboxes" (recommended)
#
# Note: We define executables relative to the absolute path of this file

import os
from sciath.test import Test
from sciath.harness import Harness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1() :
  ranks = 1
  launch = makeLocalPathAbsolute('ex.sh') + ' 1'
  expected_file = makeLocalPathAbsolute('ex1.expected')

  def comparefunc(test):
    key = 'testkey'
    test.compareInteger(key,0)

  test = Test('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.setComparisonFile('out.txt')

  return(test)

def test2():
  ranks = 1
  launch = makeLocalPathAbsolute('ex.sh') + ' 2'
  expected_file = makeLocalPathAbsolute('ex2.expected')

  def comparefunc(test):
    key = 'testkey'
    test.compareInteger(key,0)

  test = Test('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.setComparisonFile('out.txt')

  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  registeredTests = [test1(), test2()]

  h = Harness(registeredTests)
  h.setUseSandbox()
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
