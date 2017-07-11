#!/usr/bin/env python
import os
import pyTestHarness.harness as harness
import pyTestHarness.unittest as putest

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex1')
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
  test = putest.pthUnitTest('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def test2():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex2')
  expected_file = 'ex2.expected'

  def comparefunc(unittest):
    key = 'Residuals'
    unittest.compareFloatingPoint(key,0.0001)

  # Create unit test object
  test = putest.pthUnitTest('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  test.setComparisonFile('ex2-residual.log')

  return(test)

def test3():
  ranks = 1
  launch = 'touch ex3.output'
  expected_file = 'ex3.expected'

  def comparefunc(unittest):
    key = 'kspit'
    unittest.compareInteger(key,0)

    key = 'res1'
    unittest.compareFloatingPoint(key,1.0e-4)

  # Create unit test object
  test = putest.pthUnitTest('ex3',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)

  return(test)

# Define test which doesn't use an expected file
from pyTestHarness.unittest import getKeyValuesAsInt

def test4():
  def comparefunc(unittest):
    output,output_flat = unittest.getOutput()

    key = '\$kspits'
    value = getKeyValuesAsInt(output_flat,key)
    print(value)
    if value:
      if value[0] != 43:
        status = False
        kerr = 'Key = \"' + key + '\" --> ' + 'Expected the value 43, found ' + str(value[0])
      else:
        status == True
        kerr = ''
    else:
      status = False
      kerr = 'Key = \"' + key + '\" --> was not found in output file'
    unittest.updateStatus(status,kerr)

  test = putest.pthUnitTest('ex4',1,makeLocalPathAbsolute('./ex1'),None)
  test.setVerifyMethod(comparefunc)
  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  registeredTests = [ test1() , test2(), test3(), test4() ]

  os.system('gcc -o ex1 ex1.c')
  os.system('gcc -o ex2 ex2.c')

  h = harness.pthHarness(registeredTests)
  h.execute()
  h.verify() 

if __name__ == "__main__":
  run_tests()
