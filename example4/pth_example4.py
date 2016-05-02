
import os
import pyTestHarness.unittest as pth
import pyTestHarness.launch as launch

def test1():
  
  ranks = 1
  launch = './ex'
  expected_file = 'ex.expected'
  
  def comparefunc(unittest):
    
    key = 'kspits'
    unittest.compareInteger(key,0)

    key = 'norm'
    unittest.compareFloatingPoint(key,1e-4)
  
  # Create unit test object
  test = pth.pthUnitTest('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  
  return(test)

def test2():
  
  ranks = 1
  launch = './ex'
  expected_file = 'ex.expected2'
  
  def comparefunc(unittest):
    
    key = 'kspits'
    unittest.compareInteger(key,0)

    key = 'norm'
    unittest.compareFloatingPoint(key,1e-4)
  
  # Create unit test object
  test = pth.pthUnitTest('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  
  return(test)

def test3():
  
  ranks = 1
  launch = './ex'
  expected_file = 'ex.expected3'
  
  def comparefunc(unittest):
    
    key = 'kspits'
    unittest.compareInteger(key,0)
  
    key = 'norm'
    unittest.compareFloatingPoint(key,1e-4)
  
  # Create unit test object
  test = pth.pthUnitTest('ex3',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  
  return(test)
def run_unittests():
  os.environ['PYTHONUNBUFFERED'] = str('1')
  
  registered_tests = [ test1(), test2(), test3() ]

  os.system('gcc -o ex ex.c')

  launcher = launch.pthLaunch()
  launcher.executeTestSuite(registered_tests)
  launcher.verifyTestSuite(registered_tests)

if __name__ == "__main__":
  run_unittests()
