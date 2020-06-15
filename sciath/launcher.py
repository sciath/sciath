from __future__ import print_function

import os
import sys
import shutil
import fcntl
import subprocess

import sciath._yaml_parse
from   sciath import sciath_colors
from   sciath import getVersion
from   sciath._sciath_io import py23input, _remove_file_if_it_exists, command_join

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

def formatMPILaunchCommand(mpiLaunch,ranks):
    launch = mpiLaunch
    launch = launch.replace("<ranks>",str(ranks))
    launch = launch.replace("<cores>",str(ranks))
    launch = launch.replace("<tasks>",str(ranks))
    launch = launch.replace("<RANKS>",str(ranks))
    return launch.split()


def _generateLaunch_PBS(launcher,walltime,output_path,job):

    if walltime is None:
        message = "[SciATH] _generateLaunch_PBS requires walltime be specified"
        raise RuntimeError(message)

    accountname = launcher.accountName
    queuename = launcher.queueName
    mpiLaunch = launcher.mpiLaunch

    resources = job.getMaxResources()
    ranks = resources["mpiranks"]

    c_name,o_name,e_name = job.get_output_filenames()

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

    _remove_file_if_it_exists( os.path.join(output_path,c_name) )

    command_resource = job.createExecuteCommand()
    njobs = len(command_resource)
    for i in range(0,njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += formatMPILaunchCommand(mpiLaunch,j_ranks)
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

    c_name,o_name,e_name = job.get_output_filenames()

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

    _remove_file_if_it_exists( os.path.join(output_path,c_name) )

    command_resource = job.createExecuteCommand()
    njobs = len(command_resource)
    for i in range(0,njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += formatMPILaunchCommand(mpiLaunch,j_ranks)
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

    c_name,o_name,e_name = job.get_output_filenames()

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

    if constraint :
        file.write("#SBATCH --constraint=" + constraint + "\n")

    wt = FormattedHourMinSec(float(walltime)*60.0)
    file.write("#SBATCH --time=" + wt + "\n")


    # Write out the list of jobs execute commands
    # Dependent jobs have their stdout collected in separate files (one per job)
    # The stdout/stderr for the parent job is collected via the queue system

    _remove_file_if_it_exists( os.path.join(output_path,c_name) )

    command_resource = job.createExecuteCommand()
    njobs = len(command_resource)
    for i in range(0,njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += formatMPILaunchCommand(mpiLaunch,j_ranks)
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


def _subprocess_run(command, **kwargs):
    """ Wrapper for subprocess.run, to allow usage from Python 2

        It returns the error code.

        This is to avoid a dependency like subprocess32.
    """
    if sys.version_info[0] >= 3:
        ctx = subprocess.run(command, **kwargs)  #pylint: disable=no-member
        returncode =  ctx.returncode
    else:
        for key in ['stdout', 'stderr']:
            if key in kwargs and kwargs[key] == 'PIPE':
                raise Exception('The current implementation cannot handle pipes. See the subprocess documentation for an alternative')
        returncode =  subprocess.call(command, **kwargs)
    return returncode


class Launcher:
    """ :class:`Launcher` is responsible for executing :class:`Task`s specified by a :class:`Job`,
    depending on its system-dependent configuration.

    Thus, it is:

    * The exclusive location for system-specific information
    * The exclusive reader of system-specific configuration file

    :class:`Launcher` include methods to operate on a combination of a :class:`Job` and a path:

    * Run the job from that path. If not on a batch system, blocks until the job completes.
    * Check the status of the job as run from that path
    * Clean up after a job, calling the clean method from the :class:`Job` and removing configuration-specific generated files

    :class:`Launcher` does not know about :class:`Test` or :class:`Harness`, and it should be possible
    to use :class:`Launcher` and a collection of :class:`Job` objects as a convenience to execute
    sets of tasks on various systems.

    A :class:`Launcher`'s state corresponds only to its configuration,
    not the status of any particular "run" of a :class:`Job`.
    """
    _default_conf_filename = 'SciATHBatchQueuingSystem.conf'

    @staticmethod
    def writeDefaultDefinition(conf_filename_in=None):
        major, minor, patch=getVersion()
        conf_filename = conf_filename_in if conf_filename_in else Launcher._default_conf_filename
        with open(conf_filename, 'w') as conf_file:
            conf_file.write('majorVersion: %s\n' % major)
            conf_file.write('minorVersion: %s\n' % minor)
            conf_file.write('patchVersion: %s\n' % patch)
            conf_file.write('queuingSystemType: none\n' )
            conf_file.write('mpiLaunch: none\n' )

    def __init__(self,conf_filename=None):
        self.accountName = []
        self.queueName = []
        self.mpiLaunch = []
        self.queuingSystemType = []
        self.maxRanksPerNode = None
        self.batchConstraint = []
        self.jobSubmissionCommand = []
        self.useBatch = False
        self.verbosity_level = 1
        if conf_filename :
            self.conf_filename = conf_filename
        else :
            self.conf_filename = Launcher._default_conf_filename

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

            if not valid_launcher:
                raise RuntimeError('[SciATH] Your MPI launch command must contain the keyword \"<ranks>\"')

    def setQueueSystemType(self,system_type):
        if system_type in ['PBS','pbs']:
            self.queuingSystemType = 'pbs'
            self.jobSubmissionCommand = ['qsub']
            self.useBatch = True
            self.queueFileExt = 'pbs'

        elif system_type in ['LSF','lsf']:
            self.queuingSystemType = 'lsf'
            self.jobSubmissionCommand = ['sh','-c','bsub < $0'] # This allows "<".
            self.useBatch = True
            self.queueFileExt = 'lsf'

        elif system_type in ['SLURM','slurm']:
            self.queuingSystemType = 'slurm'
            self.jobSubmissionCommand = ['sbatch']
            self.useBatch = True
            self.queueFileExt = 'slurm'

        elif system_type in ['LoadLeveler','load_leveler','loadleveler','llq']:
            self.queuingSystemType = 'load_leveler'
            self.jobSubmissionCommand = ['llsubmit']
            self.useBatch = True
            self.queueFileExt = 'llq'
            raise ValueError('[SciATH] Unsupported: LoadLeveler needs to be updated')

        elif system_type in ['none', 'None', 'local']:
            self.queuingSystemType = 'none'
            self.jobSubmissionCommand = ''
            self.queueFileExt = None

        else:
            raise RuntimeError('[SciATH] Unknown or unsupported batch queuing system "' + system_type + '" specified')

    def setMaxRanksPerNode(self,n):
        """ Store an int-valued maximum number of MPI ranks per node """
        if not isinstance(n,int) or n <= 0:
            raise ValueError("Maximum ranks per node must be a positive int")
        self.maxRanksPerNode = n

    def view(self):
        if self.verbosity_level > 0:
            print('[SciATH] Batch queueing system configuration [%s]' % self.conf_filename)
            print('  Version:           %d.%d.%d' % getVersion())
            print('  Queue system:      %s' % self.queuingSystemType)
            print('  MPI launcher:      %s' % self.mpiLaunch)
            if self.useBatch:
                print('  Submit command:    %s' % command_join(self.jobSubmissionCommand))
                if self.accountName:
                    print('  Account:           %s' % self.accountName)
                if self.queueName:
                    print('  Queue:             %s' % self.queueName)
                if self.batchConstraint :
                    print('  Constraint:        %s' % self.batchConstraint)
                if self.maxRanksPerNode :
                    print('  Max Ranks Per Node:%s' % self.maxRanksPerNode)

    def configure(self):
        print('----------------------------------------------------------------')
        print('Creating new configuration file ',self.conf_filename)
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

        if self.useBatch :
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
        print('**  (i) delete the file',self.conf_filename,' or')
        print('** (ii) re-run with the command line arg --configure')
        print('----------------------------------------------------------------')

    def setup(self):
        try:
            self.loadDefinition()
        except SciATHLoadException :
            self.configure()
            self.writeDefinition()

    def writeDefinition(self):
        major, minor, patch=getVersion()
        with open(self.conf_filename, 'w') as conf_file:
            conf_file.write('majorVersion: %s\n' % major)
            conf_file.write('minorVersion: %s\n' % minor)
            conf_file.write('patchVersion: %s\n' % patch)
            conf_file.write('queuingSystemType: %s\n' % self.queuingSystemType)
            conf_file.write('mpiLaunch: %s\n' % self.mpiLaunch)
            if self.useBatch :
                conf_file.write('accountName: %s\n' % self.accountName)
                conf_file.write('batchConstraint: %s\n' % self.batchConstraint)
                conf_file.write('queueName: %s\n' % self.queueName)
                if self.maxRanksPerNode:
                    conf_file.write('maxRanksPerNode: %s\n' % self.maxRanksPerNode)

    def loadDefinition(self):
        majorFile = None
        minorFile = None
        patchFile = None
        try:
            data = sciath._yaml_parse.parse_yaml_subset_from_file(self.conf_filename)
            if 'majorVersion' in data:
                majorFile = int(data['majorVersion'])
            if 'minorVersion' in data:
                minorFile = int(data['minorVersion'])
            if 'patchVersion' in data:
                patchFile = int(data['patchVersion'])
            if 'queuingSystemType' in data:
                self.setQueueSystemType(data['queuingSystemType'])
            if 'mpiLaunch' in data:
                self.setMPILaunch(data['mpiLaunch'])
            if self.useBatch :
                if 'batchConstraint' in data:
                    self.setBatchConstraint(data['batchConstraint'])
                if 'queueName' in data:
                    self.setQueueName(data['queueName'])
                if 'accountName' in data:
                    self.setHPCAccountName(data['accountName'])
                if 'maxRanksPerNode' in data:
                    self.setMaxRanksPerNode(int(data['maxRanksPerNode']))
        except:
            raise SciATHLoadException('[SciATH] Configuration file missing. You must execute configure(), and or writeDefinition() first')

        # Do not accept conf files if the major.minor version is stale, or if versions are missing
        major,minor,patch = getVersion()
        if majorFile < major or (minorFile < minor and majorFile == major) or \
             majorFile is None or minorFile is None or patchFile is None :
            message = '[SciATH] Incompatible, outdated configuration file ' + self.conf_filename + ' detected. Please delete it and re-run to reconfigure.'
            raise RuntimeError(message)


    def __createJobSubmissionFile(self,job,walltime,output_path):

        # Verify input, check for generic errors
        if self.batchConstraint and self.queuingSystemType != 'slurm' :
            message = '[SciATH] Constraints are only currently supported with SLURM'
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
                    raise ValueError('[SciATH] Unsupported: exec paths must be absolute')

        setBlockingIOStdout()

        if not self.useBatch:
            mpiLaunch = self.mpiLaunch
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
            for command, resource in command_resource:
                launch = []
                if self.mpiLaunch != 'none':
                    j_ranks = resource["mpiranks"]
                    launch += formatMPILaunchCommand(mpiLaunch,j_ranks)
                launch.extend(command)
                launchCmd.append(launch)

            if self.verbosity_level > 0:
                print('%s[Executing %s]%s from %s' % (sciath_colors.SUBHEADER, job.name, sciath_colors.ENDC, exec_path))
                for lc in launchCmd:
                    print(command_join(lc))

            c_name,o_name,e_name = job.get_output_filenames()

            file_ecode = open( os.path.join(output_path,c_name) ,'w')
            lc_count = len(launchCmd)
            for i in range(0,lc_count):
                file_e = open( os.path.join(output_path,e_name[i]), 'w')
                file_o = open( os.path.join(output_path,o_name[i]), 'w')
                cwd_back = os.getcwd()
                os.chdir(exec_path)
                returncode = _subprocess_run(launchCmd[i], universal_newlines=True, stdout=file_o, stderr=file_e)
                os.chdir(cwd_back)
                file_o.close()
                file_e.close()
                file_ecode.write(str(returncode)+"\n") # exit code
                setBlockingIOStdout()
            file_ecode.close()

        else:
            walltime = job.total_wall_time()

            launchfile = self.__createJobSubmissionFile(job,walltime,output_path)
            launchCmd = self.jobSubmissionCommand + [launchfile]
            cwd_back = os.getcwd()
            os.chdir(exec_path)
            if self.verbosity_level > 0:
                print('%s[Executing %s]%s from %s' % (sciath_colors.SUBHEADER, job.name, sciath_colors.ENDC, exec_path))
                print(command_join(launchCmd))
            _subprocess_run(launchCmd, universal_newlines=True)
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

        c_name,o_name,e_name = job.get_output_filenames()
        _remove_file_if_it_exists( os.path.join(output_path,c_name) )
        for f in o_name:
            _remove_file_if_it_exists( os.path.join(output_path,f) )
        for f in e_name:
            _remove_file_if_it_exists( os.path.join(output_path,f) )

        if self.queueFileExt is not None:
            filename = "sciath.job-" + job.name + "-launch." + self.queueFileExt
            _remove_file_if_it_exists( os.path.join(output_path,filename) )
