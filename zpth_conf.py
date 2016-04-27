
import os
import zpth2 as pth


def generateLaunch_PBS(accountname,queuename,testname,mpiLaunch,executable,ranks,ranks_per_node,walltime,outfile):
  if not ranks:
    print("<generateLaunch_PBS>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_PBS>: Requires the walltime be specified")
  
  filename = testname + '-zpth.pbs'
  file = open(filename,"w")
  file.write("# ZPTH: auto-generated pbs file\n")
  file.write("#!/bin/bash\n")
  
  if accountname:
    file.write("#PBS -A " + accountname + "\n") # account to charge
  file.write("#PBS -N \"" + testname + "\"" + "\n") # jobname
  file.write("#PBS -o " + testname + ".stdout" + "\n")
  file.write("#PBS -e " + testname + ".stderr" + "\n")
  
  if queuename:
    file.write("#PBS -q " + queuename + "\n")
  
  file.write("#PBS -l mppwidth=1024,walltime=" + str(walltime) + "\n")
  
  file.write(mpiLaunch + " " + executable + " > " + outfile + "\n") # launch command
  file.close()
  return(filename)

def generateLaunch_SLURM(accountname,queuename,testname,executable,ranks,ranks_per_node,walltime):
  if not ranks:
    print("<generateLaunch_SLURM>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_SLURM>: Requires the walltime be specified")
  
  print("# ZPTH: auto-generated slurm file")
  print("#!/bin/bash -l")
  
  if accountname:
    print("#SBATCH --account=" + accountname + "") # account to charge
  print("#SBATCH --job-name=\"" + testname + "\"") # jobname
  
  print("#SBATCH --output=" + testname + ".stdout") # jobname.stdout
  print("#SBATCH --error=" + testname + ".stderr") # jobname.stderr
  
  if queuename:
    print("#SBATCH --partition=" + queuename)
  
  print("#SBATCH --ntasks=" + str(ranks))
  if ranks_per_node:
    print("#SBATCH --ntasks-per-node=" + str(ranks_per_node))
  
  print("#SBATCH --time=" + walltime)
  
  print("aprun -n " + executable) # launch command


def generateLaunch_LSF(accountname,queuename,testname,executable,ranks,rusage,walltime):
  if not ranks:
    print("<generateLaunch_LSF>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_LSF>: Requires the walltime be specified")
  
  print("# ZPTH: auto-generated lsf file")
  print("#!/bin/sh")
  
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
    print("<generateLaunch_LoadLeveler>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_LoadLeveler>: Requires the walltime be specified")
  
  print("# ZPTH: auto-generated llq file")
  
  print("#!/bin/sh")
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
  
  launcher = batch.zpthBatchQueuingSystem()
  
  for test in registered_tests:
    launcher.submitJob(test)
    test.verifyOutput()
  
  print('-- Unit test report --')
  counter = 0
  for test in registered_tests:
    test.report('summary')
    if test.passed == False:
      counter = counter + 1
  if counter > 0:
    print('  ' + str(counter) + ' / ' + str(len(registered_tests)) + ' tests failed')
  else:
    print('  All tests passed')
  
  print('-- Unit test error messages --')
  for test in registered_tests:
    test.report('log')


def performTestSuite_batch_launch(self,registered_tests):
  launcher = self

  for test in registered_tests:
    launcher.submitJob(test)


