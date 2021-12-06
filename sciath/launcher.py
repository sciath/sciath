""" SciATH Launcher class """
from __future__ import print_function

import os
import shlex
import sys
import fcntl
import subprocess
import re

import sciath
from sciath import yaml_parse
from sciath import SCIATH_COLORS
from sciath.utility import DotDict
from sciath._sciath_io import _remove_file_if_it_exists, command_join
from sciath._default_templates import _generate_default_template
from sciath._conf_wizard import _launcher_interactive_configure


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


def _formatted_split_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return [('%02d' % unit) for unit in (hours, minutes, seconds)]


def _format_mpi_launch_command(mpi_launch, ranks):
    launch = mpi_launch.replace("<ranks>", str(ranks))
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
                raise Exception(
                    ('The current implementation cannot handle pipes. '
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

    _default_conf_filename = 'SciATH_launcher.conf'

    @staticmethod
    def write_default_definition(conf_filename_in=None):
        """ Writes a default configuration file """
        major, minor, patch = sciath.__version__
        conf_filename = conf_filename_in if conf_filename_in else Launcher._default_conf_filename
        template_filename = _generate_default_template("local")
        with open(conf_filename, 'w') as conf_file:
            conf_file.write('majorVersion: %s\n' % major)
            conf_file.write('minorVersion: %s\n' % minor)
            conf_file.write('patchVersion: %s\n' % patch)
            conf_file.write('submitCommand: sh\n')
            conf_file.write('blocking: True\n')
            conf_file.write('jobLevelRanks: False\n')
            conf_file.write('mpiLaunch: none\n')
            conf_file.write('template: %s\n' % template_filename)

    def __init__(self, conf_filename=None):
        self.account_name = None
        self.queue_name = None
        self.mpi_launch = None
        self.job_submission_command = None
        self.has_job_level_ranks = None
        self.blocking = None
        if conf_filename:
            self.conf_filename = conf_filename
        else:
            self.conf_filename = Launcher._default_conf_filename
        self.template_filename = None
        self.template = None

        self._setup()

    def _create_launch_script(self, job, output_path):
        if not os.path.isabs(output_path):
            raise ValueError(
                '[SciATH] Unsupported: output paths must be absolute')

        # Lazily populate the template information from file
        self._populate_template()

        # Apply replacements at the Job level
        replace_rules = {
            '$SCIATH_JOB_NAME':
                job.name,
            '$SCIATH_JOB_MAX_RANKS':
                str(job.resource_max('ranks')),
            '$SCIATH_JOB_STDOUT':
                os.path.join(output_path, job.stdout_filename),
            '$SCIATH_JOB_STDERR':
                os.path.join(output_path, job.stderr_filename),
            '$SCIATH_JOB_EXITCODE':
                os.path.join(output_path, job.exitcode_filename),
            '$SCIATH_JOB_COMPLETE':
                os.path.join(output_path, job.complete_filename),
        }
        delete_rules = set()

        job_wall_time = job.total_wall_time()
        if job_wall_time is None:
            delete_rules.add('$SCIATH_JOB_WALLTIME_HM_OR_REMOVE_LINE')
            delete_rules.add('$SCIATH_JOB_WALLTIME_HMS_OR_REMOVE_LINE')
        else:
            hours_str, minutes_str, seconds_str = _formatted_split_time(60.0 * job.total_wall_time())
            replace_rules[r'$SCIATH_JOB_WALLTIME_HM_OR_REMOVE_LINE'] = '%s:%s:%s' % (hours_str, minutes_str)
            replace_rules[r'$SCIATH_JOB_WALLTIME_HMS_OR_REMOVE_LINE'] = '%s:%s:%s' % (hours_str, minutes_str, seconds_str),

        # Assemble the script, applying task-level replacements
        script_filename = os.path.join(output_path, self._batch_filename(job))

        with open(script_filename, 'w') as script_file:
            # Pre
            script_file.writelines(
                _process_lines(self.template.pre, replace=replace_rules, delete=delete_rules))

            # Task
            first = True
            for task in job.tasks:
                if first:
                    first = False
                else:
                    script_file.write('\n')
                task_ranks = task.get_resource('ranks')
                rule_task = {
                    '$SCIATH_TASK_COMMAND': command_join(task.command),
                    '$SCIATH_TASK_RANKS': str(task_ranks),
                }
                if self.mpi_launch != 'none':
                    rule_task['$SCIATH_TASK_MPI_RUN'] = command_join(
                        _format_mpi_launch_command(self.mpi_launch, task_ranks))

                task_lines_specific = _process_lines(self.template.task,
                                                     replace=rule_task)

                script_file.writelines(
                    _process_lines(task_lines_specific, replace=replace_rules, delete=delete_rules))

            # Post
            script_file.writelines(
                _process_lines(self.template.post, replace=replace_rules, delete=delete_rules))

        return script_filename

    def _populate_template(self):  #pylint: disable=too-many-branches
        """ Process the template file, interpreting a relative path
        with respect to the location of the configuration file

        Populate a DotDict with the lines or lists of lines required
        to build launch scripts.
        """
        if self.template is not None:
            return
        filename = self.template_filename
        if not os.path.isabs(filename):
            filename = os.path.join(os.path.dirname(self.conf_filename),
                                    filename)
        self.template = DotDict()
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Launcher-level replacements and deletions
        replace_rules = {}
        delete_rules = set()
        for (term, setting) in (
            ('$SCIATH_QUEUE_OR_REMOVE_LINE', self.queue_name),
            ('$SCIATH_ACCOUNT_OR_REMOVE_LINE', self.account_name),
        ):
            if not setting:
                delete_rules.add(term)
            else:
                replace_rules[term] = setting

        lines = _process_lines(lines,
                               replace=replace_rules,
                               delete=delete_rules)

        # Construct template components
        self.template.pre = []
        self.template.mpi = False
        self.template.threads = False
        self.template.command = False
        self.template.task = []
        self.template.post = []
        preamble_finished = False
        for line in lines:
            if '$SCIATH_TASK_THREADS' in line:
                preamble_finished = True
                if self.template.threads:
                    raise Exception(
                        "[SciATH] Multiple threads lines found in template")
                self.template.threads = True
                self.template.task.append(line)
            elif '$SCIATH_TASK_RANKS' in line or '$SCIATH_TASK_MPI_RUN' in line:
                preamble_finished = True
                if self.template.threads:
                    raise Exception(
                        "[SciATH] Multiple ranks lines found in template")
                self.template.threads = True
                if self.mpi_launch != 'none':
                    self.template.task.append(line)
            elif '$SCIATH_TASK_COMMAND' in line:
                preamble_finished = True
                if self.template.command:
                    raise Exception(
                        "[SciATH] Multiple command lines found in template")
                self.template.command = True
                self.template.task.append(line)
            elif not preamble_finished:
                self.template.pre.append(line)
            else:
                self.template.post.append(line)

    def set_mpi_launch(self, mpi_launch):
        """ Sets the MPI launch command and check its form """
        if mpi_launch in [None, 'none', 'None', '']:
            mpi_launch = 'none'
        if not self.is_valid_mpi_launch(mpi_launch):
            raise RuntimeError(
                '[SciATH] MPI launch command must contain the keyword \"<ranks>\"'
            )
        self.mpi_launch = mpi_launch

    def is_valid_mpi_launch(self, mpi_launch):
        """ Returns whether a given string is acceptable to launch MPI jobs """
        if mpi_launch == "none":
            return True
        if not self.has_job_level_ranks:
            return '<ranks>' in mpi_launch
        return True

    def __str__(self):
        lines = []
        lines.append('[SciATH] Batch queueing system configuration [%s]' %
                     self.conf_filename)
        lines.append('  Version:           %d.%d.%d' % sciath.__version__)
        lines.append('  MPI launcher:      %s' % self.mpi_launch)
        lines.append('  Submit command:    %s' %
                     command_join(self.job_submission_command))
        lines.append('  Blocking:          %s' % self.blocking)
        lines.append('  Job-level ranks:   %s' % self.has_job_level_ranks)
        if self.account_name:
            lines.append('  Account:           %s' % self.account_name)
        if self.queue_name:
            lines.append('  Queue:             %s' % self.queue_name)
        if self.queue_name:
            lines.append('  Template:          %s' % self.template_filename)
        return '\n'.join(lines)

    def configure(self):
        """ Interactively configure the Launcher """
        _launcher_interactive_configure(self)

    def _setup(self):
        try:
            self.load_definition(self.conf_filename)
        except SciATHLoadException:
            self.configure()
            self.write_definition(self.conf_filename)

    def write_definition(self, filename):
        """ Writes configuration to a file """
        major, minor, patch = sciath.__version__
        with open(filename, 'w') as conf_file:
            conf_file.write('majorVersion: %s\n' % major)
            conf_file.write('minorVersion: %s\n' % minor)
            conf_file.write('patchVersion: %s\n' % patch)
            conf_file.write('submitCommand: %s\n' %
                            command_join(self.job_submission_command))
            conf_file.write('blocking: %s\n' % self.blocking)
            conf_file.write('jobLevelRanks: %s\n' % self.has_job_level_ranks)
            conf_file.write('mpiLaunch: %s\n' % self.mpi_launch)
            conf_file.write('accountName: %s\n' % self.account_name)
            conf_file.write('queueName: %s\n' % self.queue_name)
            conf_file.write('template: %s\n' % self.template_filename)

    def load_definition(self, filename):  #pylint: disable=too-many-branches
        """ Loads configuration from a file """
        major_file = None
        minor_file = None
        patch_file = None
        try:
            data = yaml_parse.parse_yaml_subset_from_file(filename)
            if 'majorVersion' in data:
                major_file = int(data['majorVersion'])
            if 'minorVersion' in data:
                minor_file = int(data['minorVersion'])
            if 'patchVersion' in data:
                patch_file = int(data['patchVersion'])
            if 'submitCommand' in data:
                self.job_submission_command = shlex.split(data['submitCommand'])
            if 'blocking' in data:
                self.blocking = data['blocking'] == "True"
            if 'jobLevelRanks' in data:
                self.has_job_level_ranks = data['jobLevelRanks'] == "True"
            if 'mpiLaunch' in data:
                self.set_mpi_launch(data['mpiLaunch'])
            if 'queueName' in data:
                self.queue_name = data['queueName']
            if 'accountName' in data:
                self.account_name = data['accountName']
            if 'template' in data:
                self.template_filename = data['template']
        except (IOError, OSError):  # Would be FileNotFoundError for Python >3.5
            # pylint: disable=bad-option-value,raise-missing-from
            raise SciATHLoadException(('[SciATH] Configuration file missing. '
                                       'You must execute configure(), and/or '
                                       'write_definition() first'))

        major, minor = sciath.__version__[:2]
        if major_file is None or minor_file is None or patch_file is None:
            raise RuntimeError(
                '[SciATH] configuration file %s missing version information. '
                'Please delete it and re-run to reconfigure.' %
                self.conf_filename)
        if major_file < major or (minor_file < minor and major_file == major):
            raise RuntimeError(
                '[SciATH] Incompatible, outdated configuration file %s '
                'detected. Please delete it and re-run to reconfigure.' %
                self.conf_filename)

    def submit_job(self, job, output_path=None, exec_path=None):
        """ Attempt to run a Job

        Supply output_path to change the location where SciATH's output
        files will be saved.

        Supply exec_path to change the directory from which the command
        will be executed.

        Returns a triple (success, info, report) describing if the launch
        succeeded, and a summary string and full report, if appropriate.
        """

        if output_path is None:
            output_path = os.getcwd()
        else:
            if not os.path.isabs(output_path):
                raise ValueError('[SciATH] output paths must be absolute')
        if exec_path is None:
            exec_path = os.getcwd()
        else:
            if not os.path.isabs(exec_path):
                raise ValueError('[SciATH] exec paths must be absolute')

        if job_complete(job, output_path):
            raise Exception('[SciATH] trying to launch an already-complete Job')
        if job_launched(job, output_path):
            raise Exception('[SciATH] trying to launch an already-launched Job')

        _set_blocking_io_stdout()

        ranks = job.resource_max('ranks')
        if self.mpi_launch == 'none' and ranks is not None and ranks != 1:
            return False, 'MPI required', ['Not launched: requires MPI']

        script_filename = self._create_launch_script(job,
                                                     output_path=output_path)
        launch_command = self.job_submission_command + [script_filename]

        print(
            '%s[Executing %s]%s from %s' %
            (SCIATH_COLORS.subheader, job.name, SCIATH_COLORS.endc, exec_path))
        print(command_join(launch_command))

        cwd_back = os.getcwd()
        os.chdir(exec_path)
        _subprocess_run(launch_command, universal_newlines=True)
        os.chdir(cwd_back)
        _set_blocking_io_stdout()
        with open(os.path.join(output_path, job.launched_filename), 'w'):
            pass

        return True, None, None

    def clean(self, job, output_path=None):
        """ Remove all files created by the Launcher itself

            Note that this does not remove any files created by
            the Job (via its Tasks).
        """

        if output_path is None:
            raise ValueError(
                '[SciATH] cannot clean without an explicit output_path')
        if not os.path.isabs(output_path):
            raise ValueError(
                '[SciATH] cannot clean without an absolute output_path')

        for filename in [
                job.exitcode_filename, job.stdout_filename, job.stderr_filename
        ]:
            _remove_file_if_it_exists(os.path.join(output_path, filename))

        _remove_file_if_it_exists(
            os.path.join(output_path, self._batch_filename(job)))

        _remove_file_if_it_exists(
            os.path.join(output_path, job.launched_filename))
        _remove_file_if_it_exists(
            os.path.join(output_path, job.complete_filename))

    def _batch_filename(self, job):
        return job.name + os.path.splitext(self.template_filename)[1]


def _process_lines(lines_in, replace=None, delete=None):
    """ Process a list of lines based on sets of keys to replace and delete """
    if not delete:
        if not replace:
            return lines_in[:]
    else:
        delete_pattern = _get_multiple_match_pattern(delete)
        if not replace:
            return [
                line for line in lines_in
                if re.search(delete_pattern, line) is None
            ]

    lines = []
    replace_pattern = _get_multiple_match_pattern(replace)
    for line in lines_in:
        if not delete or re.search(delete_pattern, line) is None:
            if replace:
                lines.append(
                    replace_pattern.sub(
                        lambda match, rule=replace: rule[match.group(0)], line))

    return lines


def _get_multiple_match_pattern(source):
    """ Generate a regex to match any of the keys in a source dict or set

        Important: behavior is undefined with respect to the order of the substitutions,
        so inputs should be invariant to this, e.g. one key should
        not be a substring of another key.
    """

    def _process_word(word):
        return re.escape(word)

    return re.compile(r'|'.join(map(_process_word, source)))
