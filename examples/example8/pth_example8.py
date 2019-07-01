#!/usr/bin/env python
import os
import pyTestHarness.test as pthtest
import pyTestHarness.harness as pthharness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex')
  expected_file = 'ex.expected'

  def comparefuncSubTest(test):
    test.compareUnixDiff()

  # Create test object
  test = pthtest.Test('test1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefuncSubTest)
  test.appendKeywords('@')
  test.setUseSandbox()

  return(test)

def test1_clone():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex')
  expected_file = 'ex.expected'

  def comparefuncSubTest(test):
    test.compareUnixDiff()

  # Create test object
  test = pthtest.Test('test1_clone',ranks,launch,expected_file)
  test.setVerifyMethod(comparefuncSubTest)
  test.appendKeywords('@')
  test.setUseSandbox()

  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  os.system('gcc -o ex ex.c')

  # Register both tests, but immediately select a subset
  h = pthharness.Harness( \
          [test1(),test1_clone()],\
          ['test1']\
          ) 
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
