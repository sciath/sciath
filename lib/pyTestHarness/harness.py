
import os,sys
import argparse

import pyTestHarness.unittest as unittest
import pyTestHarness.launch as launch
from   pyTestHarness.colors import pthNamedColors as bcolors

def launcherExecuteAll(launcher,testList,description):
  
  print('' , flush=True)
  launcher.view()
  
  skipCounter = 0
  for t in testList:
    if launcher.mpiLaunch == 'none' and t.ranks != 1:
      if t.ignore == True:
        skipCounter = skipCounter + 1

  if skipCounter != 0:
    print('\n' + bcolors.WARNING + 'Warning: ' + str(skipCounter) + ' MPI parallel jobs are being skipped as a valid MPI launcher was not provided'+ bcolors.ENDC)
  
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
  nTests = len(testList)
  failCounter = 0
  execCounter = 0
  skipCounter = 0
  seqCounter = 0
  mpiCounter  = 0
  seqPassedCounter = 0
  mpiPassedCounter  = 0
  seqExecCounter = 0
  mpiExecCounter  = 0

  for test in testList:
    if test.ranks == 1:
      seqCounter = seqCounter + 1
    else:
      mpiCounter = mpiCounter + 1

    if test.ignore == False:
      execCounter = execCounter + 1

      if test.ranks == 1:
        seqExecCounter = seqExecCounter + 1
      else:
        mpiExecCounter = mpiExecCounter + 1

      if test.passed == False:
        failCounter = failCounter + 1
    else:
      skipCounter = skipCounter + 1

  for test in testList:
    if test.ignore == False:
      if test.ranks == 1 and test.passed == True:
        seqPassedCounter = seqPassedCounter + 1
      elif test.ranks >= 1 and test.passed == True:
        mpiPasedCounter = mpiPassedCounter + 1

  print('[--------- UnitTest status ----------------------]' , flush=True)
  for test in testList:
    test.report('summary')


  print('' , flush=True)
  print('[--------- UnitTest report ----------------------]' , flush=True)
  print('  ' + ("%.4d" % nTests) + ' ' + 'UnitTests registered')
  print('  ' + ("%.4d" % seqCounter) + ' Sequential UnitTests')
  print('  ' + ("%.4d" % mpiCounter) + ' MPI UnitTests')
  print('  ' + ("%.4d" % execCounter) + ' of ' +("%.4d" % nTests)+ ' UnitTests executed')

  print('')
  if execCounter == 0:
    print(bcolors.WARNING + ' [status] UNKNOWN: All tests were skipped' + bcolors.ENDC , flush=True)

  elif failCounter > 0:
    print(bcolors.FAIL + ' [status] FAIL: ' + str(failCounter) + ' of ' + str(execCounter) + bcolors.FAIL + ' tests executed FAILED' + bcolors.ENDC , flush=True)
    
    print(bcolors.FAIL +'          ' + ("%.4d" % (seqExecCounter-seqPassedCounter)) + ' of ' +("%.4d" % seqExecCounter)+ ' executed Sequential tests failed'+bcolors.ENDC)
    print(bcolors.FAIL +'          ' + ("%.4d" % (mpiExecCounter-mpiPassedCounter)) + ' of ' +("%.4d" % mpiExecCounter)+ ' executed MPI tests failed'+bcolors.ENDC)
  else:
    if skipCounter == 0:
      print(bcolors.OKGREEN + ' [status] SUCCESS: All registered tests passed' + bcolors.ENDC , flush=True)
    else:
      print(bcolors.WARNING + ' [status] SUCCESS (partial): All executed tests passed' + bcolors.ENDC , flush=True)

  if seqExecCounter + mpiExecCounter != nTests:
    print(bcolors.WARNING+'          Warning: Not all UnitTests were executed!'+ bcolors.ENDC)
  if seqExecCounter != seqCounter:
    print(bcolors.WARNING+'          Warning: '+("%.4d" % (seqCounter-seqExecCounter))+' sequential UnitTests were skipped'+ bcolors.ENDC)
  if mpiExecCounter != mpiCounter:
    print(bcolors.WARNING+'          Warning: '+("%.4d" % (mpiCounter-mpiExecCounter))+' MPI UnitTests were skipped!'+ bcolors.ENDC)

  if failCounter > 0:
    file = open('pthErrorReport.log','w')
    sys.stdout = file
    
    for test in testList:
      test.report('log')
    
    file.close()
    sys.stdout = sys.__stdout__

    print('xxx============================================================================xxx')
    print('     UnitTests failed - Full error report written to pthErrorReport.log')
    print('                      - Inspect the error log file and resolve failed tests')
    print('     vi pthErrorReport.log')
    print('xxx============================================================================xxx')



class pthHarness:
  def __init__(self,registeredTests):
    self.testsRegistered = 0
    self.testsExecuted = 0
    self.testsSkipped = 0
    self.testsPassed = 0
    self.testsFailed = 0

    self.testDescription = []
    self.registeredTests = registeredTests

    for t in self.registeredTests:
      if not isinstance(t,unittest.pthUnitTest):
        raise ValueError('[pth]: Registered tests must be of type UnitTest')
    self.testsRegistered = len(self.registeredTests)

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

    # Exclude parallel tests if mpiLauncher = 'none' and test uses more than 1 rank
    counter = 0
    skipCounter = 0
    for t in self.registeredTests:
      if self.launcher.mpiLaunch == 'none' and t.ranks != 1:
        self.registeredTests[counter].ignore = True
        self.testDescription[counter] = 'No MPI launcher was provided and test requested > 1 MPI rank'
        skipCounter = skipCounter + 1
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
          counter = counter + 1
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

    # Don't execute if we are verifying (only)
    if not self.args.verify:
      launcherExecuteAll(launcher,self.registeredTests,self.testDescription)
    

  def verify(self):
    launcher = self.launcher
    
    # Verify, unless we are running with a batch system and are not in verify(-only) mode
    if not launcher.use_batch or self.args.verify :
      launcherVerifyAll(self,self.registeredTests,self.testDescription)
      launcherReportAll(self,self.registeredTests)
