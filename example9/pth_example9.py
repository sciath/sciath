#!/usr/bin/env python
import os
import pyTestHarness.test as pthtest
import pyTestHarness.harness as pthharness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def testAbs():
  ranks = 1
  launch = makeLocalPathAbsolute('./run.sh')
  expected_file = 'expected'

  def comparefunc(test):
    key = "datum"
    tol = 1e-5;
    test.compareFloatingPointAbsolute(key,tol);

  test = pthtest.Test('testAbs',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.setUseSandbox()

  return(test)

def testRel():
  ranks = 1
  launch = makeLocalPathAbsolute('./run.sh')
  expected_file = 'expected'

  def comparefunc(test):
    key = "datum"
    tol = 1e-5;
    test.compareFloatingPointRelative(key,tol);

  test = pthtest.Test('testRel',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.setUseSandbox()

  return(test)

def testRelEpsilon():
  ranks = 1
  launch = makeLocalPathAbsolute('./run.sh')
  expected_file = 'expected'

  def comparefunc(test):
    key = "datum"
    tol = 1e-5;
    epsilon = 1e-10
    test.compareFloatingPointRelative(key,tol,epsilon);

  test = pthtest.Test('testRelEpsilon',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.setUseSandbox()

  return(test)

def run_tests():

  h = pthharness.Harness([
      testAbs(),
      testRel(),
      testRelEpsilon()
  ])
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
