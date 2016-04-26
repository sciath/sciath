
import zpth2 as pth

from zpth2 import compareLiteral
from zpth2 import compareFloatingPoint
from zpth2 import compareInteger
from zpth2 import parseFile
from zpth2 import getKeyValues
from zpth2 import getKeyValuesAsInt
from zpth2 import getKeyValuesAsFloat
from zpth2 import getKeyValuesNLinesInclusive
from zpth2 import getKeyValuesNLinesExclusive

import zpth_conf as batch

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

def run_my_tests():
  
  launcher = batch.zpthBatchQueuingSystem()
  launcher.configure()
  
  registered_tests = [test1_example(), test1_example(), test1_example(), test1_example()]
  
  for test in registered_tests:
    launcher.submitJob(test)

  for test in registered_tests:
    test.verifyOutput()
  
  print('-- Unit test report --')
  for test in registered_tests:
    test.report('summary')
  
  print('-- Unit test error messages --')
  for test in registered_tests:
    test.report('log')


if __name__ == "__main__":
  #test1()
  #test2()
  #test3()
  #test1_example()
  run_my_tests()
