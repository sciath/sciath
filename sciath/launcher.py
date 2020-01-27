from __future__ import print_function
import os
import sys
import shutil
import fcntl
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess # To be removed once Python 2 is fully abandoned
else:
    import subprocess
from   sciath import sciath_colors
from   sciath import getVersion
from   sciath._io import py23input, _remove_file

# mpiexec has been observed to set non-blocking I/O, which
#  has been observed to cause problems on OS X with errors like
#  "BlockingIOError: [Errno 35] write could not complete without blocking"
# We use this function to (re)set blocking I/O when launching
def setBlockingIOStdout() :
    fd = sys.stdout
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    if flags & os.O_NONBLOCK:
        fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)

class SciATHLoadException(Exception) :
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

def formatMPILaunchCommand(mpiLaunch,ranks,corespernode):
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
    return launch.split()


# Returns name lists for error-code file (one per job), stdout, stderr
def _getLaunchStandardOutputFileNames(job):
    jobnames = []
    try:
        jobnames = job.createJobOrdering()
    except:
        jobnames.append(job.name)

    errorCodeName = "sciath.job-" +  job.name + ".errorcode"
    stdoutName = []
    stderrName = []

    lc_count = len(jobnames)
    for i in range(0,len(jobnames)):
        jprefix = "".join(["sciath.depjob-",str(lc_count),'-',jobnames[i]])
        if lc_count == 1: # we do something special for the last job in a sequence/DAG list
            jprefix = "sciath.job-" + job.name
        
        stdoutName.append( jprefix + ".stdout" )
        stderrName.append( jprefix + ".stderr" )

        lc_count -= 1

    return errorCodeName, stdoutName, stderrName

