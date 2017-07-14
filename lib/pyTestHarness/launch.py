import os,sys
import argparse
import shutil
import pyTestHarness.unittest as pth
from   pyTestHarness.colors import pthNamedColors as bcolors
from   pyTestHarness.version import getVersion
from   pyTestHarness.utils import py23input

class PthTestHarnessLoadException(Exception) :
  pass

def FormattedHourMin(seconds):
  m, s = divmod(int(seconds), 60)
  h, m = divmod(m, 60)
  wt = "%02d:%02d" % (h, m)
  return(wt)

def FormattedHourMinSec(seconds):
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)
  wt = "%02d:%02d:%02d" % (h, m,s)
  return(wt)

def pthFormatMPILaunchCommand(mpiLaunch,ranks,corespernode):
  launch = mpiLaunch
  launch = launch.replace("<ranks>",str(ranks))
  launch = launch.replace("<cores>",str(ranks))
  launch = launch.replace("<tasks>",str(ranks))
  launch = launch.replace("<RANKS>",str(ranks))
  if corespernode:
    launch = launch.replace("<corespernode>",str(corespernode))
    launch = launch.replace("<cores_per_node>",str(corespernode))
    launch = launch.replace("<CORESPERNODE>",str(corespernode))
    launch = launch.replace("<CORES_PER_NODE>",str(corespernode))
    launch = launch.replace("<rankspernode>",str(corespernode))
    launch = launch.replace("<ranks_per_node>",str(corespernode))
    launch = launch.replace("<RANKSPERNODE>",str(corespernode))
    launch = launch.replace("<RANKS_PER_NODE>",str(corespernode))
  return(launch)

def generateLaunch_PBS(accountname,queuename,testname,mpiLaunch,executable,ranks,ranks_per_node,walltime,outfile):
  if not ranks:
    print("<generateLaunch_PBS>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_PBS>: Requires the walltime be specified")

  filename = testname + '-pth.pbs'
  file = open(filename,"w")
  file.write("#!/bin/bash\n")

  file.write("# pyTH: auto-generated pbs file\n")

  if accountname:
    file.write("#PBS -A " + accountname + "\n") # account to charge
  file.write("#PBS -N \"" + testname + "\"" + "\n") # jobname
  file.write("#PBS -o " + testname + ".stdout" + "\n")
  file.write("#PBS -e " + testname + ".stderr" + "\n")

  if queuename:
    file.write("#PBS -q " + queuename + "\n")

  wt = FormattedHourMinSec(walltime*60.0)
  file.write("#PBS -l mppwidth=1024,walltime=" + wt + "\n")

  launch = pthFormatMPILaunchCommand(mpiLaunch,ranks,ranks_per_node)
  file.write(launch + " " + executable + " > " + outfile + "\n\n") # launch command
  file.close()
  return(filename)

def generateLaunch_SLURM(accountname,queuename,testname,constraint,mpiLaunch,executable,ranks,ranks_per_node,walltime,outfile):
  if not ranks:
    print("<generateLaunch_SLURM>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_SLURM>: Requires the walltime be specified")

  filename = testname + '-pth.slurm'
  file = open(filename,"w")
  file.write("#!/bin/bash -l\n")

  file.write("# pyTH: auto-generated slurm file\n")
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

  wt = FormattedHourMinSec(walltime*60.0)
  file.write("#SBATCH --time=" + wt + "\n")

  if constraint :
    file.write("#SBATCH --constraint=" + constraint + "\n")

  launch = pthFormatMPILaunchCommand(mpiLaunch,ranks,ranks_per_node)
  file.write(launch + " " + executable + " > " + outfile + "\n\n") # launch command
  file.close()
  return(filename)

def generateLaunch_LSF(accountname,queuename,testname,mpiLaunch,executable,ranks,rusage,walltime,outfile):
  if not ranks:
    print("<generateLaunch_LSF>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_LSF>: Requires the walltime be specified")

  filename = testname + '-pth.lsf'
  file = open(filename,"w")
  file.write("#!/bin/sh\n")

  file.write("# pyTH: auto-generated lsf file\n")

  file.write("#BSUB -J " + testname + "\n") # jobname

  file.write("#BSUB -o " + testname + ".stdout\n") # jobname.stdout
  file.write("#BSUB -e " + testname + ".stderr\n") # jobname.stderr

  if queuename:
    file.write("#BSUB -q " + queuename + "\n")

  file.write("#BSUB -n " + str(ranks) + "\n")

  if rusage:
    file.write("#BSUB -R \'" + rusage + "\'" + "\n")

  wt = FormattedHourMin(walltime*60.0) 
  file.write("#BSUB -W " + wt + "\n")

  launch = pthFormatMPILaunchCommand(mpiLaunch,ranks,None)
  file.write(launch + " " + executable + " > " + outfile + "\n\n") # launch command
  file.close()
  return(filename)

