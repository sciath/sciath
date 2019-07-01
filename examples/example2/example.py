#!/usr/bin/env python
import os
import sys
import argparse
from sciath.test import Test
from sciath.harness import Harness

# Import separate tests
sys.path.append(os.path.join(os.environ['PWD'], 't1'))
sys.path.append(os.path.join(os.environ['PWD'], 't2'))
import test1 as t1
import test2 as t2

def makeLocalPathAbsolute(localRelPath) :
  thisDir = os.path.split(os.path.abspath(__file__))[0]
  return(os.path.join(thisDir,localRelPath))

def run_tests():
  os.environ['PYTHONUNBUFFERED'] = str('1')

  if os.path.isdir('output') == False:
    os.mkdir('output')

  # Register tests
  registeredTests = [ t1.test() , t2.test() ]

  # Force output to be written somewhere else, can be invoked using -o <path>
  for test in registeredTests:
    test.setOutputPath(makeLocalPathAbsolute('output'))

  # Build tests <should be done by make>
  os.system('gcc -o t1/ex1 t1/ex1.c')
  os.system('gcc -o t2/ex2 t2/ex2.c')

  h = Harness(registeredTests)
  h.execute()
  h.verify()

if __name__ == "__main__":
  run_tests()
