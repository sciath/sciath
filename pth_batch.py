
import os
import argparse
import pth_test as pth


def generateLaunch_PBS(accountname,queuename,testname,mpiLaunch,executable,ranks,ranks_per_node,walltime,outfile):
  if not ranks:
    print("<generateLaunch_PBS>: Requires the number of MPI-ranks be specified" , flush=True)
  if not walltime:
    print("<generateLaunch_PBS>: Requires the walltime be specified" , flush=True)
  
  filename = testname + '-zpth.pbs'
  file = open(filename,"w")
  file.write("#!/bin/bash\n")
  
  file.write("# ZPTH: auto-generated pbs file\n")

  if accountname:
    file.write("#PBS -A " + accountname + "\n") # account to charge
  file.write("#PBS -N \"" + testname + "\"" + "\n") # jobname
  file.write("#PBS -o " + testname + ".stdout" + "\n")
  file.write("#PBS -e " + testname + ".stderr" + "\n")
  
  if queuename:
    file.write("#PBS -q " + queuename + "\n")
  
  file.write("#PBS -l mppwidth=1024,walltime=" + str(walltime) + "\n")
  
  file.write(mpiLaunch + " " + executable + " > " + outfile + "\n\n") # launch command
  file.close()
  return(filename)

def generateLaunch_SLURM(accountname,queuename,testname,mpiLaunch,executable,ranks,ranks_per_node,walltime,outfile):
  if not ranks:
    print("<generateLaunch_SLURM>: Requires the number of MPI-ranks be specified" , flush=True)
  if not walltime:
    print("<generateLaunch_SLURM>: Requires the walltime be specified" , flush=True)
  
  filename = testname + '-zpth.slurm'
  file = open(filename,"w")
  file.write("#!/bin/bash -l\n")
  
  file.write("# ZPTH: auto-generated slurm file\n")
  if accountname:
    file.write("#SBATCH --account=" + accountname + "\n") # account to charge
  file.write("#SBATCH --job-name=\"" + testname + "\"" + "\n") # jobname
  
  file.write("#SBATCH --output=" + testname + ".stdout" + "\n") # jobname.stdout
  file.write("#SBATCH --error=" + testname + ".stderr" + "\n") # jobname.stderr
  
  if queuename:
    file.write("#SBATCH --partition=" + queuename + "\n")
  
  file.write("#SBATCH --ntasks=" + str(ranks) + "\n")
  if ranks_per_node:
    file.write("#SBATCH --ntasks-per-node=" + str(ranks_per_node) + "\n")
  
  file.write("#SBATCH --time=" + walltime + "\n")
  
  file.write(mpiLaunch + " " + executable + " > " + outfile + "\n\n") # launch command
  file.close()
  return(filename)

def generateLaunch_LSF(accountname,queuename,testname,executable,ranks,rusage,walltime):
  if not ranks:
    print("<generateLaunch_LSF>: Requires the number of MPI-ranks be specified" , flush=True)
  if not walltime:
    print("<generateLaunch_LSF>: Requires the walltime be specified" , flush=True)
  
  print("#!/bin/sh")
  
  print("# ZPTH: auto-generated lsf file")

  print("#BSUB -J " + testname ) # jobname
  
  print("#BSUB -o " + testname + ".stdout") # jobname.stdout
  print("#BSUB -e " + testname + ".stderr") # jobname.stderr
  
  if queuename:
    print("#BSUB -q " + queuename)
  
  print("#BSUB -n " + str(ranks))
  
  if rusage:
    print("#BSUB -R \'" + rusage + "\'")
  
  print("#BSUB -W " + walltime)
  
  print("aprun -n " + executable) # launch command


