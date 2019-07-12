from __future__ import print_function
import os
import sys
import argparse
import sciath.test as sciathtest
import sciath.launcher as sciathlauncher
from   sciath import sciath_colors

class Harness:
  def __init__(self,registeredTests,subsetTestName=None):
    self.testsRegistered = 0
    self.testsExecuted = 0
    self.testsSkipped = 0
    self.testsPassed = 0
    self.testsFailed = 0
    self.verbosity_level = 1
    self.errorReportFileName = 'errorReport.log'

    self.testDescription = [] # Note: not currently output, but could be used for future logging
    self.registeredTests = registeredTests

    # Check that tests are the correct type, with unique names
    testNames = []
    for t in self.registeredTests:
      testNames.append(t.name)
      if not isinstance(t,sciathtest.Test):
        raise ValueError('[SciATH]: Registered tests must be of type pyTestHarness.test.Test')
    self.testsRegistered = len(self.registeredTests)
    if len(testNames) != len(set(testNames)) :
      raise Exception('[SciATH] Registered tests must have unique names')

    parser = argparse.ArgumentParser(description='Python Test Harness.')
    parser.add_argument('-v', '--verify', help='Perform test verification only (and not execution)', required=False, action='store_true')
    parser.add_argument('-c', '--configure', help='Configure queuing system information', required=False, action='store_true')
    parser.add_argument('-t', '--test', help='List of test names', required=False)
    parser.add_argument('-o', '--output_path', help='Directory to write stdout into', required=False)
    parser.add_argument('-p', '--purge_output', help='Delete generated output', required=False, action='store_true')
    parser.add_argument('-f', '--error_on_test_failure', help='Return exit code of 1 if any test failed', required=False, action='store_true')
    parser.add_argument('-d', '--configure_default', help='Write default queuing system config file (no mpi, no queuing system)', required=False, action='store_true')
    parser.add_argument('-s', '--sandbox', help='Execute tests in separate directories. Will not work unless you supply absolute paths to executables.', required=False, action='store_true')
    parser.add_argument('-l', '--list', help='List all registered tests and exit', required=False, action='store_true')
    parser.add_argument('-w','--with_conf_file',help='Use provided configuration file instead of the default',required=False)
    parser.add_argument('--no-colors',help='Deactivate colored output',required=False,action='store_true')
    self.args, self.unknown = parser.parse_known_args()

    # Deactivate colored output if requested
    if self.args.no_colors :
        sciath_colors.set_colors(use_bash = False)

    if subsetTestName is None:
      self.subsetTestName = []
      self.execSubset = False
    else:
      self.subsetTestName = subsetTestName
      self.execSubset = True


    # If "list" option supplied, simply print out all the tests' names and exit
    if self.args.list :
      for test in registeredTests :
        print(test.name)
      sys.exit(0)

    # If --configure_default is specified, write the default file and exit
    if self.args.configure_default:
      sciathlauncher.Launcher.writeDefaultDefinition(self.args.with_conf_file)
      sys.exit(0)

    # Create the launcher
    self.launcher = sciathlauncher.Launcher(self.args.with_conf_file)

    # If --configure is specified, (re)generate the configuration file and exit
    if self.args.configure:
      self.launcher.configure()
      sys.exit(0)

    # Instruct all tests to use sandboxes if requested
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

    for name in self.subsetTestName:
      found = False
      for t in self.registeredTests:
        if name == t.name:
          subList.append(t)
          found = True
          break
      if found == False:
        errstr= '[SciATH] You requested to test a subset of registered tests, \n\t\t  but no registered test matched the name \"' + name + '\"'
        raise RuntimeError(errstr)

    if self.args.test:
      self.execSubset = True
      tnames = self.args.test.split(',')
      for name in tnames:
        found = False
        for t in self.registeredTests:
          if name == t.name:
            subList.append(t)
            found = True
            break

        if found == False:
          errstr= '[SciATH] You requested to test a subset of registered tests, \n\t\t  but no registered test matched the name \"' + name + '\"'
          raise RuntimeError(errstr)

    if self.execSubset:
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
      print(sciath_colors.HEADER + '[ *** Executing Tests *** ]' + sciath_colors.ENDC)
      launcher = self.launcher
      testList = self.registeredTests
      if launcher.verbosity_level > 0:
        launcher.view()

      skipCounter = 0
      for t in testList:
        if launcher.mpiLaunch == 'none' and t.ranks != 1:
          if t.ignore == True:
            skipCounter = skipCounter + 1

      if skipCounter != 0:
        print('\n' + sciath_colors.WARNING + 'Warning: ' + str(skipCounter) + ' MPI parallel jobs are being skipped as a valid MPI launcher was not provided'+ sciath_colors.ENDC)

      counter = 0
      skipCounter = 0
      for test in testList:
        if test.ignore == False:
          launcher.submitJob(test)
        else:
          skipCounter = skipCounter + 1
        counter = counter + 1
      if (skipCounter > 0) :
        print(sciath_colors.WARNING+'[SciATH] Skipped executing '+str(skipCounter)+' tests'+sciath_colors.ENDC)

  def verify(self):
    '''Verify, unless we are running with a batch system and are not in verify(-only) mode'''
    if not self.launcher.useBatch or self.args.verify :
      print('')
      print(sciath_colors.HEADER + '[ *** Verifying Test Output *** ]' + sciath_colors.ENDC)
      skipCounter = 0
      for test in self.registeredTests:
        if test.ignore  or (self.launcher.mpiLaunch == 'none' and test.ranks != 1) :
          skipCounter = skipCounter + 1
        else:
          print('[-- Verifying test: ' + test.name + ' --]')
          test.verifyOutput()
      if skipCounter > 0 :
        print(sciath_colors.WARNING+'[SciATH] Skipped verification for '+str(skipCounter)+' skipped tests'+sciath_colors.ENDC)

      print('')
      counter = 0
      for test in self.registeredTests:
        if not test.ignore and not test.passed :
          counter = counter + 1
      if counter > 0:
        print('')
        print(sciath_colors.SUBHEADER+'[--------- Test Error Report ----------------------]'+sciath_colors.ENDC)
        for test in self.registeredTests:
          test.report('log_short')

      errfile = self.reportAll()
      if errfile and self.args.error_on_test_failure:
        print('\n')
        print('Contents of "' + errfile +'"')
        os.system('cat ' + errfile)
        sys.exit(1)

  def clean(self):
    print('')
    print(sciath_colors.HEADER+'[ *** Deleting Existing Test Output *** ]'+sciath_colors.ENDC)
    if os.path.isfile(self.errorReportFileName) :
      os.remove(self.errorReportFileName)
    skipCounter = 0
    for test in self.registeredTests:
      if test.ignore:
        skipCounter = skipCounter + 1
      else:
        self.launcher.clean(test)
    if skipCounter > 0 :
      print(sciath_colors.WARNING+'[SciATH] Skipped removing output for '+str(skipCounter)+' skipped tests'+sciath_colors.ENDC)

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

    print(sciath_colors.SUBHEADER+'[--------- test status ----------------------]'+sciath_colors.ENDC)
    for test in testList:
      test.report('summary')

    print('')
    print(sciath_colors.SUBHEADER+'[--------- test report ----------------------]'+sciath_colors.ENDC)
    print('  ' + ("%.4d" % nTests) + ' ' + 'tests registered')
    print('  ' + ("%.4d" % seqCounter) + ' Sequential tests')
    print('  ' + ("%.4d" % mpiCounter) + ' MPI tests')
    print('  ' + ("%.4d" % execCounter) + ' of ' +("%.4d" % nTests)+ ' tests executed')

    print('')
    if execCounter == 0:
      print(sciath_colors.WARNING + ' [status] UNKNOWN: All tests were skipped' + sciath_colors.ENDC)

    elif failCounter > 0:
      print(sciath_colors.FAIL + ' [status] FAIL: ' + str(failCounter) + ' of ' + str(execCounter) + sciath_colors.FAIL + ' tests executed FAILED' + sciath_colors.ENDC)

      print(sciath_colors.FAIL +'          ' + ("%.4d" % (seqExecCounter-seqPassedCounter)) + ' of ' +("%.4d" % seqExecCounter)+ ' executed Sequential tests failed'+sciath_colors.ENDC)
      print(sciath_colors.FAIL +'          ' + ("%.4d" % (mpiExecCounter-mpiPassedCounter)) + ' of ' +("%.4d" % mpiExecCounter)+ ' executed MPI tests failed'+sciath_colors.ENDC)
    else:
      if skipCounter == 0:
        print(sciath_colors.OKGREEN + ' [status] SUCCESS: All registered tests passed' + sciath_colors.ENDC)
      else:
        print(sciath_colors.WARNING + ' [status] SUCCESS (partial): All executed tests passed' + sciath_colors.ENDC)

    if seqExecCounter + mpiExecCounter != nTests:
      print(sciath_colors.WARNING+'          Warning: Not all tests were executed!'+ sciath_colors.ENDC)
    if seqExecCounter != seqCounter:
      print(sciath_colors.WARNING+'          Warning: '+("%.4d" % (seqCounter-seqExecCounter))+' sequential tests were skipped'+ sciath_colors.ENDC)
    if mpiExecCounter != mpiCounter:
      print(sciath_colors.WARNING+'          Warning: '+("%.4d" % (mpiCounter-mpiExecCounter))+' MPI tests were skipped!'+ sciath_colors.ENDC)

    errfile = []
    if failCounter > 0:
      file = open(self.errorReportFileName,'w')
      sys.stdout = file

      for test in testList:
        test.report('log')

      file.close()
      sys.stdout = sys.__stdout__

      print('xxx============================================================================xxx')
      print('     tests failed - Full error report written to ' + self.errorReportFileName)
      print('                  - Please inspect the error log file and resolve failed tests')
      errorReportFileLocation = os.path.realpath(self.errorReportFileName)
      print('     cat ' + errorReportFileLocation)
      print('xxx============================================================================xxx')
      errfile = errorReportFileLocation
    return(errfile)
