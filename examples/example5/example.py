#!/usr/bin/env python
import os
from sciath.test import Test
from sciath.harness import Harness

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def test1():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex1')
  expected_file = 'ex1.expected'

  def comparefunc(test):
    key = '\$cputime'
    test.compareFloatingPointAbsolute(key,0.01)

    key = '\$residuals'
    test.compareFloatingPointAbsolute(key,0.000001)

    key = '\$kspits'
    test.compareInteger(key,0)

    key = '\$norm'
    test.compareFloatingPointAbsolute(key,0.01)

    key = '\$rms'
    test.compareFloatingPointAbsolute(key,0.01)

  # Create test object
  test = Test('ex1',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')

  return(test)

def test2():
  ranks = 1
  launch = makeLocalPathAbsolute('./ex2')
  expected_file = 'ex2.expected'

  def comparefunc(test):
    key = 'Residuals'
    test.compareFloatingPointAbsolute(key,0.0001)

  # Create test object
  test = Test('ex2',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  test.appendKeywords('@')
  test.setComparisonFile('ex2-residual.log')

  return(test)

def test3():
  ranks = 1
  launch = 'touch ex3.output'
  expected_file = 'ex3.expected'

  def comparefunc(test):
    key = 'kspit'
    test.compareInteger(key,0)

    key = 'res1'
    test.compareFloatingPointAbsolute(key,1.0e-4)

  # Create test object
  test = Test('ex3',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)

  return(test)

# Define test which doesn't use an expected file
from sciath.test import getKeyValuesAsInt

def test4():
  def comparefunc(test):
    output,output_flat = test.getOutput()

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
    test.updateStatus(status,kerr)

  test = Test('ex4',1,makeLocalPathAbsolute('./ex1'),None)
  test.setVerifyMethod(comparefunc)
  return(test)

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  registeredTests = [ test1() , test2(), test3(), test4() ]

  os.system('gcc -o ex1 ex1.c')
  os.system('gcc -o ex2 ex2.c')

  h = Harness(registeredTests)
  h.execute()
  h.verify() 

if __name__ == "__main__":
  run_tests()