def generateLaunch_LoadLevelerBG(accountname,queuename,testname,executable,total_ranks,machine_ranks_per_node,walltime):
  if not total_ranks:
    print("<generateLaunch_LoadLeveler>: Requires the number of MPI-ranks be specified" , flush=True)
  if not walltime:
    print("<generateLaunch_LoadLeveler>: Requires the walltime be specified" , flush=True)
  
  print("#!/bin/sh")
  print("# ZPTH: auto-generated llq file")
  print("# @ job_name = " + testname)
  print("# @ job_type = bluegene")
  print("# @ error = $(job_name)_$(jobid).stderr")
  print("# @ output = $(job_name)_$(jobid).stdout")
  print("# @ environment = COPY_ALL;")
  print("# @ wall_clock_limit = " + str(walltime))
  print("# @ notification = never")
  print("# @ class = " + queuename)
  
  bgsize = math.ceil(total_ranks/machine_ranks_per_node)
  print("# @ bg_size = " + str(bgsize))
  print("# @ bg_connection = TORUS")
  print("# @ queue")
  
  print("runjob -n " + executable) # launch command


def performTestSuite_local(self,registered_tests):
  launcher = self
  
  print('' , flush=True)
  self.view()

  for test in registered_tests:
    print('-- Executing test: ' + test.name + ' --' , flush=True)
    launcher.submitJob(test)
    test.verifyOutput()
  
  print('-- Unit test report summary --' , flush=True)
  counter = 0
  for test in registered_tests:
    test.report('summary')
    if test.passed == False:
      counter = counter + 1
  if counter > 0:
    print('  ' + str(counter) + ' / ' + str(len(registered_tests)) + ' tests failed' , flush=True)
  else:
    print('----------------------' , flush=True)
    print('  All tests passed' , flush=True)
  
  if counter > 0:
    print('-- Unit test error report --' , flush=True)
    for test in registered_tests:
      test.report('log')


def performTestSuite_execute(self,registered_tests):
  launcher = self

  print('' , flush=True)
  self.view()

  print('' , flush=True)
  for test in registered_tests:
    print('[-- Executing test: ' + test.name + ' --]' , flush=True)
    launcher.submitJob(test)


def performTestSuite_verify(self,registered_tests):
  launcher = self
  
  print('' , flush=True)
  for test in registered_tests:
    print('[-- Verifying test: ' + test.name + ' --]' , flush=True)
    if self.mpiLaunch == 'none' and test.ranks != 1:
      print('[Skipping verification for test \"' + test.name + '\" as test uses > 1 MPI ranks and no MPI launcher was provided]')
    else:
      test.verifyOutput()
  
  print('' , flush=True)
  print('[--------- Unit test summary ----------------------]' , flush=True)
  counter = 0
  for test in registered_tests:
    if self.mpiLaunch == 'none' and test.ranks != 1:
      print('  ['+test.name+']  skipped as ranks > 1 and no MPI launcher provided')
    else:
      test.report('summary')
    if test.passed == False:
      counter = counter + 1
  if counter > 0:
    print('\n  [status] ' + str(counter) + ' of ' + str(len(registered_tests)) + ' tests FAILED' , flush=True)
  else:
    print('\n  [status] All tests passed' , flush=True)
  
  if counter > 0:
    print('' , flush=True)
    print('[--------- Unit test error report ----------------------]' , flush=True)
    for test in registered_tests:
      test.report('log')


class zpthBatchQueuingSystem:

  def __init__(self):
    self.accountName = []
    self.queueName = []
    self.mpiLaunch = []
    self.queuingSystemType = []
    self.jobSubmissionCommand = []
    self.use_batch = False
    
    parser = argparse.ArgumentParser(description='Python Test Harness.')
    parser.add_argument('-e', '--execute', help='Perform test execution', required=False, action='store_true')
    parser.add_argument('-v', '--verify', help='Perform test verification', required=False, action='store_true')
    parser.add_argument('-c', '--configure', help='Configure queuing system information', required=False, action='store_true')
    parser.add_argument('-t', '--test', help='List of test names', required=False)
    self.args = parser.parse_args()

    if self.args.configure:
      self.configure()
    else:
      self.setup()

    if self.use_batch == True:
      if self.mpiLaunch == 'none':
        raise ValueError('If using a queuing system, a valid mpi launch command must be provided')

