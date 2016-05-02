
import os
import pth_unittest as pth

def test():
  
  ranks = 1
  launch = './t2/ex2' # This must be a relative path with respect to pth_example2.py
  expected_file = 'expectedoutput/ex2.expected'
  
  def comparefunc(unittest):
    key = 'Residuals'
    unittest.compareFloatingPoint(key,0.0001)
  
  # Create unit test object
  test = pth.UnitTest('unit2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  test.setComparisonFile('output/ex2-residual.log')

  return(test)
