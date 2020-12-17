""" SciATH Launcher class """
from __future__ import print_function

import os
import sys
import fcntl
import subprocess
import re

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

def _formatted_split_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return [('%02d' % unit) for unit in (hours, minutes, seconds)]


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


def job_complete(job, output_path):
    """ Returns True if a Job has completed with the given output path """
    return os.path.isfile(os.path.join(output_path, job.complete_filename))


def job_launched(job, output_path):
    """ Returns True if a Job has launched with the given output path """
    return os.path.isfile(os.path.join(output_path, job.launched_filename))


def _subprocess_run(command, **kwargs):
    """ Wrapper for subprocess.run, to allow usage from Python 2

        It returns the error code.

        This is to avoid a dependency like subprocess32.
    """
    if sys.version_info[0] >= 3:
        ctx = subprocess.run(command, check=False, **kwargs)  #pylint: disable=no-member
        returncode = ctx.returncode
    else:
        for key in ['stdout', 'stderr']:
            if key in kwargs and kwargs[key] == 'PIPE':
                raise Exception(('The current implementation cannot handle pipes. '
                                 'See the subprocess documentation for an alternative.'))
        returncode = subprocess.call(command, **kwargs)
    return returncode


class Launcher:  #pylint: disable=too-many-instance-attributes
    """ :class:`Launcher` is responsible for executing :class:`Task`s specified by a :class:`Job`,
    depending on its system-dependent configuration.

    Thus, it is:

    * The exclusive location for system-specific information
    * The exclusive reader of system-specific configuration file

    :class:`Launcher` include methods to operate on a combination of a :class:`Job` and a path:

    * Run the job from that path. If not on a batch system, blocks until the job completes.
    * Check the status of the job as run from that path
    * Clean up after a job, removing configuration-specific generated files

    :class:`Launcher` does not know about :class:`Test` or :class:`Harness`,
    and it should be possible to use :class:`Launcher` and a collection of
    :class:`Job` objects as a convenience to execute sets of tasks on various systems.

    A :class:`Launcher`'s state corresponds only to its configuration,
    not the status of any particular "run" of a :class:`Job`.
    """

    _default_conf_filename = 'SciATHBatchQueuingSystem.conf'

    @staticmethod
    def write_default_definition(conf_filename_in=None):
        """ Writes a default configuration file """
        major, minor, patch = sciath.__version__
        conf_filename = conf_filename_in if conf_filename_in else Launcher._default_conf_filename
        with open(conf_filename, 'w') as conf_file:
            conf_file.write('majorVersion: %s\n' % major)
            conf_file.write('minorVersion: %s\n' % minor)
            conf_file.write('patchVersion: %s\n' % patch)
            conf_file.write('queuingSystemType: none\n')
            conf_file.write('mpiLaunch: none\n')

    def __init__(self, conf_filename=None, template_filename=None):
        self.account_name = []
        self.queue_name = []
        self.mpi_launch = []
        self.queuing_system_type = []
        self.batch_constraint = []
        self.job_submission_command = []
        self.use_batch = False
        if conf_filename:
            self.conf_filename = conf_filename
        else:
            self.conf_filename = Launcher._default_conf_filename
        self.queue_file_extension = None

        # Incremental step: use a template to construct the submission
        # script (but not for configuration)
        self.use_template = template_filename is not None
        if self.use_template:
            self.template_filename = os.path.expanduser(template_filename)
            self.launch_script_filename = 'launch' + os.path.splitext(template_filename)[1]
        self.template = None

        self._setup()

        if self.use_batch:
            if self.mpi_launch == 'none':
                raise RuntimeError(('[SciATH] If using a queuing system, a valid mpi '
                                    'launch command must be provided'))



    def _create_launch_script(self, job, **kwargs): # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        output_path = os.getcwd()
        for key, value in kwargs.items():
            if key == 'output_path':
                output_path = value
                if not os.path.isabs(output_path):
                    raise ValueError(
                        '[SciATH] Unsupported: output paths must be absolute')

        # Lazily populate the template information from file
        self._populate_template()

        # Apply replacement map at the Job level
        hours_str, minutes_str, seconds_str = _formatted_split_time(60.0 * job.total_wall_time())
        rule_job = {
            '$SCIATH_JOB_NAME': job.name,
            '$SCIATH_JOB_MAX_RANKS': str(job.resource_max('ranks')),
            '$SCIATH_JOB_STDOUT': os.path.join(output_path, job.stdout_filename),
            '$SCIATH_JOB_STDERR': os.path.join(output_path, job.stderr_filename),
            '$SCIATH_JOB_EXITCODE': os.path.join(output_path, job.exitcode_filename),
            '$SCIATH_JOB_WALLTIME_H': hours_str,
            '$SCIATH_JOB_WALLTIME_M': minutes_str,
            '$SCIATH_JOB_WALLTIME_S': seconds_str,
            '$SCIATH_JOB_COMPLETE': os.path.join(output_path, job.complete_filename),
        }
        pattern = _get_multiple_replace_pattern(rule_job)
        script = [
            pattern.sub(lambda match, rule=rule_job: rule[match.group(0)], line)
            for line in self.template
        ]

        # Split the script into preamble, per-task, and postamble
        # This logic is quite brittle.
        task_lines = []
        threads_line_found = False
        ranks_line_found = False
        command_line_found = False
        preamble = []
        preamble_finished = False
        postamble = []
        for line in script:
            if  '$SCIATH_TASK_THREADS' in line:
                preamble_finished = True
                if threads_line_found:
                    raise Exception("[SciATH] Multiple threads lines found in template")
                threads_line_found = True
                task_lines.append(line)
            elif '$SCIATH_TASK_RANKS' in line:
                preamble_finished = True
                if ranks_line_found:
                    raise Exception("[SciATH] Multiple ranks lines found in template")
                ranks_line_found = True
                task_lines.append(line)
            elif '$SCIATH_TASK_COMMAND' in line:
                preamble_finished = True
                if command_line_found:
                    raise Exception("[SciATH] Multiple command lines found in template")
                command_line_found = line
                task_lines.append(line)
            elif not preamble_finished:
                preamble.append(line)
            else:
                postamble.append(line)

        # Assemble the script, applying task-level replacements
        script_filename = os.path.join(output_path, self.launch_script_filename)
        with open(script_filename, 'w') as script_file:
            script_file.writelines(preamble)
            first = True
            for task in job.tasks:
                if first:
                    first = False
                else:
                    script_file.write('\n')
                rule_task = {
                    '$SCIATH_TASK_COMMAND': command_join(task.command),
                    '$SCIATH_TASK_RANKS': str(task.get_resource('ranks')),
                }
                pattern = _get_multiple_replace_pattern(rule_task)
                task_lines_specific = []
                for line in task_lines:
                    task_lines_specific.append(
                        pattern.sub(lambda match, rule=rule_task: rule[match.group(0)], line)
                    )
                script_file.writelines(task_lines_specific)
            script_file.writelines(postamble)

        return script_filename

    def _populate_template(self):
        if self.template is None:
            with open(self.template_filename, 'r') as template_file:
                self.template = template_file.readlines()

    def set_mpi_launch(self, name):
        """ Set the MPI launch command and check its form """
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
        """ Set queueing system type and derived properties """
        if system_type in ['sh', 'local', 'Local']:
            self.queuing_system_type = 'local'
            self.job_submission_command = ['sh']
            self.use_batch = True
            self.queue_file_extension = 'sh'

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

        elif system_type in ['none', 'None']:
            self.queuing_system_type = 'none'
            self.job_submission_command = ''
            self.queue_file_extension = None

        else:
            raise RuntimeError(
                '[SciATH] Unknown or unsupported batch queuing system "' +
                system_type + '" specified')

    def __str__(self):
        lines = []
        lines.append('[SciATH] Batch queueing system configuration [%s]' % self.conf_filename)
        lines.append('  Version:           %d.%d.%d' % sciath.__version__)
        lines.append('  Queue system:      %s' % self.queuing_system_type)
        lines.append('  MPI launcher:      %s' % self.mpi_launch)
        if self.use_batch:
            lines.append('  Submit command:    %s' % command_join(self.job_submission_command))
            if self.account_name:
                lines.append('  Account:           %s' % self.account_name)
            if self.queue_name:
                lines.append('  Queue:             %s' % self.queue_name)
            if self.batch_constraint:
                lines.append('  Constraint:        %s' % self.batch_constraint)
        return '\n'.join(lines)

    def configure(self): #pylint: disable=too-many-branches,too-many-statements
        """ Create a new configuration file from user input """
        print('----------------------------------------------------------------')
        print('Creating new configuration file ', self.conf_filename)
        user_input = None
        while not user_input:
            prompt = '[1] Batch queuing system type <local,lsf,slurm,none>: '
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
            prompt = ('[2] MPI launch command with num. procs. flag '
                      '(required - hit enter for examples): ')
            user_input = os.path.expandvars(py23input(prompt))
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
                    print(('  Example PETSc MPI wrapper : '
                           '/users/myname/petsc/arch-xxx/bin/mpiexec -n <ranks>'))
                print((' Note that the string \"<ranks>\" must be included if '
                       'the number of ranks is required at launch.'))
                print((' The keyword <ranks> will be replaced by the actual number '
                       'of MPI ranks (defined by a given test) when the test is launched.'))
        self.set_mpi_launch(user_input)

        if self.use_batch:
            prompt = ('[3] specify a constraint (e.g. "gpu" on Piz Daint) '
                      '(optional - hit enter if not applicable):')
            self.batch_constraint = py23input(prompt)

            prompt = '[4] Account to charge (optional - hit enter if not applicable): '
            self.account_name = py23input(prompt)

            prompt = ('[5] Name of queue to submit tests to '
                      '(optional - hit enter if not applicable): ')
            self.queue_name = py23input(prompt)

        self._write_definition()
        print('\n')
        print('** If you wish to change the config for your batch system, either')
        print('**  (i) delete the file', self.conf_filename, ' or')
        print('** (ii) re-run with the command line arg --configure')
        print('----------------------------------------------------------------')

    def _setup(self):
        try:
            self._load_definition()
        except SciATHLoadException:
            self.configure()
            self._write_definition()

    def _write_definition(self):
        major, minor, patch = sciath.__version__
        with open(self.conf_filename, 'w') as conf_file:
            conf_file.write('majorVersion: %s\n' % major)
            conf_file.write('minorVersion: %s\n' % minor)
            conf_file.write('patchVersion: %s\n' % patch)
            conf_file.write('queuingSystemType: %s\n' % self.queuing_system_type)
            conf_file.write('mpiLaunch: %s\n' % self.mpi_launch)
            if self.use_batch:
                conf_file.write('accountName: %s\n' % self.account_name)
                conf_file.write('batchConstraint: %s\n' % self.batch_constraint)
                conf_file.write('queueName: %s\n' % self.queue_name)

    def _load_definition(self): #pylint: disable=too-many-branches
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
                    self.batch_constraint = data['batchConstraint']
                if 'queueName' in data:
                    self.queue_name = data['queueName']
                if 'accountName' in data:
                    self.account_name = data['accountName']
        except (IOError, OSError):  # Would be FileNotFoundError for Python >3.5
            # pylint: disable=bad-option-value,raise-missing-from
            raise SciATHLoadException(('[SciATH] Configuration file missing. '
                                       'You must execute configure(), and/or '
                                       '_write_definition() first'))

        major, minor = sciath.__version__[:2]
        if major_file is None or minor_file is None or patch_file is None:
            raise RuntimeError('[SciATH] configuration file %s missing version information. '
                               'Please delete it and re-run to reconfigure.' %
                               self.conf_filename)
        if major_file < major or (minor_file < minor and major_file == major):
            raise RuntimeError('[SciATH] Incompatible, outdated configuration file %s '
                               'detected. Please delete it and re-run to reconfigure.' %
                               self.conf_filename)

    def _create_job_submission_file(self, job, walltime, output_path):

        # Verify input, check for generic errors
        if self.batch_constraint and self.queuing_system_type != 'slurm':
            message = '[SciATH] Constraints are only currently supported with SLURM'
            raise RuntimeError(message)

        if self.queuing_system_type == 'local':
            filename = self._generate_launch_sh(output_path, job)
        elif self.queuing_system_type == 'lsf':
            filename = self._generate_launch_lsf(None, walltime, output_path, job)
        elif self.queuing_system_type == 'slurm':
            filename = self._generate_launch_slurm(walltime, output_path, job)

        print('Created submission file:', filename)
        return filename

    def submit_job(self, job, **kwargs):  #pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """ Attempt to run a job

        Supply output_path to change the location where SciATH's output
        files will be saved.

        Supply exec_path to change the directory from which the command
        will be executed.

        Returns a triple (success, info, report) describing if the launch
        succeeded, and a summary string and full report, if appropriate.
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

        if job_complete(job, output_path):
            raise Exception('[SciATH] trying to launch an already-complete Job')
        if job_launched(job, output_path):
            raise Exception('[SciATH] trying to launch an already-launched Job')

        if self.use_template:
            script_filename = self._create_launch_script(job, output_path=output_path)
            launch_command = self.job_submission_command + [script_filename]

            print('%s[Executing %s]%s from %s' %
                  (SCIATH_COLORS.subheader, job.name, SCIATH_COLORS.endc,
                   exec_path))
            print(command_join(launch_command))

            cwd_back = os.getcwd()
            os.chdir(exec_path)
            _subprocess_run(launch_command, universal_newlines=True)
            os.chdir(cwd_back)
            _set_blocking_io_stdout()
            with open(os.path.join(output_path, job.launched_filename), 'w'):
                pass
            return True, None, None

        # "Old" way of creating a job script, to be superceded with template approach
        _set_blocking_io_stdout()

        if not self.use_batch:
            mpi_launch = self.mpi_launch
            ranks = job.resource_max('mpiranks')
            threads = job.resource_max('threads')
            if threads is not None and threads != 1:
                raise ValueError(
                    '[SciATH] Unsupported: Job cannot be submitted multi-threaded'
                )

            if self.mpi_launch == 'none' and ranks is not None and ranks != 1:
                return False, 'MPI required', ['Not launched: requires MPI']

            command_resource = job.create_execute_command()
            launch_command = []
            for command, resource in command_resource:
                launch = []
                if self.mpi_launch != 'none':
                    j_ranks = resource["mpiranks"]
                    launch += _format_mpi_launch_command(mpi_launch, j_ranks)
                launch.extend(command)
                launch_command.append(launch)

            print('%s[Executing %s]%s from %s' %
                  (SCIATH_COLORS.subheader, job.name, SCIATH_COLORS.endc,
                   exec_path))
            for term in launch_command:
                print(command_join(term))

            with open(os.path.join(output_path, job.exitcode_filename), 'w') as file_exitcode, \
                 open(os.path.join(output_path, job.stderr_filename), 'w') as file_stderr, \
                 open(os.path.join(output_path, job.stdout_filename), 'w') as file_stdout:
                for command in launch_command:
                    cwd_back = os.getcwd()
                    os.chdir(exec_path)
                    returncode = _subprocess_run(command, universal_newlines=True,
                                                 stdout=file_stdout, stderr=file_stderr)
                    os.chdir(cwd_back)
                    file_exitcode.write(str(returncode) + "\n")
                    _set_blocking_io_stdout()
            with open(os.path.join(output_path, job.launched_filename), 'w'):
                pass
            with open(os.path.join(output_path, job.complete_filename), 'w'):
                pass
        else:
            walltime = job.total_wall_time()

            launchfile = self._create_job_submission_file(job, walltime, output_path)
            launch_command = self.job_submission_command + [launchfile]
            cwd_back = os.getcwd()
            os.chdir(exec_path)
            print('%s[Executing %s]%s from %s' %
                  (SCIATH_COLORS.subheader, job.name, SCIATH_COLORS.endc,
                   exec_path))
            print(command_join(launch_command))
            _subprocess_run(launch_command, universal_newlines=True)
            os.chdir(cwd_back)
            _set_blocking_io_stdout()
            with open(os.path.join(output_path, job.launched_filename), 'w'):
                pass

        return True, None, None

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
            raise ValueError('[SciATH] cannot clean without an explicit output_path')
        if not os.path.isabs(output_path):
            raise ValueError('[SciATH] cannot clean without an absolute output_path')

        for filename in [job.exitcode_filename, job.stdout_filename, job.stderr_filename]:
            _remove_file_if_it_exists(os.path.join(output_path, filename))

        if self.queue_file_extension is not None:
            filename = self._batch_filename(job)
            _remove_file_if_it_exists(os.path.join(output_path, filename))

        _remove_file_if_it_exists(os.path.join(output_path, job.launched_filename))
        _remove_file_if_it_exists(os.path.join(output_path, job.complete_filename))

    def _batch_filename(self, job):
        return job.name + "." + self.queue_file_extension

    def _generate_launch_sh(self, output_path, job):

        mpi_launch = self.mpi_launch
        filename = os.path.join(output_path, self._batch_filename(job))
        exitcode_name = job.exitcode_filename

        # This is awkward and suboptimal. It would be better to have
        # the ability to modify the command used to launch the script,
        # based on the job. Then, output could be redirected there,
        # making the local launch behave more like cluster launch.
        redirect_string = "1>%s 2>%s" % (
                os.path.join(output_path, job.stdout_filename),
                os.path.join(output_path, job.stderr_filename),
                )

        with open(filename, "w") as file:
            file.write("#!/usr/bin/env sh\n")
            file.write("# SciATH: auto-generated POSIX shell script\n\n")

            _remove_file_if_it_exists(os.path.join(output_path, exitcode_name))

            for command, resources in job.create_execute_command():
                ranks = resources["mpiranks"]
                launch = [redirect_string]
                launch += _format_mpi_launch_command(mpi_launch, ranks)
                if isinstance(command, list):
                    launch.append(command_join(command))
                else:
                    launch.append(command)

                file.write(" ".join(launch) + " \n")
                file.write("echo $? >> " + os.path.join(output_path, exitcode_name) + "\n")
            file.write("\n")
            file.write("touch %s\n" % os.path.join(output_path, job.complete_filename))

        return filename


    def _generate_launch_lsf(self, rusage, walltime, output_path, job):  #pylint: disable=too-many-locals

        if walltime is None:
            message = "[SciATH] _generate_launch_lsf requires walltime be specified"
            raise RuntimeError(message)

        accountname = self.account_name
        queuename = self.queue_name
        mpi_launch = self.mpi_launch

        resources = job.get_max_resources()
        ranks = resources["mpiranks"]

        exitcode_name = job.exitcode_filename
        stdout_name = job.stdout_filename
        stderr_name = job.stderr_filename

        filename = os.path.join(output_path, self._batch_filename(job))
        with open(filename, "w") as file:
            # LSF specifics
            file.write("#!/bin/sh\n")
            file.write("# SciATH: auto-generated lsf file\n")

            if accountname:
                file.write("#BSUB -G " + accountname + "\n")

            file.write("#BSUB -J " + "sciath.job-" + job.name + "\n")
            file.write("#BSUB -o " + os.path.join(output_path, stdout_name) + "\n")
            file.write("#BSUB -e " + os.path.join(output_path, stderr_name) + "\n")

            if queuename:
                file.write("#BSUB -q " + queuename + "\n")

            file.write("#BSUB -n " + str(ranks) + "\n")

            if rusage:
                file.write("#BSUB -R \'" + rusage + "\'" + "\n")

            walltime_string = _formatted_hour_min(float(walltime) * 60.0)
            file.write("#BSUB -W " + walltime_string + "\n")

            _remove_file_if_it_exists(os.path.join(output_path, exitcode_name))

            command_resource = job.create_execute_command()
            n_tasks = len(command_resource)
            for i in range(0, n_tasks):
                j = command_resource[i]
                j_ranks = j[1]["mpiranks"]
                launch = []
                launch += _format_mpi_launch_command(mpi_launch, j_ranks)
                if isinstance(j[0], list):
                    launch.append(command_join(j[0]))
                else:
                    launch.append(j[0])

                file.write(" ".join(launch) + "\n")
                file.write("echo $? >> " + os.path.join(output_path, exitcode_name) + "\n")
            file.write("\n")
            file.write("touch %s\n" % os.path.join(output_path, job.complete_filename))
        return filename


    def _generate_launch_slurm(self, walltime, output_path, job):  #pylint: disable=too-many-locals

        if walltime is None:
            message = "[SciATH] _generate_launch_slurm requires walltime be specified"
            raise RuntimeError(message)

        accountname = self.account_name
        queuename = self.queue_name
        constraint = self.batch_constraint
        mpi_launch = self.mpi_launch

        resources = job.get_max_resources()
        ranks = resources["mpiranks"]

        exitcode_name = job.exitcode_filename
        stdout_name = job.stdout_filename
        stderr_name = job.stderr_filename

        filename = os.path.join(output_path, self._batch_filename(job))
        with open(filename, "w") as file:
            # SLURM specifics
            file.write("#!/bin/bash -l\n")
            file.write("# SciATH: auto-generated slurm file\n")

            if accountname:
                file.write("#SBATCH --account=" + accountname +
                           "\n")  # account to charge

            file.write("#SBATCH --job-name=\"" + "sciath.job-" + job.name + "\"" + "\n")
            file.write("#SBATCH --output=" + os.path.join(output_path, stdout_name) + "\n")
            file.write("#SBATCH --error=" + os.path.join(output_path, stderr_name) + "\n")

            if queuename:
                file.write("#SBATCH --partition=" + queuename + "\n")

            file.write("#SBATCH --ntasks=" + str(ranks) + "\n")

            if constraint:
                file.write("#SBATCH --constraint=" + constraint + "\n")

            walltime_string = _formatted_hour_min_sec(float(walltime) * 60.0)
            file.write("#SBATCH --time=" + walltime_string + "\n")

            file.write("export CRAY_CUDA_MPS=1\n")

            _remove_file_if_it_exists(os.path.join(output_path, exitcode_name))

            command_resource = job.create_execute_command()
            n_tasks = len(command_resource)
            for i in range(0, n_tasks):
                j = command_resource[i]
                j_ranks = j[1]["mpiranks"]
                launch = []
                launch += _format_mpi_launch_command(mpi_launch, j_ranks)
                if isinstance(j[0], list):
                    launch.append(command_join(j[0]))
                else:
                    launch.append(j[0])

                file.write(" ".join(launch) + "\n")
                file.write("echo $? >> " + os.path.join(output_path, exitcode_name) + "\n")
            file.write("\n")
            file.write("touch %s\n" % os.path.join(output_path, job.complete_filename))
        file.close()
        return filename


def _get_multiple_replace_pattern(source_dict):
    """ Generate a regex to match any of the keys in source_dict

        Important: this match is not done on full words, so behavior
        when one key is a substring of another is undefined.
    """
    def process_word(word):
        """ add escape characters """
        return re.escape(word)
    return re.compile(r'|'.join(map(process_word, source_dict)))
