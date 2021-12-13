========================
SciATH with MPI Tutorial
========================

TODO


Configuring the launcher
========================

In order to run MPI jobs, SciATH needs to know how these jobs
are run on your system. On some local systems, this might be something like

.. code-block:: sh

    mpiexec -np 2 my_executable -arg1 -arg2

but in general there are many variations.

For this reason, SciATH stores information about how a local system runs jobs
in configuration file, by default called ``SciATH_launcher.conf``, which points
to a template file, by default called ``SciATH_template.ext``, where ``.ext``
is replaced by an appropriate extension. For example, on a local system, this
file is called ``SciATH_template.sh``, since it is a POSIX shell script, run with the
``sh`` executable.

If the configuration file doesn't exist, running SciATH will interactively prompt you
for some information. The most crucial is the specification of the MPI launch command.
On a local system, this might be something like

.. code-block:: sh

   mpiexec -np <ranks>


Specifying number of ranks
==========================

As discussed in the :doc:`advanced_input`,
each test includes one or more tasks. These tasks
consist of a command (which executable and arguments to run),
and also information about what resources are required to execute
the task as part of a job.

You may specify a number of ranks at the level of a test,
providing a default. Note that this number may be ``0``, indicated
that by default, MPI is not used. Note that SciATH considers this distinct
from ``1`` rank, even though in many cases, an executable run on a single rank
may behave exactly like an executable run without MPI.

You may specify the number of ranks for each task, as well. This
overrides any job-level value.

If the number of ranks isn't specified at all for a task, it is assumed
that MPI is not required.



Example: using SciaTH with PETSc
================================

The following example shows how one can use captured environment variables,
and a custom mpiexec wrapper to execute tests from a large scientific library,
in this case [PETSc](https://petsc.org).

TODO: with a working PETSc install, reproduce the "test check" case. I already have this is my PETSc helpers, basically! (Just do it all from the input file, since we can now run non-MPI jobs as well.)