def _generateLaunch_PBS(launcher,walltime,output_path,job):
  
    if walltime is None:
        message = "[SciATH] _generateLaunch_PBS requires walltime be specified"
        raise RuntimeError(message)
    
    accountname = launcher.accountName
    queuename = launcher.queueName
    mpiLaunch = launcher.mpiLaunch
    
    resources = job.getMaxResources()
    ranks = resources["mpiranks"]
    idle_ranks_per_node = resources["idlempirankspernode"]
    ranks_per_node = None
    # TODO: Need logic here to compute the number of ranks per node

    c_name,o_name,e_name = _getLaunchStandardOutputFileNames(job)

    filename = os.path.join(output_path,"sciath.job-" + job.name + "-launch." + launcher.queueFileExt)
    file = open(filename,"w")

    # PBS specifics
    file.write("#!/bin/bash\n")
    file.write("# SciATH: auto-generated pbs file\n")
    
    if accountname:
        file.write("#PBS -A " + accountname + "\n") # account to charge

    file.write("#PBS -N \"" + "sciath.job-" + job.name + "\"" + "\n") # jobname
    file.write("#PBS -o " + os.path.join(output_path,o_name[-1]) + "\n")
    file.write("#PBS -e " + os.path.join(output_path,e_name[-1]) + "\n")
    
    if queuename:
        file.write("#PBS -q " + queuename + "\n")
    
    wt = FormattedHourMinSec(float(walltime)*60.0)
    file.write("#PBS -l mppwidth=1024,walltime=" + wt + "\n")

    # Write out the list of jobs execute commands
    # Dependent jobs have their stdout collected in separate files (one per job)
    # The stdout/stderr for the parent job is collected via the queue system

    _remove_file( os.path.join(output_path,c_name) )

    command_resource = job.createExecuteCommand()
    njobs = len(command_resource)
    for i in range(0,njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += formatMPILaunchCommand(mpiLaunch,j_ranks,ranks_per_node)
        if isinstance(j[0], list):
            for c in j[0]:
                launch.append(c)
        else:
            launch.append(j[0])
        
        if i < njobs-1:
            file.write(" ".join(launch) + " > " + os.path.join(output_path,o_name[i]) + "\n") # launch command
            file.write("echo $? >> " + os.path.join(output_path,c_name) + "\n")
    # Command for the parent job
    file.write(" ".join(launch) + "\n") # launch command
    file.write("echo $? >> " + os.path.join(output_path,c_name) + "\n")
    file.write("\n")

    file.close()
    return filename

def _generateLaunch_LSF(launcher,rusage,walltime,output_path,job):

    if walltime is None:
        message = "[SciATH] _generateLaunch_LSF requires walltime be specified"
        raise RuntimeError(message)

    accountname = launcher.accountName
    queuename = launcher.queueName
    mpiLaunch = launcher.mpiLaunch
    
    resources = job.getMaxResources()
    ranks = resources["mpiranks"]
    idle_ranks_per_node = resources["idlempirankspernode"]
    ranks_per_node = None
    # TODO: Need logic here to compute the number of ranks per node
    
    c_name,o_name,e_name = _getLaunchStandardOutputFileNames(job)
  
    filename = os.path.join(output_path,"sciath.job-" + job.name + "-launch." + launcher.queueFileExt)
    file = open(filename,"w")

    # LSF specifics
    file.write("#!/bin/sh\n")
    file.write("# SciATH: auto-generated lsf file\n")

    if accountname:
        file.write("#BSUB -G " + accountname + "\n")

    file.write("#BSUB -J " + "sciath.job-" + job.name + "\n") # jobname
    file.write("#BSUB -o " + os.path.join(output_path,o_name[-1]) + "\n") # jobname.stdout
    file.write("#BSUB -e " + os.path.join(output_path,e_name[-1]) + "\n") # jobname.stderr

    if queuename:
        file.write("#BSUB -q " + queuename + "\n")
    
    file.write("#BSUB -n " + str(ranks) + "\n")

    if rusage:
        file.write("#BSUB -R \'" + rusage + "\'" + "\n")
    
    wt = FormattedHourMin(float(walltime)*60.0)
    file.write("#BSUB -W " + wt + "\n")
    
    # Write out the list of jobs execute commands
    # Dependent jobs have their stdout collected in separate files (one per job)
    # The stdout/stderr for the parent job is collected via the queue system

    _remove_file( os.path.join(output_path,c_name) )
  
    command_resource = job.createExecuteCommand()
    njobs = len(command_resource)
    for i in range(0,njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += formatMPILaunchCommand(mpiLaunch,j_ranks,ranks_per_node)
        if isinstance(j[0], list):
            for c in j[0]:
                launch.append(c)
        else:
            launch.append(j[0])
        
        if i < njobs-1:
            file.write(" ".join(launch) + " > " + os.path.join(output_path,o_name[i]) + "\n") # launch command
            file.write("echo $? >> " + os.path.join(output_path,c_name) + "\n")
    # Command for the parent job
    file.write(" ".join(launch) + "\n") # launch command
    file.write("echo $? >> " + os.path.join(output_path,c_name) + "\n")
    file.write("\n")
    
    file.close()
    return filename



def _generateLaunch_SLURM(launcher,walltime,output_path,job):
  
    if walltime is None:
      message = "[SciATH] _generateLaunch_SLURM requires walltime be specified"
      raise RuntimeError(message)
  
    accountname = launcher.accountName
    queuename = launcher.queueName
    constraint = launcher.batchConstraint
    mpiLaunch = launcher.mpiLaunch
  
    resources = job.getMaxResources()
    ranks = resources["mpiranks"]
    idle_ranks_per_node = resources["idlempirankspernode"]
    ranks_per_node = None
    # TODO: Need logic here to compute the number of ranks per node

    c_name,o_name,e_name = _getLaunchStandardOutputFileNames(job)
  
    filename = os.path.join(output_path,"sciath.job-" + job.name + "-launch." + launcher.queueFileExt)
    file = open(filename,"w")

    # SLURM specifics
    file.write("#!/bin/bash -l\n")
    file.write("# SciATH: auto-generated slurm file\n")

    if accountname:
        file.write("#SBATCH --account=" + accountname + "\n") # account to charge

    file.write("#SBATCH --job-name=\"" + "sciath.job-" + job.name + "\"" + "\n") # jobname
    file.write("#SBATCH --output=" + os.path.join(output_path,o_name[-1]) + "\n") # jobname.stdout
    file.write("#SBATCH --error=" + os.path.join(output_path,e_name[-1]) + "\n") # jobname.stderr

    if queuename:
        file.write("#SBATCH --partition=" + queuename + "\n")
    
    file.write("#SBATCH --ntasks=" + str(ranks) + "\n")
    #if ranks_per_node:
    #  file.write("#SBATCH --ntasks-per-node=" + str(ranks_per_node) + "\n")
  
    if constraint :
        file.write("#SBATCH --constraint=" + constraint + "\n")

    wt = FormattedHourMinSec(float(walltime)*60.0)
    file.write("#SBATCH --time=" + wt + "\n")
    

    # Write out the list of jobs execute commands
    # Dependent jobs have their stdout collected in separate files (one per job)
    # The stdout/stderr for the parent job is collected via the queue system

    _remove_file( os.path.join(output_path,c_name) )
  
    command_resource = job.createExecuteCommand()
    njobs = len(command_resource)
    for i in range(0,njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += formatMPILaunchCommand(mpiLaunch,j_ranks,ranks_per_node)
        if isinstance(j[0], list):
            for c in j[0]:
                launch.append(c)
        else:
            launch.append(j[0])
        
        if i < njobs-1:
            file.write(" ".join(launch) + " > " + os.path.join(output_path,o_name[i]) + "\n") # launch command
            file.write("echo $? >> " + os.path.join(output_path,c_name) + "\n")
    # Command for the parent job
    file.write(" ".join(launch) + "\n") # launch command
    file.write("echo $? >> " + os.path.join(output_path,c_name) + "\n")
    file.write("\n")

    file.close()
    return filename


class Launcher:
    defaultConfFileName = 'SciATHBatchQueuingSystem.conf'

    @staticmethod
    def writeDefaultDefinition(confFileNameIn=None):
        confFileName = confFileNameIn if confFileNameIn else Launcher.defaultConfFileName
        file = open(confFileName,'w')
        major,minor,patch=getVersion()
        file.write('majorVersion=' + str(major) + '\n')
        file.write('minorVersion=' + str(minor) + '\n')
        file.write('patchVersion=' + str(patch) + '\n')
        file.write('queuingSystemType=none\n' )
        file.write('mpiLaunch=none\n' )
        file.close()

    def __init__(self,confFileName=None):
        self.accountName = []
        self.queueName = []
        self.mpiLaunch = []
        self.queuingSystemType = []
        self.maxRanksPerNode = None
        self.batchConstraint = []
        self.jobSubmissionCommand = []
        self.useBatch = False
        self.verbosity_level = 1
        if confFileName :
            self.confFileName = confFileName
        else :
            self.confFileName = Launcher.defaultConfFileName

        self.setup()

        if self.useBatch :
            if self.mpiLaunch == 'none':
                raise RuntimeError('[SciATH] If using a queuing system, a valid mpi launch command must be provided')

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
                raise RuntimeError('[SciATH] Your MPI launch command must contain the keyword \"<ranks>\"')

    def setQueueSystemType(self,type):
        if type in ['PBS','pbs']:
            self.queuingSystemType = 'pbs'
            self.jobSubmissionCommand = 'qsub'
            self.useBatch = True
            self.queueFileExt = 'pbs'

        elif type in ['LSF','lsf']:
            self.queuingSystemType = 'lsf'
            self.jobSubmissionCommand = 'sh -c \'bsub < $0\'' # Note single (escaped) quotes. This is a trick to interpret "<".
            self.useBatch = True
            self.queueFileExt = 'lsf'

        elif type in ['SLURM','slurm']:
            self.queuingSystemType = 'slurm'
            self.jobSubmissionCommand = 'sbatch'
            self.useBatch = True
            self.queueFileExt = 'slurm'

        elif type in ['LoadLeveler','load_leveler','loadleveler','llq']:
            self.queuingSystemType = 'load_leveler'
            self.jobSubmissionCommand = 'llsubmit'
            self.useBatch = True
            self.queueFileExt = 'llq'
            raise ValueError('[SciATH] Unsupported: LoadLeveler needs to be updated')

        elif type in ['none', 'None', 'local']:
            self.queuingSystemType = 'none'
            self.jobSubmissionCommand = ''
            self.queueFileExt = None

        else:
            raise RuntimeError('[SciATH] Unknown or unsupported batch queuing system "' + type + '" specified')

    def setMaxRanksPerNode(self,n):
        """ Store an int-valued maximum number of MPI ranks per node """
        if not isinstance(n,int) or n <= 0:
            raise ValueError("Maximum ranks per node must be a positive int")
        self.maxRanksPerNode = n

    def view(self):
        print('SciATH: Batch queueing system configuration [',self.confFileName,']')
        major,minor,patch=getVersion()
        print('  Version:           ',str(major)+'.'+str(minor)+'.'+str(patch))
        print('  Queue system:      ',self.queuingSystemType)
        print('  MPI launcher:      ',self.mpiLaunch)
        if self.useBatch:
            print('  Submit command:    ', self.jobSubmissionCommand)
            if self.accountName:
                print('  Account:           ',self.accountName)
            if self.queueName:
                print('  Queue:             ',self.queueName)
            if self.batchConstraint :
                print('  Constraint:        ', self.batchConstraint)
            if self.maxRanksPerNode :
                print('  Max Ranks Per Node:', self.maxRanksPerNode)

    def configure(self):
        print('----------------------------------------------------------------')
        print('Creating new configuration file ',self.confFileName)
        v = None
        while not v :
            prompt = '[1] Batch queuing system type <pbs,lsf,slurm,llq,none>: '
            v = py23input(prompt)
            if not v :
                print( 'Required.')
            else :
                try :
                    self.setQueueSystemType(v)
                except RuntimeError as e :
                    print(e)
                    v = None

        v = None
        while not v:
            prompt = '[2] MPI launch command with num. procs. flag (required - hit enter for examples): '
            v = py23input(prompt)
            if not v :
                print(' Required. Some example MPI launch commands:')
                print('  No MPI Required           : none')
                print('  Local Machine (mpirun)    : mpirun -np <ranks>')
                print('  Local Machine (mpiexec)   : mpiexec -np <ranks>')
                print('  SLURM w/ aprun            : aprun -B')
                print('  Native SLURM              : srun -n $SLURM_NTASKS')
                print('  LSF (Euler)               : mpirun')
                PETSC_DIR=os.getenv('PETSC_DIR')
                PETSC_ARCH=os.getenv('PETSC_ARCH')
                if PETSC_DIR and PETSC_ARCH:
                    print('  Current PETSc MPI wrapper :',os.path.join(PETSC_DIR,PETSC_ARCH,'bin','mpiexec'),'-n <ranks>')
                else :
                    print('  Example PETSc MPI wrapper : /users/myname/petsc/arch-xxx/bin/mpiexec -n <ranks>')
                print(' Note that the string \"<ranks>\" must be included if the number of ranks is required at launch.')
                print(' The keyword <ranks> will be replaced by the actual number of MPI ranks (defined by a given test) when the test is launched.')
        self.setMPILaunch(v)

        if self.useBatch == True:
            prompt = '[3] specify a constraint (e.g. "gpu" on Piz Daint) (optional - hit enter if not applicable):'
            v = py23input(prompt)
            self.setBatchConstraint(v)

            prompt = '[4] Account to charge (optional - hit enter if not applicable): '
            v = py23input(prompt)
            self.setHPCAccountName(v)

            prompt = '[5] Name of queue to submit tests to (optional - hit enter if not applicable): '
            v = py23input(prompt)
            self.setQueueName(v)

            prompt = '[6] Maximum number of MPI ranks per compute node (optional - hit enter to skip): '
            done = False
            while not done:
                v = py23input(prompt)
                if len(v) == 0:
                    done = True
                else:
                    try:
                        self.setMaxRanksPerNode(int(v))
                        done = True
                    except ValueError:
                        print('Enter a positive integer (or nothing, to skip)')

        self.writeDefinition()
        print('\n')
        print('** If you wish to change the config for your batch system, either')
        print('**  (i) delete the file',self.confFileName,' or')
        print('** (ii) re-run with the command line arg --configure')
        print('----------------------------------------------------------------')

    def setup(self):
        try:
            self.loadDefinition()
        except SciATHLoadException :
            self.configure()
            self.writeDefinition()

    def writeDefinition(self):
        file = open(self.confFileName,'w')
        major,minor,patch=getVersion()
        file.write('majorVersion=' + str(major) + '\n')
        file.write('minorVersion=' + str(minor) + '\n')
        file.write('patchVersion=' + str(patch) + '\n')
        file.write('queuingSystemType=' + self.queuingSystemType + '\n')
        file.write('mpiLaunch=' + self.mpiLaunch + '\n')
        if self.useBatch == True:
            file.write('accountName=' + self.accountName + '\n')
            file.write('batchConstraint=' + self.batchConstraint + '\n')
            file.write('queueName=' + self.queueName + '\n')
            if self.maxRanksPerNode:
                file.write('maxRanksPerNode=' + str(self.maxRanksPerNode) + '\n')
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
                if self.useBatch == True:
                    if key == 'batchConstraint' :
                        self.setBatchConstraint(value)
                    if key == 'queueName' :
                        self.setQueueName(value)
                    if key == 'accountName' :
                        self.setHPCAccountName(value)
                    if key == 'maxRanksPerNode' :
                        self.setMaxRanksPerNode(int(value))
            file.close()
        except:
            raise SciATHLoadException('[SciATH] You must execute configure(), and or writeDefinition() first')

        # Do not accept conf files if the major.minor version is stale, or if versions are missing
        major,minor,patch = getVersion()
        if majorFile < major or (minorFile < minor and majorFile == major) or \
             majorFile==None or minorFile==None or patchFile==None :
            message = '[SciATH] Incompatible, outdated configuration file ' + self.confFileName + ' detected. Please delete it and re-run to reconfigure.'
            raise RuntimeError(message)


    def __createJobSubmissionFile(self,job,walltime,output_path):
      
        # Verify input, check for generic errors
        if self.batchConstraint and self.queuingSystemType != 'slurm' :
            message = '[SciATH] Constraints are only currently supported with SLURM'
            raise RuntimeError(message)

        idle_ranks_per_node = job.resources["idlempirankspernode"]
        if idle_ranks_per_node != 0:
            message = '[SciATH] Job requests with a reduced number of ranks-per-node is currently not supported'
            raise RuntimeError(message)

        if self.queuingSystemType == 'pbs':
            filename = _generateLaunch_PBS(self,walltime,output_path,job)
        elif self.queuingSystemType == 'lsf':
            filename = _generateLaunch_LSF(self,None,walltime,output_path,job)
        elif self.queuingSystemType == 'slurm':
            filename = _generateLaunch_SLURM(self,walltime,output_path,job)

        print('Created submission file:',filename)
        return filename

    def submitJob(self,job,**kwargs):
        """ Run a job

        Supply output_path to change the location where SciATH's output
        files will be saved.

        Supply exec_path to change the directory from which the command
        will be executed.
        """
      
        output_path = os.getcwd()
        exec_path = os.getcwd()
        for key, value in kwargs.items():
            if key == 'output_path':
                output_path = value
                if not os.path.isabs(output_path):
                    raise ValueError('[SciATH] Unsupported: output paths must be absolute')
            if key == 'exec_path':
                exec_path = value
                if not os.path.isabs(exec_path):
                    raise ValueError('[SciATH] Unsupported: output paths must be absolute')

        if job.name == None:
            raise ValueError('[SciATH] Unsupported: Job cannot be submitted without it having a name')
        
        setBlockingIOStdout()

        if not self.useBatch:
            mpiLaunch = self.mpiLaunch
            # This supports DAG jobs
            resources = job.getMaxResources()
            ranks = resources["mpiranks"]
            threads = resources["threads"]
            if threads != 1:
                raise ValueError('[SciATH] Unsupported: Job cannot be submitted multi-threaded')

            if self.mpiLaunch == 'none' and ranks != 1:
                print('[Failed to launch test \"' + job.name + '\" as test uses > 1 MPI ranks and no MPI launcher was provided]')
                return
            
            command_resource = job.createExecuteCommand()
            launchCmd = []
            for j in command_resource:
                launch = []
                if self.mpiLaunch != 'none':
                    j_ranks = j[1]["mpiranks"]
                    launch += formatMPILaunchCommand(mpiLaunch,j_ranks,None)
                
                if isinstance(j[0], list):
                    for c in j[0]:
                        launch.append(c)
                else:
                    launch.append(j[0])
                
                launchCmd.append(launch)
                  
            if self.verbosity_level > 0:
                lc_len = len(launchCmd)
                lc_count = 0
                for lc in launchCmd:
                    lc_count = lc_count + 1
                    launch_text = sciath_colors.SUBHEADER + '[Executing ' + job.name
                    if lc_len > 1 :
                        launch_text = launch_text + ' (' + str(lc_count) + '/' + str(lc_len) + ')'
                    launch_text = launch_text + ']' + sciath_colors.ENDC
                    launch_text = launch_text + ' from ' + os.getcwd()
                    print(launch_text)
                    print('  [cmd] ',lc)
        
            c_name,o_name,e_name = _getLaunchStandardOutputFileNames(job)

            file_ecode = open( os.path.join(output_path,c_name) ,'w')
            lc_count = len(launchCmd)
            for i in range(0,lc_count):
                file_e = open( os.path.join(output_path,e_name[i]), 'w')
                file_o = open( os.path.join(output_path,o_name[i]), 'w')
                cwd_back = os.getcwd()
                os.chdir(exec_path)
                ctx = subprocess.run( launchCmd[i], universal_newlines=True, stdout=file_o, stderr=file_e)
                os.chdir(cwd_back)
                file_o.close()
                file_e.close()
                file_ecode.write(str(ctx.returncode)+"\n") # exit code
                setBlockingIOStdout()
            file_ecode.close()

        else:
            walltime = 0.0
            walltime = job.getMaxWallTime()

            launchfile = self.__createJobSubmissionFile(job,walltime,output_path)
            launchCmd = [self.jobSubmissionCommand,launchfile]
            cwd_back = os.getcwd()
            os.chdir(exec_path)
            if self.verbosity_level > 0:
                print(sciath_colors.SUBHEADER + '[Executing ' + job.name + ']' + sciath_colors.ENDC + ' from ' + os.getcwd())
                print('  [cmd] ',launchCmd)
            subprocess.run(launchCmd, universal_newlines=True)
            os.chdir(cwd_back)
            setBlockingIOStdout()

    def clean(self,job,**kwargs):
     
        output_path = None
        for key, value in kwargs.items():
            if key == 'output_path':
                output_path = value

        if not output_path:
            raise ValueError('[SciATH] cannot clean without an explicit output_path')
        if not os.path.isabs(output_path):
            raise ValueError('[SciATH] cannot clean without an absolute output_path')
      
        try:
            job.clean()
        except:
            pass

        c_name,o_name,e_name = _getLaunchStandardOutputFileNames(job)
        _remove_file( os.path.join(output_path,c_name) )
        for f in o_name:
            _remove_file( os.path.join(output_path,f) )
        for f in e_name:
            _remove_file( os.path.join(output_path,f) )
        
        if self.queueFileExt is not None:
            filename = "sciath.job-" + job.name + "-launch." + self.queueFileExt
            _remove_file( os.path.join(output_path,filename) )

        return
        