def generateLaunch_LoadLevelerBG(accountname,queuename,testname,executable,total_ranks,machine_ranks_per_node,walltime):
  if not total_ranks:
    print("<generateLaunch_LoadLeveler>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_LoadLeveler>: Requires the walltime be specified")

  print("#!/bin/sh")
  print("# pyTH: auto-generated llq file")
  print("# @ job_name = " + testname)
  print("# @ job_type = bluegene")
  print("# @ error = $(job_name)_$(jobid).stderr")
  print("# @ output = $(job_name)_$(jobid).stdout")
  print("# @ environment = COPY_ALL;")
  wt = FormattedHourMinSec(walltime*60.0)
  print("# @ wall_clock_limit = " + wt)
  print("# @ notification = never")
  print("# @ class = " + queuename)

  bgsize = math.ceil(total_ranks/machine_ranks_per_node)
  print("# @ bg_size = " + str(bgsize))
  print("# @ bg_connection = TORUS")
  print("# @ queue")

  print("runjob -n " + executable) # launch command


class pthLaunch:
  def __init__(self,args):
    self.accountName = []
    self.queueName = []
    self.mpiLaunch = []
    self.queuingSystemType = []
    self.batchConstraint=[]
    self.jobSubmissionCommand = []
    self.use_batch = False
    self.output_path = ''
    self.verbosity_level = 1
    self.confFileName = 'pthBatchQueuingSystem.conf'

    self.args = args

    if self.args.configure:
      self.configure()
      sys.exit(0)
    elif self.args.configure_default:
      self.writeDefaultDefinition()
      sys.exit(0)
    else:
      self.setup()

    if self.use_batch :
      if self.mpiLaunch == 'none':
        raise RuntimeError('[pth] If using a queuing system, a valid mpi launch command must be provided')

  def setVerbosityLevel(self,value):
    self.verbosity_level = value

  def setQueueName(self,name):
    self.queueName = name

  def setBatchConstraint(self,argstring):
    self.batchConstraint=argstring

  def setHPCAccountName(self,name):
    self.accountName = name

  def setMPILaunch(self,name):
    self.mpiLaunch = name
    # check for existence of "rank" keyword in the string "name"
    if self.queuingSystemType in ['none', 'None', 'local'] and name != 'none':
      keywordlist = [ '<ranks>', '<cores>', '<tasks>', '<RANKS>' ]
      # check of any of keywordlist[i] appears in name
      valid_launcher = False
      for kword in keywordlist:
        if kword in name:
          valid_launcher = True
          break

      if valid_launcher == False:
        raise RuntimeError('[pth] Your MPI launch command must contain the keyword \"<ranks>\"')

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
      print('Value found: ' + type + ' ...')
      raise RuntimeError('[pth] Unknown or unsupported batch queuing system specified')

  def setQueueName(self,name):
    self.queueName = name

  def view(self):
    print('pth: Batch queueing system configuration [',self.confFileName,']')
    print('  Queue system:    ',self.queuingSystemType)
    print('  MPI launcher:    ',self.mpiLaunch)
    if self.use_batch:
      print('  Submit command:', self.jobSubmissionCommand)
      if self.accountName:
        print('  Account:       ',self.accountName)
      if self.queueName:
        print('  Queue:         ',self.queueName)
      if self.batchConstraint :
        print('  Constraint:    ', self.batchConstraint)

  def configure(self):
    print('----------------------------------------------------------------')
    print('Creating new',self.confFileName,'file')
    prompt = '[1] Batch queuing system type <pbs,lsf,slurm,llq,none>: '
    v = py23input(prompt)
    if not v:
      raise ValueError('[pth] You must specify the type of queuing system')
    self.setQueueSystemType(v)

    v = None
    while not v:
      prompt = '[2] MPI launch command with num. procs. flag (required - hit enter for examples): '
      v = py23input(prompt)
      if not v :
        print(' Required. Some example MPI launch commands:')
        print('  none','(if your tests do not use MPI)')
        print('  mpirun -np <ranks>','(local machine)')
        print('  mpiexec -n <ranks>','(local machine)')
        print('  aprun -B','(slurm with aprun)')
        print('  srun -n $SLURM_NTASKS','(native slurm)')
        print('  /users/myname/petsc/bin/petscmpiexec -n <ranks>','(typical PETSc MPI wrapper)')
        print(' Note that the string \"<ranks>\" must be included in your launch command.')
        print(' The keyword <ranks> will be replaced by the actual number of MPI ranks (defined by a given test) when the test is launched.')
    self.setMPILaunch(v)

    if self.use_batch == True:
      prompt = '[3] specify a constraint (e.g. "gpu" on Piz Daint) (optional - hit enter if not applicable):'
      v = None
      v = py23input(prompt)
      if v :
        self.setBatchConstraint(v)

      prompt = '[4] Account to charge (optional - hit enter if not applicable): '
      v = py23input(prompt)
      self.setHPCAccountName(v)

      prompt = '[5] Name of queue to submit tests to (optional - hit enter if not applicable): '
      v = py23input(prompt)
      self.setQueueName(v)

    self.writeDefinition()
    print('\n')
    print('** If you wish to change the config for your batch system, either')
    print('**   (i) delete the file',self.confFileName,' or')
    print('**  (ii) re-run pth2.configure()')
    print('** (iii) re-run with the command line arg --configure')
    print('----------------------------------------------------------------')

  def setup(self):
    try:
      self.loadDefinition()
    except PthTestHarnessLoadException :
      self.configure()
      self.writeDefinition()

  def writeDefaultDefinition(self):
    file = open(self.confFileName,'w')
    major,minor,patch=getVersion()
    file.write('majorVersion=' + str(major) + '\n')
    file.write('minorVersion=' + str(minor) + '\n')
    file.write('patchVersion=' + str(patch) + '\n')
    file.write('queuingSystemType=none\n' )
    file.write('mpiLaunch=none\n' )
    file.close()

  def writeDefinition(self):
    file = open(self.confFileName,'w')
    major,minor,patch=getVersion()
    file.write('majorVersion=' + str(major) + '\n')
    file.write('minorVersion=' + str(minor) + '\n')
    file.write('patchVersion=' + str(patch) + '\n')
    file.write('queuingSystemType=' + self.queuingSystemType + '\n')
    file.write('mpiLaunch=' + self.mpiLaunch + '\n')
    if self.use_batch == True:
      file.write('accountName=' + self.accountName + '\n')
      file.write('batchConstraint=' + self.batchConstraint + '\n')
      file.write('queueName=' + self.queueName + '\n')
    file.close()

  def loadDefinition(self):
    try:
      majorFile = None
      minorFile = None
      patchFile = None
      file = open(self.confFileName,'r')
      for v in file :
        key,value = v.split('=',1)
        value = value.rstrip()
        if key == 'majorVersion' :
          majorFile = int(value)
        if key == 'minorVersion' :
          minorFile = int(value)
        if key == 'patchVersion' :
          patchFile = int(value)
        if key == 'queuingSystemType' :
          self.setQueueSystemType(value)
        if key == 'mpiLaunch' :
          self.setMPILaunch(value)
        if self.use_batch == True:
          if key == 'batchConstraint' :
            self.setBatchConstraint(value)
          if key == 'queueName' :
            self.setQueueName(value)
          if key == 'accountName' :
            self.setHPCAccountName(value)
      file.close()
    except:
      raise PthTestHarnessLoadException('[pth] You must execute configure(), and or writeDefinition() first')

    # Do not accept conf files if the major.minor version is stale, or if versions are missing
    major,minor,patch = getVersion()
    if majorFile < major or (minorFile < minor and majorFile == major) or \
         majorFile==None or minorFile==None or patchFile==None :
      print('[pth] Incompatible outdated,',self.confFileName,'file detected. Please delete it and run again to generate a new one.')
      raise RuntimeError(message)

  def createSubmissionFile(self,testname,commnd,ranks,ranks_per_node,walltime,outfile):
    filename = ''
    if not self.use_batch:
      print('Warning: no submission file creation required')
      return(filename)

    if self.batchConstraint and self.queuingSystemType != 'slurm' :
      message = '[pth] Constraints are only currently supported with SLURM'
      raise RuntimeError(message)

    if self.queuingSystemType == 'pbs':
      filename = generateLaunch_PBS(self.accountName,self.queueName,testname,self.mpiLaunch,commnd,ranks,ranks_per_node,walltime,outfile)

    elif self.queuingSystemType == 'lsf':
      filename = generateLaunch_LSF(self.accountName,self.queueName,testname,self.mpiLaunch,commnd,ranks,None,walltime,outfile)

    elif self.queuingSystemType == 'slurm':
      filename = generateLaunch_SLURM(self.accountName,self.queueName,testname,self.batchConstraint,self.mpiLaunch,commnd,ranks,ranks_per_node,walltime,outfile)

    elif self.queuingSystemType == 'load_leveler':
      raise ValueError('[pth] Unsupported: LoadLeveler needs to be updated')

    print('Created submission file:',filename)
    return(filename)

  def submitJob(self,unittest):
    if self.args.sandbox :
        unittest.use_sandbox = True
        sandboxBack = os.getcwd()
        os.mkdir(unittest.sandbox_path) # error if  it already exists
        os.chdir(unittest.sandbox_path)
    unittest.setVerbosityLevel(self.verbosity_level)
    if not self.use_batch:
      mpiLaunch = self.mpiLaunch

      if self.mpiLaunch == 'none' and unittest.ranks != 1:
        print('[Failed to launch test \"' + unittest.name + '\" as test uses > 1 MPI ranks and no MPI launcher was provided]')
      else:
        if self.mpiLaunch == 'none':
          launchCmd = unittest.execute + " > " + os.path.join(unittest.output_path,unittest.output_file)
        else:
          launch = pthFormatMPILaunchCommand(mpiLaunch,unittest.ranks,None)
          launchCmd = launch + ' ' + unittest.execute + " > " + os.path.join(unittest.output_path,unittest.output_file)
        if self.verbosity_level > 0:
          if self.args.sandbox :
            print('[Executing from ' + os.getcwd() + ']',launchCmd)
          else :
            print('[Executing]',launchCmd)
        unittest.errno = os.system(launchCmd) >> 8
    else:
      outfile = os.path.join(unittest.output_path,unittest.output_file)
      launchfile = self.createSubmissionFile(unittest.name,unittest.execute,unittest.ranks,'',unittest.walltime,outfile)
      launchCmd = self.jobSubmissionCommand + launchfile
      if self.verbosity_level > 0:
        if self.args.sandbox :
          print('[Executing from ' + os.getcwd() + ']',launchCmd)
        else :
          print('[Executing]',launchCmd)
      os.system(launchCmd)

    if self.args.sandbox :
        os.chdir(sandboxBack)

  def clean(self,registered_tests):
    for test in registered_tests:
      print('[ removing output for ' + test.name +' ]')
      if self.args.sandbox :
        test.use_sandbox = True
        sandboxBack = os.getcwd()
        if not os.path.isdir(test.sandbox_path) :
            os.mkdir(test.sandbox_path)
        os.chdir(test.sandbox_path)
      outfile = os.path.join(test.output_path,test.output_file)
      if os.path.isfile(outfile) :
        os.remove(outfile)
      if test.comparison_file != outfile and os.path.isfile(test.comparison_file) :
        foundInLocalTree = False
        cwd = os.getcwd()
        for (root, dirs, files) in os.walk(cwd) :
          for f in files :
            if os.path.abspath(test.comparison_file) == os.path.abspath(os.path.join(root,f)) :
              foundInLocalTree = True
              break
          if foundInLocalTree :
            break
        if foundInLocalTree :
          os.remove(test.comparison_file)
        else :
          message = "Refusing to remove output file " + test.comparison_file + " since it does not live in the local subtree. If you really wanted to compare with this file, please delete it yourself to proceed"
          raise RuntimeError(message)
      if self.use_batch:
        stderrFile = test.name + '.stderr'
        if os.path.isfile(stderrFile) :
          os.remove(stderrFile)
        stdoutFile = test.name + '.stdout'
        if os.path.isfile(stdoutFile) :
          os.remove(stdoutFile)
        if self.queuingSystemType == 'pbs':
          pbsFile = test.name + '-pth.pbs'
          if os.path.isfile(pbsFile) :
            os.remove(pbsFile)
        elif self.queuingSystemType == 'lsf':
          lsfFile = test.name + '-pth.lsf'
          if os.path.isfile(lsfFile) :
            os.remove(lsfFile)
        elif self.queuingSystemType == 'slurm':
          slurmFile = test.name + '-pth.slurm'
          if os.path.isfile(slurmFile) :
            os.remove(slurmFile)
        elif self.queuingSystemType == 'load_leveler':
          llqFile = test.name + '-pth.llq'
          if os.path.isfile(llqFile) :
            os.remove(llqFile)

      if self.args.sandbox :
        os.chdir(sandboxBack)
        shutil.rmtree(test.sandbox_path) # remove entire subtree

# < end class >
