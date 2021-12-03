""" Interactive tool for populating Launcher configuration information """

import os

from sciath._sciath_io import py23input


def _launcher_interactive_configure(launcher):
    """ Create a new configuration file from user input """
    print('--------------------------------------------------------------')
    print('Creating new configuration file ', launcher.conf_filename)
    user_input = None
    while not user_input:
        prompt = '[1] Batch queuing system type <local,lsf,slurm>: '
        user_input = py23input(prompt)
        if not user_input:
            print('Required.')
        else:
            try:
                launcher.set_queue_system_type(user_input)
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
                print(
                    ('  Example PETSc MPI wrapper : '
                     '/users/myname/petsc/arch-xxx/bin/mpiexec -n <ranks>'))
            print((' Note that the string \"<ranks>\" must be included if '
                   'the number of ranks is required at launch.'))
            print((
                ' The keyword <ranks> will be replaced by the actual number '
                'of MPI ranks (defined by a given test) when the test is launched.'
            ))
    launcher.set_mpi_launch(user_input)

    prompt = '[3] Account to charge (optional - hit enter if not applicable): '
    launcher.account_name = py23input(prompt)

    prompt = ('[4] Name of queue to submit tests to '
              '(optional - hit enter if not applicable): ')
    launcher.queue_name = py23input(prompt)

    launcher.template_filename = launcher.write_default_template(
        launcher.queuing_system_type)

    print('** The template for generating batch submission files is\n')
    print('**  ', launcher.template_filename)
    print('**  You may modify it if desired\n')

    launcher._write_definition()
    print('\n')
    print(
        '** If you wish to change the config for your batch system, either')
    print('**  (i) delete the file', launcher.conf_filename, ' or')
    print('** (ii) re-run with the command line arg --configure')
    print( '--------------------------------------------------------------')