#  def addIgnoreKeywords(self,d):
#    self.ignoreKeywords.append(d)


  def setQueueName(self,name):
    self.queueName = name


  def setHPCAccountName(self,name):
    self.accountName = name


  def setMPILaunch(self,name):
    self.mpiLaunch = name


  def setQueueSystemType(self,type):
    if type in ['PBS','pbs']:
      self.queuingSystemType = 'pbs'
      self.jobSubmissionCommand = 'qsub '
      self.use_batch = True
      #print('Recognized PBS queuing system')

    elif type in ['LSF','lsf']:
      self.queuingSystemType = 'lsf'
      self.jobSubmissionCommand = 'bsub < '
      self.use_batch = True
      #print('Recognized LSF queuing system')

    elif type in ['SLURM','slurm']:
      self.queuingSystemType = 'slurm'
      self.jobSubmissionCommand = 'sbatch '
      self.use_batch = True
      #print('Recognized Slurm queuing system')

    elif type in ['LoadLeveler','load_leveler','loadleveler','llq']:
      self.queuingSystemType = 'load_leveler'
      self.jobSubmissionCommand = 'llsubmit '
      self.use_batch = True
      #print('Recognized IBM LoadLeveler queuing system')

    elif type in ['none', 'None', 'local']:
      self.queuingSystemType = 'none'
      self.jobSubmissionCommand = ''
      #print('No queuing system being used')

    else:
      print('Value found: ' + type + ' ...' , flush=True)
      raise ValueError('Error: Unknown or unsupported batch queuing system specified')


  def setQueueName(self,name):
    self.queueName = name


  def view(self):
    print('pth: Batch queueing system configuration [zpthBatchQueingSystem.conf]')
    print('  Queue system:    ',self.queuingSystemType)
    print('  MPI launcher:    ',self.mpiLaunch)
    if self.use_batch:
      print('  Submit command:', self.jobSubmissionCommand , flush=True)
      if self.accountName:
        print('  Account:       ',self.accountName , flush=True)
      if self.queueName:
        print('  Queue:         ',self.queueName , flush=True)


  def configure(self):
    print('----------------------------------------------------------------' , flush=True)
    print('Creating new zpthBatchQueuingSystem.conf file' , flush=True)
    v = input('[1] Batch queuing system type <pbs,lsf,slurm,llq,none>: ')
    if not v:
      raise ValueError('You must specify the type of queuing system')
    self.setQueueSystemType(v)

    v = input('[2] MPI launch command with num. procs. flag (required): <none>')
    if not v:
      raise ValueError('Error: You must specify an MPI launch command')
    self.setMPILaunch(v)

    if self.use_batch == True:

      v = input('[3] Account to charge (optional - hit enter if not applicable): ')
      self.setHPCAccountName(v)

      v = input('[4] Name of queue to submit tests to (optional - hit enter if not applicable): ')
      self.setQueueName(v)
    
    self.writeDefinition()
    print('\n' , flush=True)
    print('** If you wish to change the config for your batch system, either' , flush=True)
    print('**   (i) delete the file zpthBatchQueuingSystem.conf, or' , flush=True)
    print('**  (ii) re-run zpth2.configure()' , flush=True)
    print('** (iii) re-run with the command line arg --configure' , flush=True)
    print('----------------------------------------------------------------' , flush=True)


  def setup(self):
    try:
      self.loadDefinition()
    
    except:
      self.configure()
      self.writeDefinition()


  def writeDefinition(self):

    file = open('zpthBatchQueuingSystem.conf','w')
    #    file.write('queuingSystemType = ' + self.queuingSystemType + '\n' )
    #    file.write('accountName = ' + self.accountName + '\n' )
    #    file.write('queueName = ' + self.queueName + '\n' )
    #    file.write('mpiLaunch = ' + self.mpiLaunch + '\n' )
    file.write( self.queuingSystemType + '\n' )
    file.write( self.mpiLaunch + '\n' )
    if self.use_batch == True:
      file.write( self.queueName + '\n' )
      file.write( self.accountName + '\n' )
    file.close()


  def loadDefinition(self):
    try:
      file = open('zpthBatchQueuingSystem.conf','r')

      v = file.readline()
      self.setQueueSystemType(v.rstrip())

      v = file.readline()
      self.setMPILaunch(v.rstrip())

      if self.use_batch == True:
        v = file.readline()
        self.setQueueName(v.rstrip())

        v = file.readline()
        self.setHPCAccountName(v.rstrip())

      file.close()
    except:
      raise ValueError('Error: You must execute configure(), and or writeDefinition() first')


  def createSubmissionFile(self,testname,commnd,ranks,ranks_per_node,walltime,outfile):
    filename = ''
    if not self.use_batch:
      print('Warning: no submission file creation required' , flush=True)
      return(filename)
    
    if self.queuingSystemType == 'pbs':
      filename = generateLaunch_PBS(self.accountName,self.queueName,testname,self.mpiLaunch,commnd,ranks,ranks_per_node,walltime,outfile)

    elif self.queuingSystemType == 'lsf':
      raise ValueError('Unsupported: LSF needs to be updated')

    elif self.queuingSystemType == 'slurm':
      filename = generateLaunch_SLURM(self.accountName,self.queueName,testname,self.mpiLaunch,commnd,ranks,ranks_per_node,walltime,outfile)

    elif self.queuingSystemType == 'load_leveler':
      raise ValueError('Unsupported: LoadLeveler needs to be updated')

    print('Created submission file:',filename , flush=True)
    return(filename)


  def submitJob(self,unittest):
    if not self.use_batch:
      mpiLaunch = self.mpiLaunch
    
      if self.mpiLaunch == 'none' and unittest.ranks != 1:
        print('[Failed to launch test \"' + unittest.name + '\" as test uses > 1 MPI ranks and no MPI launcher was provided]')
      else:
        if self.mpiLaunch == 'none':
          launchCmd = unittest.execute + " > " + unittest.output_file
        else:
          launchCmd = mpiLaunch + ' ' + str(unittest.ranks) + ' ' + unittest.execute + " > " + unittest.output_file
        print('[Executing] ',launchCmd , flush=True)
        os.system(launchCmd)
    else:
      launchfile = self.createSubmissionFile(unittest.name,unittest.execute,unittest.ranks,'',unittest.walltime,unittest.output_file)
      launchCmd = self.jobSubmissionCommand + launchfile
      print('[Executing] ',launchCmd , flush=True)
      os.system(launchCmd)


  def executeTestSuite(self,registered_tests):
    performTestSuite_execute(self,registered_tests)


  def verifyTestSuite(self,registered_tests):
    if self.use_batch:
      if self.args.verify:
        performTestSuite_verify(self,registered_tests)
    else:
      performTestSuite_verify(self,registered_tests)


# < end class >

def test1():
  batch = zpthBatchQueuingSystem()
  batch.configure()
  batch.view()

  batch2 = zpthBatchQueuingSystem()

  #conf.addIgnoreKeywords('**')
  #print(conf.ignoreKeywords)

  #batch.setQueueSystemType('llq')
  #batch.setMPILaunch('mpiexec')
  #batch.setHPCAccountName('geophys')
  #batch.setQueueName('small')

  batch2.view()

  launchfile = batch2.createSubmissionFile('ex1a','./ex1 -options_file go.fast',24,'',"00:05:00",'ex1a-p24.output')
  print('[To launch execute] ' + batch2.jobSubmissionCommand + launchfile , flush=True)

if __name__ == "__main__":
  test1()
