#!/usr/bin/env python
import os,sys
import argparse
import pth_test as pth
import pth_batch as batch


sys.path.append(os.path.join(os.environ['PWD'], 't1'))
sys.path.append(os.path.join(os.environ['PWD'], 't2'))
import unittest_1 as ut1
import unittest_2 as ut2



def run_unittests_example1():
  
  if os.path.isdir('output') == False:
    os.mkdir('output')

  # Register tests
  registeredTests = [ ut1.test() , ut2.test() ]

  # Force output to written somewhere else, can be invoked using -o <path>
  for test in registeredTests:
    test.setOutputPath('output')

  # Build tests <should be done by make>
  os.system('gcc -o t1/ex1 t1/ex1.c')
  os.system('gcc -o t2/ex2 t2/ex2.c')

  launcher = batch.zpthBatchQueuingSystem()

  # Filter tests <could be promoted into batch execute()/verify() methods
  args = launcher.args
  subset = []
  if args.test:
    print(registeredTests)
    tnames = args.test.split(',')
    for name in tnames:
      for t in registeredTests:
        if name == t.name:
          subset.append(t)
    if subset == []:
      raise RuntimeError('You requested to tests a subset of registered tests, \n',
                         'but no registed test matched the name list provided')
    else:
      print(subset)
  else:
    subset = registeredTests

  launcher.executeTestSuite(subset)
  launcher.verifyTestSuite(subset)

if __name__ == "__main__":
  run_unittests_example1()
