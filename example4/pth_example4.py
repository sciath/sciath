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

  def comparefunc(test):
    key = 'kspits'
    test.compareInteger(key,0)

    key = 'norm'
    test.compareFloatingPoint(key,1e-4)

  # Create test object
  test = pthtest.Test('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def test2():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex')
  expected_file = 'ex.expected2'

  def comparefunc(test):
    key = 'kspits'
    test.compareInteger(key,0)

    key = 'norm'
    test.compareFloatingPoint(key,1e-4)

  # Create test object
  test = pthtest.Test('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def test3():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex')
  expected_file = 'ex.expected3'

  def comparefunc(test):
    key = 'kspits'
    test.compareInteger(key,0)

    key = 'norm'
    test.compareFloatingPoint(key,1e-4)

  # Create test object
  test = pthtest.Test('ex3',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  registeredTests = [ test1(), test2(), test3() ]

  os.system('gcc -o ex ex.c')

  h = pthharness.Harness(registeredTests)
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
