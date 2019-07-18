=====================
Design and Motivation
=====================

Why another test harness?

We wrote SciATH because we couldn't find a test harness that
did what we wanted. We wanted to  replace and generalize an existing
simple test suite for `pTatin3D`_ , an MPI-based code
for regional geodynamic simulation. We wanted something:

* simple and general
* easy to understand and work with
* tailored to test scientific applications, which tend to be

  * hard to unit test, being monolithic applications controlled by large parameter files and generating large output
  * susceptible to numerical "noise"
  * parallel, using MPI, OpenMP, OpenCL, CUDA, etc.
  * maintained by very few people
  * run in combination with setup and/or post-processing scripts, in various languages

* non-invasive, not requiring modification of application source or writing of new executables
* language-agnostic
* easily usable on many different systems, including clusters with batch systems
* portable, easy to run on any system without heavy dependencies
* robust
* usable with CI
* that "shows you what's happening", giving you the commands that are run, not running invisible processes, etc.

We found that most existing solutions were optimized for a rather different purpose,
unit testing of traditional software libraries in serial environments.

.. _pTatin3D: https://bitbucket.org/ptatin/ptatin3d

The main classes
----------------

Note: this material will likely make its way into the docstrings for these
classes and then be removed.

Job
~~~

* A command to be run, that is a string containing an executable and arguments. Note that any relative paths will be interpreted relative to where the command is run.
* A set of "resources" required. These are system-agnostic details like the number of (MPI) ranks or (OpenMP) threads.
* Information on how to interpret an exit code as indicating a successful run (note that in the case of running other testing programs, "error" exit codes may indicate that tests failed, not that the program didn't run as intended)
* An optional user-provided method to clean up after the command, assuming it has run once from the same path

Note that this class knows nothing about where it will be run from or how many times (possibly simultaneously).
Indeed, it is mostly just a collection of data.

Subclasses exist to describe composite sets of ``Job`` objects.

Launcher
~~~~~~~~

* The exclusive location for system-specific information
* The exclusive reader of system-specific configuration (a simple plain-text `key: value` file)

Includes methods to operate on a combination of a `Job` and a path:
* Run the job from that path. Depending on whether this is a batch system,
  * blocking: blocks, function returns error code
  * non-blocking: returns after launching
* Check the status of the job as run from that path
  * includes error code for batch jobs
* Clean up after a job, calling the clean method from the ``Job`` and removing other generated files

Note that it should be possible to use the Launcher and a set of Jobs as
a convenience to run the same commands on various systems, without knowing
anything about `Test` or `Harness`.

Test
~~~~

* A ``Job``
* A name
* A method to verify success
* An set of string-valued tags

Harness
~~~~~~~

The central object which users interact with, either in their own scripts
or via direct invocation of the `sciath` module.

* A set of uniquely-named ``Test`` objects
* A ``Launcher``
* Exclusive location for interaction with command-line arguments
* Exclusive location for printing to stdout
* Tools for running and verifying a test suite
* Can work with groups of tests defined by tags or resources
* Exclusive location of information about where to launch ``Jobs`` from, passed to included ``Launcher``
