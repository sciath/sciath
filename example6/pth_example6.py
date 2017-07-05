#!/usr/bin/env python
# An example where an executable creates an output file with a standardized name
# (perhaps not good software practice but common, and can happen unintentionally)
# Run this example with the -s flag to execute each test in its own "sandbox"
#
# Note: We define executables relative to the absolute path of this file

import os
import pyTestHarness.unittest as pth
import pyTestHarness.harness as harness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1() :
  ranks = 1
  launch = makeLocalPathAbsolute('ex.sh') + ' 1'
  expected_file = 'ex1.expected'

  def comparefunc(unittest):
    key = 'testkey'
    unittest.compareInteger(key,0)

  test = pth.pthUnitTest('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.setComparisonFile('out.txt')

  return(test)

def test2():
  ranks = 1
  launch = makeLocalPathAbsolute('ex.sh') + ' 2'
  expected_file = 'ex2.expected'

  def comparefunc(unittest):
    key = 'testkey'
    unittest.compareInteger(key,0)

  test = pth.pthUnitTest('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.setComparisonFile('out.txt')

  return(test)

def run_example6():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  registered_tests = [test1(), test2()] 

  h = harness.pthHarness(registered_tests)
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_example6()
