""" Interactive tool for populating Launcher configuration information """

import os
import shlex
import shutil

from sciath._sciath_io import py23input
from sciath._default_templates import _generate_default_template
from sciath.utility import DotDict

DEFAULTS_LOCAL = DotDict()
DEFAULTS_LOCAL.job_submission_command = ("sh",)
DEFAULTS_LOCAL.blocking = True
DEFAULTS_LOCAL.has_job_level_ranks = False

DEFAULTS_LSF = DotDict()
DEFAULTS_LSF.job_submission_command = (
    "sh",
    "-c",
    "bsub < $0",
)  # This allows "<".
DEFAULTS_LSF.blocking = False
DEFAULTS_LSF.has_job_level_ranks = True
DEFAULTS_LSF.mpi_launch = "mpirun"

DEFAULTS_SLURM = DotDict()
DEFAULTS_SLURM.job_submission_command = ("sbatch",)
DEFAULTS_SLURM.blocking = False
DEFAULTS_SLURM.has_job_level_ranks = True
DEFAULTS_SLURM.mpi_launch = "srun -n <ranks>"

DEFAULTS = {
    "local": DEFAULTS_LOCAL,
    "lsf": DEFAULTS_LSF,
    "slurm": DEFAULTS_SLURM,
}


def _query_user(description="",
                options=None,
                examples=None,
                default=None,
                validate=None):
    valid = False
    while not valid:
        options_string = "" if options is None else " <%s>" % ", ".join(options)

        print("%s%s" % (description, options_string))
        if examples is not None:
            print("Examples:")
            for example in examples:
                print(example)

        if default is not None:
            print("Hit enter to accept default [%s]" % default)

        result = py23input("> ")
        result = os.path.expandvars(result)
        result = os.path.expanduser(result)

        if result == "":
            result = default

        valid = options is None or result in options
        if validate is not None and valid:
            valid = validate(result)

    return result


def _launcher_interactive_configure(launcher):  #pylint: disable=too-many-statements, too-many-branches
    """ Create a new configuration file from user input """
    print("--------------------------------------------------------------")
    print("Creating new configuration file %s" % launcher.conf_filename)

    system_type_options = list(DEFAULTS.keys()) + ["generic"]
    system_type = _query_user("\n[?] Batch queuing system type",
                              options=system_type_options,
                              default="local")

    if system_type in DEFAULTS:
        launcher.job_submission_command = list(
            DEFAULTS[system_type].job_submission_command)
    else:
        launcher.job_submission_command = shlex.split(
            _query_user("\n[?] job submission command",
                        validate=lambda command: command is not None))

    if system_type in DEFAULTS:
        launcher.blocking = DEFAULTS[system_type].blocking
    else:
        launcher.blocking = _query_user("\n[?] blocking",
                                        options=["True", "False"]) == "True"

    if system_type in DEFAULTS:
        launcher.has_job_level_ranks = DEFAULTS[system_type].has_job_level_ranks
    else:
        launcher.has_job_level_ranks = _query_user(
            "\n[?] supports job-level ranks specification",
            options=["True", "False"]) == "True"

    mpi_launch_examples = [
        "  No MPI Required           : none",
        "  Local Machine (mpirun)    : mpirun -np <ranks>",
        "  Local Machine (mpiexec)   : mpiexec -np <ranks>",
        "  SLURM w/ aprun            : aprun -B",
        "  Native SLURM              : srun -n <ranks>",
        "  LSF (Euler)               : mpirun",
    ]
    petsc_dir = os.getenv("PETSC_DIR")
    petsc_arch = os.getenv("PETSC_ARCH")
    if petsc_dir and petsc_arch:
        mpi_launch_examples.append(
            "  Current PETSc MPI wrapper : %s -n <ranks>" %
            os.path.join(petsc_dir, petsc_arch, "bin", "mpiexec"))
    else:
        mpi_launch_examples.append(
            "  Example PETSc MPI wrapper : /users/myname/petsc/arch-xxx/bin/mpiexec -n <ranks>"
        )

    if system_type in DEFAULTS and "mpi_launch" in DEFAULTS[system_type]:
        mpi_launch_default = DEFAULTS[system_type].mpi_launch
    else:
        mpi_launch_default = "none"
    mpi_launch = _query_user(
        "\n[?] MPI launch command, including <ranks> for number of ranks",
        examples=mpi_launch_examples,
        default=mpi_launch_default,
        validate=launcher.is_valid_mpi_launch)

    launcher.set_mpi_launch(mpi_launch)

    launcher.account_name = _query_user("\n[?] Account to charge", default="")

    launcher.queue_name = _query_user("\n[?] Name of queue to submit tests to",
                                      default="")

    # Assume, dubiously, that defaults defined here have a default template defined,
    # that the user always wants to use.
    query_template = system_type not in DEFAULTS
    if query_template:
        template_source_filename = _query_user(
            "\n[?]Please select a file, to be copied here, to use as a Launcher template",
            validate=os.path.isfile,
        )
        template_filename = os.path.split(template_source_filename)[1]
        if not os.path.isfile(template_filename):
            shutil.copyfile(template_source_filename, template_filename)
        launcher.template_filename = template_filename
    else:
        launcher.template_filename = _generate_default_template(system_type)

    launcher.write_definition(launcher.conf_filename)

    print("")
    print("** The template for batch submission files is  %s" %
          launcher.template_filename)
    print("** You may modify it if desired, but it will be overwritten")
    print("** if you re-configure.")
    print("")
    print("** To change the config for your batch system, either")
    print("**  (i) delete the file %s  or" % launcher.conf_filename)
    print("** (ii) re-run with the command line arg --configure")
    print("--------------------------------------------------------------")
