
import os
import argparse

import pyTestHarness.unittest as unittest
import pyTestHarness.launch as launch
from   pyTestHarness.colors import pthNamedColors as bcolors

def launcherExecuteAll(launcher,testList,description):
  
  print('' , flush=True)
  launcher.view()
  
  print('' , flush=True)
  counter = 0
  for test in testList:
    if test.ignore == False:
      print('[-- Executing test: ' + test.name + ' --]' , flush=True)
      launcher.submitJob(test)
    else:
      print('[-- Skipping test: ' + test.name + ' --] Reason: ' + description[counter] , flush=True)
    counter = counter + 1


def launcherVerifyAll(launcher,testList,description):
  
  print('' , flush=True)
  counter = 0
  for test in testList:
    if test.ignore == False:
      print('[-- Verifying test: ' + test.name + ' --]' , flush=True)
      test.verifyOutput()
    else:
      print('[-- Skipping test: ' + test.name + ' --] Reason: ' + description[counter] , flush=True)
    counter = counter + 1


def launcherReportAll(launcher,testList):

  print('' , flush=True)
  failCounter = 0
  execCounter = 0
  skipCounter = 0
  for test in testList:
    if test.ignore == False:
      execCounter = execCounter + 1
      if test.passed == False:
        failCounter = failCounter + 1
    else:
      skipCounter = skipCounter + 1
  if failCounter > 0:
    print('' , flush=True)
    print('[--------- Unit test error report ----------------------]' , flush=True)
    for test in testList:
      test.report('log')


  print('[--------- Unit test summary ----------------------]' , flush=True)
  for test in testList:
    test.report('summary')

  if execCounter == 0:
    print(bcolors.WARNING + '          *******************************' + bcolors.ENDC)
    print(bcolors.WARNING + ' [status] UNKNOWN: All tests were skipped' + bcolors.ENDC , flush=True)
    print(bcolors.WARNING + '          *******************************' + bcolors.ENDC)

  elif failCounter > 0:
    print(bcolors.FAIL + '          *************************************' + bcolors.ENDC)
    print(bcolors.FAIL + ' [status] FAIL: ' + str(failCounter) + ' of ' + str(execCounter) + bcolors.FAIL + ' tests executed FAILED' + bcolors.ENDC , flush=True)
    print(bcolors.FAIL + '          *************************************' + bcolors.ENDC)

  else:
    print(bcolors.OKGREEN + '          ***********************************' + bcolors.ENDC)
    print(bcolors.OKGREEN + ' [status] SUCCESS: All executed tests passed' + bcolors.ENDC , flush=True)
    print(bcolors.OKGREEN + '          ***********************************' + bcolors.ENDC)


class pthHarnesss:
  def __init__(self,registeredTests):
    self.registeredTests = registeredTests
    self.testDescription = []

    for t in self.registeredTests:
      if not isinstance(t,unittest.pthUnitTest):
        raise ValueError('[pth]: Registered tests must be of type UnitTest')


    self.launcher = launch.pthLaunch()

    parser = argparse.ArgumentParser(description='Python Test Harness.')
    parser.add_argument('-e', '--execute', help='Execute all tests', required=False, action='store_true')
    parser.add_argument('-v', '--verify', help='Perform test verification only (and not execution)', required=False, action='store_true')
    parser.add_argument('-c', '--configure', help='Configure queuing system information', required=False, action='store_true')
    parser.add_argument('-t', '--test', help='List of test names', required=False)
    parser.add_argument('-o', '--output_path', help='Directory to write stdout into', required=False)
    self.args = parser.parse_args()

    # Label tests as Registered or Excluded:Reason
    for i in range(0,len(self.registeredTests)):
      self.testDescription.append('Registered')

    # Exclude parallel tests if mpiLauncher = 'none' and test uses more than 4 ranks
    counter = 0
    for t in self.registeredTests:
      if self.launcher.mpiLaunch == 'none' and t.ranks != 1:
        self.registeredTests[counter].ignore = True
        self.testDescription[counter] = 'No MPI launcher was provided and test requested > 1 MPI rank'
      counter = counter + 1

    # Exclude tests based on command line option
    subList = []
    if self.args.test:
      tnames = self.args.test.split(',')
      for name in tnames:
        found = False
        for t in self.registeredTests:
          if name == t.name:
            subList.append(t)
            found = True
            break

        if found == False:
          raise RuntimeError('[pth] You requested to test a subset of registered tests, \n\t\t  but no registed test matched the name \"' + name + '\"' )

    if self.args.test:
      counter = 0
      for t in self.registeredTests:
        # skip tests already marked to be ignored (e.g. due to mpiLaunch = none and test.ranks != 1
        if t.ignore == True:
          continue
        
        if t not in subList:
          t.ignore = True
          self.testDescription[counter] = 'Excluded based on users command line arg -t'
        counter = counter + 1


  def execute(self):
    launcher = self.launcher
    # Set output path on all tests if different to the current working directory
    if self.args.output_path:
      for test in self.allTests:
        test.setOutputPath(self.args.output_path)

    # Don't execute if we are verifying a batch run
    if not launcher.use_batch and not self.args.verify:
      launcherExecuteAll(launcher,self.registeredTests,self.testDescription)
    

  def verify(self):
    launcher = self.launcher
    
    # Verify, unless we are running with a batch system and are not in verify(-only) mode
    if not launcher.use_batch or self.args.verify :
      launcherVerifyAll(self,self.registeredTests,self.testDescription)
      launcherReportAll(self,self.registeredTests)
