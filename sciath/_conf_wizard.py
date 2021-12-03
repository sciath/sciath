""" Interactive tool for populating Launcher configuration information """

import os

from sciath._sciath_io import py23input


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


def _launcher_interactive_configure(launcher):
    """ Create a new configuration file from user input """
    print("--------------------------------------------------------------")
    print("Creating new configuration file %s" % launcher.conf_filename)

    launcher.set_queue_system_type(
        _query_user(
            "\n[1] Batch queuing system type",
            options=["local", "lsf", "slurm"],
            default="local",
        ))

    mpi_launch_examples = [
        "  No MPI Required           : none",
        "  Local Machine (mpirun)    : mpirun -np <ranks>",
        "  Local Machine (mpiexec)   : mpiexec -np <ranks>",
        "  SLURM w/ aprun            : aprun -B",
        "  Native SLURM              : srun -n $SLURM_NTASKS",
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

    mpi_launch = _query_user(
        "\n[2] MPI launch command, including <ranks> for number of ranks",
        examples=mpi_launch_examples,
        default="none",
        validate=launcher.is_valid_mpi_launch)

    launcher.set_mpi_launch(mpi_launch)

    launcher.account_name = _query_user("\n[3] Account to charge", default="")

    launcher.queue_name = _query_user("\n[4] Name of queue to submit tests to",
                                      default="")

    launcher.template_filename = launcher.write_default_template(
        launcher.queuing_system_type)

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
