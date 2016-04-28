
import pth_test as pth
import pth_batch as batch

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

def run_petsc_unittests_example3():
  
  registered_tests = [ run_petsc_ex2a() , run_petsc_ex2b() , run_petsc_ex2c() ]
  
  launcher = batch.zpthBatchQueuingSystem()
  launcher.executeTestSuite(registered_tests)
  launcher.verifyTestSuite(registered_tests)

if __name__ == "__main__":
  run_petsc_unittests_example3()