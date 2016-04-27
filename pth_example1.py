
import pth_test as pth

from pth_test import compareLiteral
from pth_test import compareFloatingPoint
from pth_test import compareInteger
from pth_test import parseFile
from pth_test import getKeyValues
from pth_test import getKeyValuesAsInt
from pth_test import getKeyValuesAsFloat
from pth_test import getKeyValuesNLinesInclusive
from pth_test import getKeyValuesNLinesExclusive

import pth_batch as batch

def test1_example():
  
  ranks = 1
  
  launch = './ex1 -options_file a'
  
  expected_file = 'ex1.expected'
  
  def comparefunc(unittest):
    expected,expected_flat = unittest.getExpected()
    output,output_flat = unittest.getOutput()
    
    key = '\$cputime'
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,0.01,values_e)
    unittest.updateStatus(status,err)
    
    key = '\$residuals'
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,0.000001,values_e)
    unittest.updateStatus(status,err)
    
    key = '\$kspits'
    values_e = getKeyValuesAsInt(expected_flat,key)
    values   = getKeyValuesAsInt(output_flat,key)
    status,err = compareFloatingPoint(values,0,values_e)
    unittest.updateStatus(status,err)
    
    key = '\$norm'
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,0.01,values_e)
    unittest.updateStatus(status,err)
    
    key = '\$rms'
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,0.01,values_e)
    unittest.updateStatus(status,err)
  
  # Create unit test object
  ex1 = pth.UnitTest('ex1',ranks,launch,expected_file)
  ex1.setVerifyMethod(comparefunc)
  ex1.appendKeywords('@')
  
  return(ex1)

# /Users/dmay/software/petsc-3.6.0/arch-darwin-c-debug/bin/mpiexec
def run_petsc_ex2a():

  launch = '${PETSC_DIR}/src/ksp/ksp/examples/tutorials/ex2'
  ranks = 4
  expected_file = 'ex2.expected'
  
  def comparefunc(unittest):
    key = 'KSP Residual norm'
    unittest.compareFloatingPoint(key,1.0e-5)

  test = pth.UnitTest('ex2a',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  return(test)

def run_petsc_ex2b():
  
  launch = '${PETSC_DIR}/src/ksp/ksp/examples/tutorials/ex2 -ksp_monitor_short'
  ranks = 4
  expected_file = 'ex2.expected'
  
  def comparefunc(unittest):
    key = 'KSP Residual norm'
    unittest.compareFloatingPoint(key,1.0e-5)
  
  test = pth.UnitTest('ex2b',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  return(test)

def run_petsc_ex2c():
  
  launch = '${PETSC_DIR}/src/ksp/ksp/examples/tutorials/ex2 -ksp_type gcr -ksp_monitor_short'
  ranks = 4
  expected_file = 'ex2.expected'
  
  def comparefunc(unittest):
    key = 'KSP Residual norm'
    unittest.compareFloatingPoint(key,1.0e-5)
  
    key = 'Norm of error'
    unittest.compareLiteral(key)
  
  test = pth.UnitTest('ex2c',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  return(test)

def run_my_tests():
  
  launcher = batch.zpthBatchQueuingSystem()
  launcher.configure()
  
  registered_tests = [test1_example(), test1_example(), test1_example(), test1_example()]
  
  for test in registered_tests:
    launcher.submitJob(test)

  for test in registered_tests:
    test.verifyOutput()
  
  print('-- Unit test report --')
  counter = 0
  for test in registered_tests:
    test.report('summary')
    if test.passed == False:
      counter = counter + 1
  print(str(counter) + ' / ' + str(len(registered_tests)) + ' failed')

  print('-- Unit test error messages --')
  for test in registered_tests:
    test.report('log')

def run_my_tests_petsc():
  
  launcher = batch.zpthBatchQueuingSystem()
  launcher.configure()
  
  registered_tests = [ run_petsc_ex2a() , run_petsc_ex2b() , run_petsc_ex2c() ]
  
  for test in registered_tests:
    launcher.submitJob(test)
  
  for test in registered_tests:
    test.verifyOutput()
  
  print('-- Unit test report summary --')
  counter = 0
  for test in registered_tests:
    test.report('summary')
    if test.passed == False:
      counter = counter + 1
  if counter > 0:
    print('  ' + str(counter) + ' / ' + str(len(registered_tests)) + ' tests failed')
  else:
    print('  All tests passed')

  print('-- Unit test error messages --')
  for test in registered_tests:
    test.report('log')

def run_my_tests_petsc_v2():
  
  registered_tests = [ run_petsc_ex2a() , run_petsc_ex2b() , run_petsc_ex2c() ]
  #registered_tests = [ run_petsc_ex2b() ]
  
  launcher = batch.zpthBatchQueuingSystem()
  launcher.executeTestSuite(registered_tests)
  launcher.verifyTestSuite(registered_tests)

if __name__ == "__main__":
  #test1()
  #test2()
  #test3()
  #test1_example()
  #run_my_tests()
  #run_my_tests_petsc()
  run_my_tests_petsc_v2()