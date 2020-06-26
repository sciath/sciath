""" SciATH Launcher class """
from __future__ import print_function

import os
import sys
import fcntl
import subprocess

import sciath
from sciath import yaml_parse
from sciath import SCIATH_COLORS
from sciath._sciath_io import py23input, _remove_file_if_it_exists, command_join


# mpiexec has been observed to set non-blocking I/O, which
#  has been observed to cause problems on OS X with errors like
#  "BlockingIOError: [Errno 35] write could not complete without blocking"
# We use this function to (re)set blocking I/O when launching
def _set_blocking_io_stdout():
    descriptor = sys.stdout
    flags = fcntl.fcntl(descriptor, fcntl.F_GETFL)
    if flags & os.O_NONBLOCK:
        fcntl.fcntl(descriptor, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)


class SciATHLoadException(Exception):
    """ Exception for a failed load of configuration file """


def _formatted_hour_min(seconds):
    minutes = divmod(int(seconds), 60)[0]
    hours, minutes = divmod(minutes, 60)
    return "%02d:%02d" % (hours, minutes)


def _formatted_hour_min_sec(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


def _format_mpi_launch_command(mpi_launch, ranks):
    launch = mpi_launch
    launch = launch.replace("<ranks>", str(ranks))
    launch = launch.replace("<cores>", str(ranks))
    launch = launch.replace("<tasks>", str(ranks))
    launch = launch.replace("<RANKS>", str(ranks))
    return launch.split()


def _generate_launch_pbs(launcher, walltime, output_path, job):

    if walltime is None:
        message = "[SciATH] _generate_launch_pbs requires walltime be specified"
        raise RuntimeError(message)

    accountname = launcher.account_name
    queuename = launcher.queue_name
    mpi_launch = launcher.mpi_launch

    # resources = job.get_max_resources()
    # ranks = resources["mpiranks"]

    c_name, o_name, e_name = job.get_output_filenames()

    filename = os.path.join(
        output_path,
        "sciath.job-" + job.name + "-launch." + launcher.queue_file_extension)
    file = open(filename, "w")

    # PBS specifics
    file.write("#!/bin/bash\n")
    file.write("# SciATH: auto-generated pbs file\n")

    if accountname:
        file.write("#PBS -A " + accountname + "\n")  # account to charge

    file.write("#PBS -N \"" + "sciath.job-" + job.name + "\"" + "\n")  # jobname
    file.write("#PBS -o " + os.path.join(output_path, o_name[-1]) + "\n")
    file.write("#PBS -e " + os.path.join(output_path, e_name[-1]) + "\n")

    if queuename:
        file.write("#PBS -q " + queuename + "\n")

    walltime_string = _formatted_hour_min_sec(float(walltime) * 60.0)
    file.write("#PBS -l mppwidth=1024,walltime=" + walltime_string + "\n")

    # Write out the list of jobs execute commands
    # Dependent jobs have their stdout collected in separate files (one per job)
    # The stdout/stderr for the parent job is collected via the queue system

    _remove_file_if_it_exists(os.path.join(output_path, c_name))

    command_resource = job.create_execute_command()
    njobs = len(command_resource)
    for i in range(0, njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += _format_mpi_launch_command(mpi_launch, j_ranks)
        if isinstance(j[0], list):
            launch.extend(j[0])
        else:
            launch.append(j[0])

        if i < njobs - 1:
            file.write(" ".join(launch) + " > " +
                       os.path.join(output_path, o_name[i]) +
                       "\n")  # launch command
            file.write("echo $? >> " + os.path.join(output_path, c_name) + "\n")
    # Command for the parent job
    file.write(" ".join(launch) + "\n")  # launch command
    file.write("echo $? >> " + os.path.join(output_path, c_name) + "\n")
    file.write("\n")

    file.close()
    return filename


def _generate_launch_lsf(launcher, rusage, walltime, output_path, job):

    if walltime is None:
        message = "[SciATH] _generate_launch_lsf requires walltime be specified"
        raise RuntimeError(message)

    accountname = launcher.account_name
    queuename = launcher.queue_name
    mpi_launch = launcher.mpi_launch

    resources = job.get_max_resources()
    ranks = resources["mpiranks"]

    c_name, o_name, e_name = job.get_output_filenames()

    filename = os.path.join(
        output_path,
        "sciath.job-" + job.name + "-launch." + launcher.queue_file_extension)
    file = open(filename, "w")

    # LSF specifics
    file.write("#!/bin/sh\n")
    file.write("# SciATH: auto-generated lsf file\n")

    if accountname:
        file.write("#BSUB -G " + accountname + "\n")

    file.write("#BSUB -J " + "sciath.job-" + job.name + "\n")  # jobname
    file.write("#BSUB -o " + os.path.join(output_path, o_name[-1]) +
               "\n")  # jobname.stdout
    file.write("#BSUB -e " + os.path.join(output_path, e_name[-1]) +
               "\n")  # jobname.stderr

    if queuename:
        file.write("#BSUB -q " + queuename + "\n")

    file.write("#BSUB -n " + str(ranks) + "\n")

    if rusage:
        file.write("#BSUB -R \'" + rusage + "\'" + "\n")

    walltime_string = _formatted_hour_min(float(walltime) * 60.0)
    file.write("#BSUB -W " + walltime_string + "\n")

    # Write out the list of jobs execute commands
    # Dependent jobs have their stdout collected in separate files (one per job)
    # The stdout/stderr for the parent job is collected via the queue system

    _remove_file_if_it_exists(os.path.join(output_path, c_name))

    command_resource = job.create_execute_command()
    njobs = len(command_resource)
    for i in range(0, njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += _format_mpi_launch_command(mpi_launch, j_ranks)
        if isinstance(j[0], list):
            launch.extend(j[0])
        else:
            launch.append(j[0])

        if i < njobs - 1:
            file.write(" ".join(launch) + " > " +
                       os.path.join(output_path, o_name[i]) +
                       "\n")  # launch command
            file.write("echo $? >> " + os.path.join(output_path, c_name) + "\n")
    # Command for the parent job
    file.write(" ".join(launch) + "\n")  # launch command
    file.write("echo $? >> " + os.path.join(output_path, c_name) + "\n")
    file.write("\n")

    file.close()
    return filename


def _generate_launch_slurm(launcher, walltime, output_path, job):

    if walltime is None:
        message = "[SciATH] _generate_launch_slurm requires walltime be specified"
        raise RuntimeError(message)

    accountname = launcher.account_name
    queuename = launcher.queue_name
    constraint = launcher.batch_constraint
    mpi_launch = launcher.mpi_launch

    resources = job.get_max_resources()
    ranks = resources["mpiranks"]

    c_name, o_name, e_name = job.get_output_filenames()

    filename = os.path.join(
        output_path,
        "sciath.job-" + job.name + "-launch." + launcher.queue_file_extension)
    file = open(filename, "w")

    # SLURM specifics
    file.write("#!/bin/bash -l\n")
    file.write("# SciATH: auto-generated slurm file\n")

    if accountname:
        file.write("#SBATCH --account=" + accountname +
                   "\n")  # account to charge

    file.write("#SBATCH --job-name=\"" + "sciath.job-" + job.name + "\"" +
               "\n")  # jobname
    file.write("#SBATCH --output=" + os.path.join(output_path, o_name[-1]) +
               "\n")  # jobname.stdout
    file.write("#SBATCH --error=" + os.path.join(output_path, e_name[-1]) +
               "\n")  # jobname.stderr

    if queuename:
        file.write("#SBATCH --partition=" + queuename + "\n")

    file.write("#SBATCH --ntasks=" + str(ranks) + "\n")

    if constraint:
        file.write("#SBATCH --constraint=" + constraint + "\n")

    walltime_string = _formatted_hour_min_sec(float(walltime) * 60.0)
    file.write("#SBATCH --time=" + walltime_string + "\n")

    # Write out the list of jobs execute commands
    # Dependent jobs have their stdout collected in separate files (one per job)
    # The stdout/stderr for the parent job is collected via the queue system

    _remove_file_if_it_exists(os.path.join(output_path, c_name))

    command_resource = job.create_execute_command()
    njobs = len(command_resource)
    for i in range(0, njobs):
        j = command_resource[i]
        j_ranks = j[1]["mpiranks"]
        launch = []
        launch += _format_mpi_launch_command(mpi_launch, j_ranks)
        if isinstance(j[0], list):
            launch.extend(j[0])
        else:
            launch.append(j[0])

        if i < njobs - 1:
            file.write(" ".join(launch) + " > " +
                       os.path.join(output_path, o_name[i]) +
                       "\n")  # launch command
            file.write("echo $? >> " + os.path.join(output_path, c_name) + "\n")
    # Command for the parent job
    file.write(" ".join(launch) + "\n")  # launch command
    file.write("echo $? >> " + os.path.join(output_path, c_name) + "\n")
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
        returncode = ctx.returncode
    else:
        for key in ['stdout', 'stderr']:
            if key in kwargs and kwargs[key] == 'PIPE':
                raise Exception(
                    'The current implementation cannot handle pipes. See the subprocess documentation for an alternative'
                )
        returncode = subprocess.call(command, **kwargs)
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
    def write_default_definition(conf_filename_in=None):
        """ Writes a default configuration file """
        major, minor, patch = sciath.version()
        conf_filename = conf_filename_in if conf_filename_in else Launcher._default_conf_filename
        with open(conf_filename, 'w') as conf_file:
            conf_file.write('majorVersion: %s\n' % major)
            conf_file.write('minorVersion: %s\n' % minor)
            conf_file.write('patchVersion: %s\n' % patch)
            conf_file.write('queuingSystemType: none\n')
            conf_file.write('mpiLaunch: none\n')

    def __init__(self, conf_filename=None):
        self.account_name = []
        self.queue_name = []
        self.mpi_launch = []
        self.queuing_system_type = []
        self.max_ranks_per_node = None
        self.batch_constraint = []
        self.job_submission_command = []
        self.use_batch = False
        self.verbosity_level = 1
        if conf_filename:
            self.conf_filename = conf_filename
        else:
            self.conf_filename = Launcher._default_conf_filename
        self.queue_file_extension = None

        self.setup()

        if self.use_batch:
            if self.mpi_launch == 'none':
                raise RuntimeError(
                    '[SciATH] If using a queuing system, a valid mpi launch command must be provided'
                )

    def set_queue_name(self, name):
        self.queue_name = name

    def set_batch_constraint(self, argstring):
        self.batch_constraint = argstring

    def set_hpc_account_name(self, name):
        self.account_name = name

    def set_mpi_launch(self, name):
        self.mpi_launch = name
        # check for existence of "rank" keyword in the string "name"
        if self.queuing_system_type in ['none', 'None', 'local'] and name != 'none':
            keywordlist = ['<ranks>', '<cores>', '<tasks>', '<RANKS>']
            # check of any of keywordlist[i] appears in name
            valid_launcher = False
            for kword in keywordlist:
                if kword in name:
                    valid_launcher = True
                    break

            if not valid_launcher:
                raise RuntimeError(
                    '[SciATH] Your MPI launch command must contain the keyword \"<ranks>\"'
                )

    def set_queue_system_type(self, system_type):
        if system_type in ['PBS', 'pbs']:
            self.queuing_system_type = 'pbs'
            self.job_submission_command = ['qsub']
            self.use_batch = True
            self.queue_file_extension = 'pbs'

        elif system_type in ['LSF', 'lsf']:
            self.queuing_system_type = 'lsf'
            self.job_submission_command = ['sh', '-c', 'bsub < $0']  # This allows "<".
            self.use_batch = True
            self.queue_file_extension = 'lsf'

        elif system_type in ['SLURM', 'slurm']:
            self.queuing_system_type = 'slurm'
            self.job_submission_command = ['sbatch']
            self.use_batch = True
            self.queue_file_extension = 'slurm'

        elif system_type in ['LoadLeveler', 'load_leveler', 'loadleveler', 'llq']:
            self.queuing_system_type = 'load_leveler'
            self.job_submission_command = ['llsubmit']
            self.use_batch = True
            self.queue_file_extension = 'llq'
            raise ValueError(
                '[SciATH] Unsupported: LoadLeveler needs to be updated')

        elif system_type in ['none', 'None', 'local']:
            self.queuing_system_type = 'none'
            self.job_submission_command = ''
            self.queue_file_extension = None

        else:
            raise RuntimeError(
                '[SciATH] Unknown or unsupported batch queuing system "' +
                system_type + '" specified')

    def set_max_ranks_per_node(self, max_ranks_per_node):
        """ Store an int-valued maximum number of MPI ranks per node """
        if not isinstance(max_ranks_per_node, int) or max_ranks_per_node <= 0:
            raise ValueError("Maximum ranks per node must be a positive integer")
        self.max_ranks_per_node = max_ranks_per_node

    def view(self):
        if self.verbosity_level > 0:
            print('[SciATH] Batch queueing system configuration [%s]' %
                  self.conf_filename)
            print('  Version:           %d.%d.%d' % sciath.version())
            print('  Queue system:      %s' % self.queuing_system_type)
            print('  MPI launcher:      %s' % self.mpi_launch)
            if self.use_batch:
                print('  Submit command:    %s' %
                      command_join(self.job_submission_command))
                if self.account_name:
                    print('  Account:           %s' % self.account_name)
                if self.queue_name:
                    print('  Queue:             %s' % self.queue_name)
                if self.batch_constraint:
                    print('  Constraint:        %s' % self.batch_constraint)
                if self.max_ranks_per_node:
                    print('  Max Ranks Per Node:%s' % self.max_ranks_per_node)

    def configure(self):
        print('----------------------------------------------------------------')
        print('Creating new configuration file ', self.conf_filename)
        user_input = None
        while not user_input:
            prompt = '[1] Batch queuing system type <pbs,lsf,slurm,llq,none>: '
            user_input = py23input(prompt)
            if not user_input:
                print('Required.')
            else:
                try:
                    self.set_queue_system_type(user_input)
                except RuntimeError as exception:
                    print(exception)
                    user_input = None

        user_input = None
        while not user_input:
            prompt = '[2] MPI launch command with num. procs. flag (required - hit enter for examples): '
            user_input = py23input(prompt)
            if not user_input:
                print(' Required. Some example MPI launch commands:')
                print('  No MPI Required           : none')
                print('  Local Machine (mpirun)    : mpirun -np <ranks>')
                print('  Local Machine (mpiexec)   : mpiexec -np <ranks>')
                print('  SLURM w/ aprun            : aprun -B')
                print('  Native SLURM              : srun -n $SLURM_NTASKS')
                print('  LSF (Euler)               : mpirun')
                petsc_dir = os.getenv('PETSC_DIR')
                petsc_arch = os.getenv('PETSC_ARCH')
                if petsc_dir and petsc_arch:
                    print('  Current PETSc MPI wrapper :',
                          os.path.join(petsc_dir, petsc_arch, 'bin', 'mpiexec'),
                          '-n <ranks>')
                else:
                    print(
                        '  Example PETSc MPI wrapper : /users/myname/petsc/arch-xxx/bin/mpiexec -n <ranks>'
                    )
                print(
                    ' Note that the string \"<ranks>\" must be included if the number of ranks is required at launch.'
                )
                print(
                    ' The keyword <ranks> will be replaced by the actual number of MPI ranks (defined by a given test) when the test is launched.'
                )
        self.set_mpi_launch(user_input)

        if self.use_batch:
            prompt = '[3] specify a constraint (e.g. "gpu" on Piz Daint) (optional - hit enter if not applicable):'
            self.set_batch_constraint(py23input(prompt))

            prompt = '[4] Account to charge (optional - hit enter if not applicable): '
            self.set_hpc_account_name(py23input(prompt))

            prompt = '[5] Name of queue to submit tests to (optional - hit enter if not applicable): '
            self.set_queue_name(py23input(prompt))

            prompt = '[6] Maximum number of MPI ranks per compute node (optional - hit enter to skip): '
            done = False
            while not done:
                user_input = py23input(prompt)
                if len(user_input) == 0:
                    done = True
                else:
                    try:
                        self.set_max_ranks_per_node(int(user_input))
                        done = True
                    except ValueError:
                        print('Enter a positive integer (or nothing, to skip)')

        self._write_definition()
        print('\n')
        print('** If you wish to change the config for your batch system, either')
        print('**  (i) delete the file', self.conf_filename, ' or')
        print('** (ii) re-run with the command line arg --configure')
        print('----------------------------------------------------------------')

    def setup(self):
        try:
            self._load_definition()
        except SciATHLoadException:
            self.configure()
            self._write_definition()

    def _write_definition(self):
        major, minor, patch = sciath.version()
        with open(self.conf_filename, 'w') as conf_file:
            conf_file.write('majorVersion: %s\n' % major)
            conf_file.write('minorVersion: %s\n' % minor)
            conf_file.write('patchVersion: %s\n' % patch)
            conf_file.write('queuing_system_type: %s\n' % self.queuing_system_type)
            conf_file.write('mpiLaunch: %s\n' % self.mpi_launch)
            if self.use_batch:
                conf_file.write('accountName: %s\n' % self.account_name)
                conf_file.write('batchConstraint: %s\n' % self.batch_constraint)
                conf_file.write('queueName: %s\n' % self.queue_name)
                if self.max_ranks_per_node:
                    conf_file.write('maxRanksPerNode: %s\n' %
                                    self.max_ranks_per_node)

    def _load_definition(self):
        major_file = None
        minor_file = None
        patch_file = None
        try:
            data = yaml_parse.parse_yaml_subset_from_file(self.conf_filename)
            if 'majorVersion' in data:
                major_file = int(data['majorVersion'])
            if 'minorVersion' in data:
                minor_file = int(data['minorVersion'])
            if 'patchVersion' in data:
                patch_file = int(data['patchVersion'])
            if 'queuingSystemType' in data:
                self.set_queue_system_type(data['queuingSystemType'])
            if 'mpiLaunch' in data:
                self.set_mpi_launch(data['mpiLaunch'])
            if self.use_batch:
                if 'batchConstraint' in data:
                    self.set_batch_constraint(data['batchConstraint'])
                if 'queueName' in data:
                    self.set_queue_name(data['queueName'])
                if 'accountName' in data:
                    self.set_hpc_account_name(data['accountName'])
                if 'maxRanksPerNode' in data:
                    self.set_max_ranks_per_node(int(data['maxRanksPerNode']))
        except:
            raise SciATHLoadException(
                '[SciATH] Configuration file missing. You must execute configure(), and or _write_definition() first'
            )

        # Do not accept conf files if the major.minor version is stale, or if versions are missing
        major, minor, patch = sciath.version()
        if major_file < major or (minor_file < minor and major_file == major) or \
             major_file is None or minor_file is None or patch_file is None:
            message = '[SciATH] Incompatible, outdated configuration file ' + self.conf_filename + ' detected. Please delete it and re-run to reconfigure.'
            raise RuntimeError(message)

    def _create_job_submission_file(self, job, walltime, output_path):

        # Verify input, check for generic errors
        if self.batch_constraint and self.queuing_system_type != 'slurm':
            message = '[SciATH] Constraints are only currently supported with SLURM'
            raise RuntimeError(message)

        if self.queuing_system_type == 'pbs':
            filename = _generate_launch_pbs(self, walltime, output_path, job)
        elif self.queuing_system_type == 'lsf':
            filename = _generate_launch_lsf(self, None, walltime, output_path, job)
        elif self.queuing_system_type == 'slurm':
            filename = _generate_launch_slurm(self, walltime, output_path, job)

        print('Created submission file:', filename)
        return filename

    def submit_job(self, job, **kwargs):
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
                    raise ValueError(
                        '[SciATH] Unsupported: output paths must be absolute')
            if key == 'exec_path':
                exec_path = value
                if not os.path.isabs(exec_path):
                    raise ValueError(
                        '[SciATH] Unsupported: exec paths must be absolute')

        _set_blocking_io_stdout()

        if not self.use_batch:
            mpi_launch = self.mpi_launch
            resources = job.get_max_resources()
            ranks = resources["mpiranks"]
            threads = resources["threads"]
            if threads != 1:
                raise ValueError(
                    '[SciATH] Unsupported: Job cannot be submitted multi-threaded'
                )

            if self.mpi_launch == 'none' and ranks != 1:
                print(
                    '[Failed to launch test \"' + job.name +
                    '\" as test uses > 1 MPI ranks and no MPI launcher was provided]'
                )
                return

            command_resource = job.create_execute_command()
            launch_command = []
            for command, resource in command_resource:
                launch = []
                if self.mpi_launch != 'none':
                    j_ranks = resource["mpiranks"]
                    launch += _format_mpi_launch_command(mpi_launch, j_ranks)
                launch.extend(command)
                launch_command.append(launch)

            if self.verbosity_level > 0:
                print('%s[Executing %s]%s from %s' %
                      (SCIATH_COLORS.SUBHEADER, job.name, SCIATH_COLORS.ENDC,
                       exec_path))
                for term in launch_command:
                    print(command_join(term))

            c_name, o_name, e_name = job.get_output_filenames()

            file_ecode = open(os.path.join(output_path, c_name), 'w')
            lc_count = len(launch_command)
            for i in range(0, lc_count):
                file_e = open(os.path.join(output_path, e_name[i]), 'w')
                file_o = open(os.path.join(output_path, o_name[i]), 'w')
                cwd_back = os.getcwd()
                os.chdir(exec_path)
                returncode = _subprocess_run(launch_command[i],
                                             universal_newlines=True,
                                             stdout=file_o,
                                             stderr=file_e)
                os.chdir(cwd_back)
                file_o.close()
                file_e.close()
                file_ecode.write(str(returncode) + "\n")  # exit code
                _set_blocking_io_stdout()
            file_ecode.close()

        else:
            walltime = job.total_wall_time()

            launchfile = self._create_job_submission_file(job, walltime, output_path)
            launch_command = self.job_submission_command + [launchfile]
            cwd_back = os.getcwd()
            os.chdir(exec_path)
            if self.verbosity_level > 0:
                print('%s[Executing %s]%s from %s' %
                      (SCIATH_COLORS.SUBHEADER, job.name, SCIATH_COLORS.ENDC,
                       exec_path))
                print(command_join(launch_command))
            _subprocess_run(launch_command, universal_newlines=True)
            os.chdir(cwd_back)
            _set_blocking_io_stdout()

    def clean(self, job, **kwargs):
        """ Remove all files created by the Launcher itself

            Note that this does not remove any files created by
            the Job (via its Tasks).
        """

        output_path = None
        for key, value in kwargs.items():
            if key == 'output_path':
                output_path = value

        if not output_path:
            raise ValueError(
                '[SciATH] cannot clean without an explicit output_path')
        if not os.path.isabs(output_path):
            raise ValueError(
                '[SciATH] cannot clean without an absolute output_path')

        c_name, o_name, e_name = job.get_output_filenames()
        _remove_file_if_it_exists(os.path.join(output_path, c_name))
        for filename in o_name:
            _remove_file_if_it_exists(os.path.join(output_path, filename))
        for filename in e_name:
            _remove_file_if_it_exists(os.path.join(output_path, filename))

        if self.queue_file_extension is not None:
            filename = "sciath.job-" + job.name + "-launch." + self.queue_file_extension
            _remove_file_if_it_exists(os.path.join(output_path, filename))
