import os
from sciath.test import Test

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test():
  ranks = 1
  launch = makeLocalPathAbsolute('ex1')
  expected_file = makeLocalPathAbsolute(os.path.join('..','expectedoutput','ex1.expected'))

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
  ex1 = Test('test1',ranks,launch,expected_file)
  ex1.setVerifyMethod(comparefunc)
  ex1.appendKeywords('@')

  return(ex1)
