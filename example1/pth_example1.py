
import os
import pth_test as pth
import pth_batch as batch

def test1():
  
  ranks = 1
  
  launch = './ex1'
  
  expected_file = 'ex1.expected'
  
  def comparefunc(unittest):
    
    key = '\$cputime'
    unittest.compareFloatingPoint(key,0.01)
    
    key = '\$residuals'
    unittest.compareFloatingPoint(key,0.000001)
    
    key = '\$kspits'
    unittest.compareInteger(key,0)

    key = '\$norm'
    unittest.compareFloatingPoint(key,0.01)
    
    key = '\$rms'
    unittest.compareFloatingPoint(key,0.01)
  
  # Create unit test object
  ex1 = pth.UnitTest('ex1',ranks,launch,expected_file)
  ex1.setVerifyMethod(comparefunc)
  ex1.appendKeywords('@')
  
  return(ex1)

def test2():
  
  ranks = 1
  launch = './ex2'
  expected_file = 'ex2.expected'
  
  def comparefunc(unittest):
    key = 'Residuals'
    unittest.compareFloatingPoint(key,0.0001)
  
  # Create unit test object
  test = pth.UnitTest('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  test.setComparisonFile('ex2-residual.log')

  return(test)

def run_unittests_example1():
  
  registered_tests = [ test1() , test2() ]

  os.system('gcc -o ex1 ex1.c')
  os.system('gcc -o ex2 ex2.c')

  launcher = batch.zpthBatchQueuingSystem()
  launcher.executeTestSuite(registered_tests)
  launcher.verifyTestSuite(registered_tests)

if __name__ == "__main__":
  run_unittests_example1()
