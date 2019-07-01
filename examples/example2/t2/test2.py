import os
import pyTestHarness.test as pthtest

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex2')
  expected_file = 'expectedoutput/ex2.expected'

  def comparefunc(test):
    key = 'Residuals'
    test.compareFloatingPointAbsolute(key,0.0001)

  # Create test object
  test = pthtest.Test('test2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  test.setComparisonFile('output/ex2-residual.log')

  return(test)
