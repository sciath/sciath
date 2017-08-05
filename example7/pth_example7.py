#!/usr/bin/env python
import os
import pyTestHarness.test as pthtest
import pyTestHarness.harness as pthharness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1():
  ranks = 1
  launch = [ makeLocalPathAbsolute('./ex') , makeLocalPathAbsolute('./ex') ]
  expected_file = 'ex.expected'

  def comparefuncSubTest(test):
    os.system('head -n 8 ex1-p1.output > cvg.txt')
    os.system('tail -n 3 ex1-p1.output >> cvg.txt')
    test.compareUnixDiff()


  # Create test object
  test = pthtest.Test('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefuncSubTest)
  test.appendKeywords('@')

  return(test)


def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  os.system('gcc -o ex ex.c')

  h = pthharness.Harness( [test1()] )
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
