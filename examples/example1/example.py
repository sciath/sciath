#!/usr/bin/env python
import os
from sciath.test import Test
from sciath.harness import Harness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex1')
  expected_file = makeLocalPathAbsolute('ex1.expected')

  def comparefunc(test):
    key = '\$cputime'
    test.compareFloatingPointAbsolute(key,0.01)

    key = '\$residuals'
    test.compareFloatingPointAbsolute(key,0.000001)

    key = 'kspits'
    test.compareInteger(key,0)

    key = '\$norm'
    test.compareFloatingPointAbsolute(key,0.01)

    key = '\$rms'
    test.compareFloatingPointAbsolute(key,0.01)

  # Create test object
  test = Test('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def test2():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex2')
  expected_file = makeLocalPathAbsolute('ex2.expected')
  def comparefunc(test):
    key = 'Residuals'
    test.compareFloatingPointAbsolute(key,0.0001)

  # Create test object
  test = Test('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  test.setComparisonFile('ex2-residual.log')

  return(test)

def test3():
  ranks = 1
  launch = 'echo' # produce no output
  expected_file = makeLocalPathAbsolute('ex3.expected')

  def comparefunc(test):
    key = 'kspit'
    test.compareInteger(key,0)

    key = 'res1'
    test.compareFloatingPointAbsolute(key,1.0e-4)

  # Create test object
  test = Test('ex3',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)

  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  registeredTests = [ test1() , test2(), test3() ]

  os.system('gcc -o ' + makeLocalPathAbsolute('ex1') + ' ' + makeLocalPathAbsolute('ex1.c'))
  os.system('gcc -o ' + makeLocalPathAbsolute('ex2') + ' ' + makeLocalPathAbsolute('ex2.c'))

  h = Harness(registeredTests)
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
