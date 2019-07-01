#!/usr/bin/env python
import os
from sciath.test import Test
from sciath.harness import Harness

def run_petsc_ex2a():
  launch = '${PETSC_DIR}/src/ksp/ksp/examples/tutorials/ex2'
  ranks = 4
  expected_file = 'ex2.expected'

  def comparefunc(test):
    key = 'KSP Residual norm'
    test.compareFloatingPointAbsolute(key,1.0e-5)

  test = Test('ex2a',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  return(test)

def run_petsc_ex2b():
  launch = '${PETSC_DIR}/src/ksp/ksp/examples/tutorials/ex2 -ksp_monitor_short'
  ranks = 4
  expected_file = 'ex2.expected'

  def comparefunc(test):
    key = 'KSP Residual norm'
    test.compareFloatingPointAbsolute(key,1.0e-5)

  test = Test('ex2b',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  return(test)

def run_petsc_ex2c():
  launch = '${PETSC_DIR}/src/ksp/ksp/examples/tutorials/ex2 -ksp_type gcr -ksp_monitor_short'
  ranks = 4
  expected_file = 'ex2.expected'

  def comparefunc(test):
    key = 'KSP Residual norm'
    test.compareFloatingPointAbsolute(key,1.0e-5)

    key = 'Norm of error'
    test.compareLiteral(key)

  test = Test('ex2c',ranks,launch,expected_file)
  test.setVerifyMethod(comparefunc)
  return(test)

def run_petsc_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  # Build KSP example 2
  if not os.environ.get('PETSC_ARCH') or not os.environ.get('PETSC_DIR') :
    raise Exception('You must define PETSC_ARCH and PETSC_DIR to correspond to a working PETSc build')
  os.system('cd ' + os.environ['PETSC_DIR'] + '/src/ksp/ksp/examples/tutorials && make ex2 && cd -')

  registeredTests = [ run_petsc_ex2a() , run_petsc_ex2b() , run_petsc_ex2c() ]

  h = Harness(registeredTests)
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_petsc_tests()
