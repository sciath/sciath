from __future__ import print_function
import os
import sys
import argparse
import pyTestHarness.test as pthtest
import pyTestHarness.launcher as pthlauncher
from   pyTestHarness.colors import NamedColors as pthcolors

class Harness:
  def __init__(self,registeredTests):
    self.testsRegistered = 0
    self.testsExecuted = 0
    self.testsSkipped = 0
    self.testsPassed = 0
    self.testsFailed = 0
    self.verbosity_level = 1
    self.pthErrorReportFileName = 'pthErrorReport.log'

    self.testDescription = []
    self.registeredTests = registeredTests

    for t in self.registeredTests:
      if not isinstance(t,pthtest.Test):
        raise ValueError('[pth]: Registered tests must be of type test')
    self.testsRegistered = len(self.registeredTests)

    parser = argparse.ArgumentParser(description='Python Test Harness.')
    parser.add_argument('-e', '--execute', help='Execute all tests', required=False, action='store_true')
    parser.add_argument('-v', '--verify', help='Perform test verification only (and not execution)', required=False, action='store_true')
    parser.add_argument('-c', '--configure', help='Configure queuing system information', required=False, action='store_true')
    parser.add_argument('-t', '--test', help='List of test names', required=False)
    parser.add_argument('-o', '--output_path', help='Directory to write stdout into', required=False)
    parser.add_argument('-p', '--purge_output', help='Delete generated output', required=False, action='store_true')
    parser.add_argument('-f', '--error_on_test_failure', help='Return exit code of 1 if any test failed', required=False, action='store_true')
    parser.add_argument('-d', '--configure_default', help='Write default queuing system config file (no mpi, no queuing system)', required=False, action='store_true')
    parser.add_argument('-s', '--sandbox', help='Execute tests in separate directories. Will not work unless you supply absolute paths to executables.', required=False, action='store_true')
    parser.add_argument('-l', '--list', help='List all registered tests and exit', required=False, action='store_true')
    self.args, self.unknown = parser.parse_known_args()

    # If "list" option supplied, simply print out all the tests' names and exit
    if self.args.list :
      for test in registeredTests :
        print(test.name)
      sys.exit(0)

    # If --configure_default is specified, write the default file and exit
    if self.args.configure_default:
      pthlauncher.Launcher.writeDefaultDefinition()
      sys.exit(0)

    # Create the launcher
    self.launcher = pthlauncher.Launcher()

    # If --configure is specified, (re)generate the configuration file and exit
    if self.args.configure:
      self.launcher.configure()
      sys.exit(0)

    # Instruct tests to use sandboxes if requested
    if self.args.sandbox :
      for test in registeredTests :
        test.use_sandbox = True

    # Set output path on all tests if --output_path option was included
    if self.args.output_path:
      for test in self.registeredTests:
        test.setOutputPath(self.args.output_path)

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
          errstr= '[pth] You requested to test a subset of registered tests, \n\t\t  but no registered test matched the name \"' + name + '\"'
          raise RuntimeError(errstr)

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

    # Clean all output unless we are verifying (only)
    if not self.args.verify :
      self.clean()

    # If -p was supplied, stop after cleaning
    if self.args.verify and self.args.purge_output :
      raise RuntimeError('-p (--purge_output) and -v (--verify) are not supported together')
    if self.args.purge_output :
      exit(0);

  def setVerbosityLevel(self,value):
    self.verbosity_level = value
    self.launcher.setVerbosityLevel(self.verbosity_level)

  def execute(self):
    '''Execute tests unless verifying (only) or purging output (only)'''
    if not self.args.verify and not self.args.purge_output:
      print('')
      print(pthcolors.HEADER + '[ *** Executing Tests *** ]' + pthcolors.ENDC)
      launcher = self.launcher
      testList = self.registeredTests
      description = self.testDescription
      if launcher.verbosity_level > 0:
        launcher.view()

      skipCounter = 0
      for t in testList:
        if launcher.mpiLaunch == 'none' and t.ranks != 1:
          if t.ignore == True:
            skipCounter = skipCounter + 1

      if skipCounter != 0:
        print('\n' + pthcolors.WARNING + 'Warning: ' + str(skipCounter) + ' MPI parallel jobs are being skipped as a valid MPI launcher was not provided'+ pthcolors.ENDC)

      counter = 0
      for test in testList:
        if test.ignore == False:
          print('[-- Executing test: ' + test.name + ' --]')
          launcher.submitJob(test)
        else:
          print('[-- Skipping test: ' + test.name + ' --] Reason: ' + description[counter])
        counter = counter + 1

  def verify(self):
    '''Verify, unless we are running with a batch system and are not in verify(-only) mode'''
    if not self.launcher.useBatch or self.args.verify :
      print('')
      print(pthcolors.HEADER + '[ *** Verifying Test Output *** ]' + pthcolors.ENDC)
      tests_not_skipped = 0
      for test in self.registeredTests:
        print('[-- Verifying test: ' + test.name + ' --]')
        if test.ignore :
          print('[Skipping verification for test \"' + test.name + '\"]')
        elif self.launcher.mpiLaunch == 'none' and test.ranks != 1:
          print('[Skipping verification for test \"' + test.name + '\" as test uses > 1 MPI ranks and no MPI launcher was provided]')
        else:
          tests_not_skipped = tests_not_skipped + 1
          test.verifyOutput()

      print('')
      counter = 0
      for test in self.registeredTests:
        if not test.ignore and not test.passed :
          counter = counter + 1
      if counter > 0:
        print('')
        print('[--------- Test Error Report ----------------------]')
        for test in self.registeredTests:
          test.report('log')

      errfile = self.reportAll()
      if errfile and self.args.error_on_test_failure:
        print('\n')
        print('Contents of "' + errfile +'"')
        os.system('cat ' + errfile)
        sys.exit(1)

  def clean(self):
    print('')
    print(pthcolors.HEADER + '[ *** Deleting Existing Test Output *** ]' + pthcolors.ENDC)
    if os.path.isfile(self.pthErrorReportFileName) :
      os.remove(self.pthErrorReportFileName)
    for test in self.registeredTests:
      if test.ignore:
        print('[ -- Skipping test:',test.name,'--]')
      else:
        self.launcher.clean(test)

  def reportAll(self):
    launcher = self.launcher
    testList = self.registeredTests
    print('')
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
          mpiPassedCounter = mpiPassedCounter + 1

    print('[--------- test status ----------------------]')
    for test in testList:
      test.report('summary')

    print('')
    print('[--------- test report ----------------------]')
    print('  ' + ("%.4d" % nTests) + ' ' + 'tests registered')
    print('  ' + ("%.4d" % seqCounter) + ' Sequential tests')
    print('  ' + ("%.4d" % mpiCounter) + ' MPI tests')
    print('  ' + ("%.4d" % execCounter) + ' of ' +("%.4d" % nTests)+ ' tests executed')

    print('')
    if execCounter == 0:
      print(pthcolors.WARNING + ' [status] UNKNOWN: All tests were skipped' + pthcolors.ENDC)

    elif failCounter > 0:
      print(pthcolors.FAIL + ' [status] FAIL: ' + str(failCounter) + ' of ' + str(execCounter) + pthcolors.FAIL + ' tests executed FAILED' + pthcolors.ENDC)

      print(pthcolors.FAIL +'          ' + ("%.4d" % (seqExecCounter-seqPassedCounter)) + ' of ' +("%.4d" % seqExecCounter)+ ' executed Sequential tests failed'+pthcolors.ENDC)
      print(pthcolors.FAIL +'          ' + ("%.4d" % (mpiExecCounter-mpiPassedCounter)) + ' of ' +("%.4d" % mpiExecCounter)+ ' executed MPI tests failed'+pthcolors.ENDC)
    else:
      if skipCounter == 0:
        print(pthcolors.OKGREEN + ' [status] SUCCESS: All registered tests passed' + pthcolors.ENDC)
      else:
        print(pthcolors.WARNING + ' [status] SUCCESS (partial): All executed tests passed' + pthcolors.ENDC)

    if seqExecCounter + mpiExecCounter != nTests:
      print(pthcolors.WARNING+'          Warning: Not all tests were executed!'+ pthcolors.ENDC)
    if seqExecCounter != seqCounter:
      print(pthcolors.WARNING+'          Warning: '+("%.4d" % (seqCounter-seqExecCounter))+' sequential tests were skipped'+ pthcolors.ENDC)
    if mpiExecCounter != mpiCounter:
      print(pthcolors.WARNING+'          Warning: '+("%.4d" % (mpiCounter-mpiExecCounter))+' MPI tests were skipped!'+ pthcolors.ENDC)

    errfile = []
    if failCounter > 0:
      file = open(self.pthErrorReportFileName,'w')
      sys.stdout = file

      for test in testList:
        test.report('log')

      file.close()
      sys.stdout = sys.__stdout__

      print('xxx============================================================================xxx')
      print('     tests failed - Full error report written to ' + self.pthErrorReportFileName)
      print('                      - Inspect the error log file and resolve failed tests')
      pthErrorReportFileLocation = os.path.realpath(self.pthErrorReportFileName)
      print('     cat ' + pthErrorReportFileLocation)
      print('xxx============================================================================xxx')
      errfile = pthErrorReportFileLocation
    return(errfile)

# Deprecated alias for backwards compatibility
pthHarness = Harness
