#!/usr/bin/env python
import os
from sciath.test import Test
from sciath.harness import Harness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex')
  expected_file = makeLocalPathAbsolute('ex.expected')

  def comparefuncSubTest(test):
    test.compareUnixDiff()

  # Create test object
  test = Test('test1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefuncSubTest)
  test.appendKeywords('@')
  test.setUseSandbox()

  return(test)

def test1_clone():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex')
  expected_file = makeLocalPathAbsolute('ex.expected')

  def comparefuncSubTest(test):
    test.compareUnixDiff()

  # Create test object
  test = Test('test1_clone',ranks,launch,expected_file)
  test.setVerifyMethod(comparefuncSubTest)
  test.appendKeywords('@')
  test.setUseSandbox()

  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  os.system('gcc -o ' + makeLocalPathAbsolute('ex') + ' ' + makeLocalPathAbsolute('ex.c'))

  # Register both tests, but immediately select a subset
  h = Harness( \
          [test1(),test1_clone()],\
          ['test1']\
          )
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
