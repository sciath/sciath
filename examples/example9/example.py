#!/usr/bin/env python
import os
from sciath.test import Test
from sciath.harness import Harness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def testAbs():
  ranks = 1
  launch = makeLocalPathAbsolute('./run.sh')
  expected_file = makeLocalPathAbsolute('expected')

  def comparefunc(test):
    key = "datum"
    tol = 1e-5;
    test.compareFloatingPointAbsolute(key,tol);

  test = Test('testAbs',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)

  return(test)

def testRel():
  ranks = 1
  launch = makeLocalPathAbsolute('./run.sh')
  expected_file = makeLocalPathAbsolute('expected')

  def comparefunc(test):
    key = "datum"
    tol = 1e-5;
    test.compareFloatingPointRelative(key,tol);

  test = Test('testRel',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)

  return(test)

def testRelEpsilon():
  ranks = 1
  launch = makeLocalPathAbsolute('./run.sh')
  expected_file = makeLocalPathAbsolute('expected')

  def comparefunc(test):
    key = "datum"
    tol = 1e-5;
    epsilon = 1e-10
    test.compareFloatingPointRelative(key,tol,epsilon);

  test = Test('testRelEpsilon',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)

  return(test)

def run_tests():

  h = Harness([
      testAbs(),
      testRel(),
      testRelEpsilon()
  ])
  h.setUseSandbox()
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