def performTestSuite_batch_verify(self,registered_tests):
  launcher = self
  
  for test in registered_tests:
    test.verifyOutput()
  
  print('-- Unit test report --')
  counter = 0
  for test in registered_tests:
    test.report('summary')
    if test.passed == False:
      counter = counter + 1
  if counter > 0:
    print('  ' + str(counter) + ' / ' + str(len(registered_tests)) + ' tests failed')
  else:
    print('  All tests passed')
  
  print('-- Unit test error messages --')
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
      print('Recognized PBS queuing system')

    elif type in ['LSF','lsf']:
      self.queuingSystemType = 'lsf'
      self.jobSubmissionCommand = 'bsub < '
      self.use_batch = True
      print('Recognized LSF queuing system')

    elif type in ['SLURM','slurm']:
      self.queuingSystemType = 'slurm'
      self.jobSubmissionCommand = 'sbatch '
      self.use_batch = True
      print('Recognized Slurm queuing system')

    elif type in ['LoadLeveler','load_leveler','loadleveler','llq']:
      self.queuingSystemType = 'load_leveler'
      self.jobSubmissionCommand = 'llsubmit '
      self.use_batch = True
      print('Recognized IBM LoadLeveler queuing system')

    elif type in ['none', 'None', 'local']:
      self.queuingSystemType = 'none'
      self.jobSubmissionCommand = ''
      print('No queuing system being used')

    else:
      print('Value found: ' + type + ' ...')
      raise ValueError('Unknown or unsupported batch queuing system specified')


  def setQueueName(self,name):
    self.queueName = name


  def view(self):
    print('zpthBatchQueuingSystem:')
    print('  System:        ',self.queuingSystemType)
    print('  Submit command:', self.jobSubmissionCommand)
    print('  MPI launcher:    ',self.mpiLaunch)
    if self.accountName:
      print('  Account:       ',self.accountName)
    if self.queueName:
      print('  Queue:         ',self.queueName)


  def configure(self):
    print('----------------------------------------------------------------')
    print('Creating new zpthBatchQueuingSystem.conf file')
    v = input('[1] Batch queuing system type <pbs,lsf,slurm,llq,none>: ')
    if not v:
      raise ValueError('You must specify the type of queuing system')
    self.setQueueSystemType(v)

    v = input('[2] MPI launch command (required): ')
    if not v:
      raise ValueError('Error: You must specify an MPI launch command')
    self.setMPILaunch(v)

    if self.use_batch == True:

      v = input('[3] Account to charge (optional - hit enter if not applicable): ')
      self.setHPCAccountName(v)

      v = input('[4] Name of queue to submit tests to (optional - hit enter if not applicable): ')
      self.setQueueName(v)
    
    self.writeDefinition()
    print('\n')
    print('** If you wish to change the config for your batch system, either')
    print('** (i) delete the file zpthBatchQueuingSystem.conf, or')
    print('** (ii) re-run zpth2.configure()')
    print('----------------------------------------------------------------')


  def reconfigure(self):
    try:
      self.loadDefinition()
    
    except:
      print('Creating new .conf file')
      v = input('Batch queuing system type <pbs,lsf,slurm,llq,none>: ')
      if not v:
        raise ValueError('You must specify the type of queuing system')
      self.setQueueSystemType(v)
      
      v = input('MPI launch command (required): ')
      if not v:
        raise ValueError('You must specify an MPI launch command')
      self.setMPILaunch(v)
      
      v = input('Account to charge (optional - hit enter if not applicable): ')
      self.setHPCAccountName(v)
      
      v = input('Queue name to submit tests to (optional - hit enter if not applicable): ')
      self.setQueueName(v)
      
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
    if self.queuingSystemType == 'pbs':
      filename = generateLaunch_PBS(self.accountName,self.queueName,testname,self.mpiLaunch,commnd,ranks,ranks_per_node,walltime,outfile)

    print('To launch execute: ' + self.jobSubmissionCommand + filename)
    return(filename)

  def submitJob(self,unittest):
    if not self.use_batch:
      launchCmd = self.mpiLaunch + ' ' + str(unittest.ranks) + ' ' + unittest.execute + " > " + unittest.output_file
      print('Execute ',launchCmd)
      os.system(launchCmd)
    else:
      print('Call createSubmissionFile() then launch')
      self.createSubmissionFile(unittest.name,unittest.execute,unittest.ranks,'',unittest.walltime,unittest.output_file)



# < end class >

def test1():
  batch = zpthBatchQueuingSystem()
  batch.configure()
  batch.view()

  batch2 = zpthBatchQueuingSystem()
  batch2.reconfigure()

  #conf.addIgnoreKeywords('**')
  #print(conf.ignoreKeywords)

  #batch.setQueueSystemType('llq')
  #batch.setMPILaunch('mpiexec')
  #batch.setHPCAccountName('geophys')
  #batch.setQueueName('small')

  batch2.view()

  batch2.createSubmissionFile('ex1a','./ex1 -options_file go.fast',24,6,"00:05:00",'ex1a-p24.output')

if __name__ == "__main__":
  test1()
