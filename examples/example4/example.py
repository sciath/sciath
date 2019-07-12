#!/usr/bin/env python
import os
from sciath.test import Test
from sciath.harness import Harness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1():
  ranks = 1
  launch = './ex'
  expected_file = makeLocalPathAbsolute('ex.expected')

  def comparefunc(test):
    key = 'kspits'
    test.compareInteger(key,0)

    key = 'norm'
    test.compareFloatingPointAbsolute(key,1e-4)

  # Create test object
  test = Test('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def test2():
  ranks = 1
  launch = './ex'
  expected_file = makeLocalPathAbsolute('ex.expected2')

  def comparefunc(test):
    key = 'kspits'
    test.compareInteger(key,0)

    key = 'norm'
    test.compareFloatingPointAbsolute(key,1e-4)

  # Create test object
  test = Test('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def test3():
  ranks = 1
  launch = './ex'
  expected_file = makeLocalPathAbsolute('ex.expected3')

  def comparefunc(test):
    key = 'kspits'
    test.compareInteger(key,0)

    key = 'norm'
    test.compareFloatingPointAbsolute(key,1e-4)

  # Create test object
  test = Test('ex3',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  registeredTests = [ test1(), test2(), test3() ]

  os.system('gcc -o ex ' + makeLocalPathAbsolute('ex.c'))

  h = Harness(registeredTests)
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
