#!/usr/bin/env python
import os
import pyTestHarness.unittest as pth
import pyTestHarness.harness as harness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex1')
  expected_file = 'ex1.expected'

  def comparefunc(unittest):
    key = '\$cputime'
    unittest.compareFloatingPoint(key,0.01)

    key = '\$residuals'
    unittest.compareFloatingPoint(key,0.000001)

    key = 'kspits'
    unittest.compareInteger(key,0)

    key = '\$norm'
    unittest.compareFloatingPoint(key,0.01)

    key = '\$rms'
    unittest.compareFloatingPoint(key,0.01)

  # Create unit test object
  test = pth.pthUnitTest('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def test2():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex2')
  expected_file = 'ex2.expected'
  def comparefunc(unittest):
    key = 'Residuals'
    unittest.compareFloatingPoint(key,0.0001)

  # Create unit test object
  test = pth.pthUnitTest('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  test.setComparisonFile('ex2-residual.log')

  return(test)

def test3():
  ranks = 1
  launch = 'echo' # produce no output
  expected_file = 'ex3.expected'

  def comparefunc(unittest):
    key = 'kspit'
    unittest.compareInteger(key,0)

    key = 'res1'
    unittest.compareFloatingPoint(key,1.0e-4)

  # Create unit test object
  test = pth.pthUnitTest('ex3',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)

  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  registeredTests = [ test1() , test2(), test3() ]

  os.system('gcc -o ex1 ex1.c')
  os.system('gcc -o ex2 ex2.c')

  h = harness.pthHarness(registeredTests)
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
