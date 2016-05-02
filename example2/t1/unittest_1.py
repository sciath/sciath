
import os
import pyTestHarness.unittest as pth

def test():
  
  ranks = 1
  launch = './t1/ex1' # This must be a relative path with respect to pth_example2.py
  expected_file = 'expectedoutput/ex1.expected'
  
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
  ex1 = pth.pthUnitTest('unit1',ranks,launch,expected_file)
  ex1.setVerifyMethod(comparefunc)
  ex1.appendKeywords('@')
  
  return(ex1)
