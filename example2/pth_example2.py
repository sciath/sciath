#!/usr/bin/env python
import os,sys
import argparse

import pyTestHarness.unittest as pth
import pyTestHarness.harness as harness

# Import separate tests
sys.path.append(os.path.join(os.environ['PWD'], 't1'))
sys.path.append(os.path.join(os.environ['PWD'], 't2'))
import unittest_1 as ut1
import unittest_2 as ut2


def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

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

  h = harness.pthHarness(registeredTests)
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
