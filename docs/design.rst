=====================
Design and Motivation
=====================

Why another test harness?

We wrote SciATH because we couldn't find a test harness that did what we
wanted. We wanted to  replace and generalize an existing simple test suite for
`pTatin3D`_ , an MPI-based code for regional geodynamic simulation. We wanted
something tailored to test scientific applications, which tend to be

* hard to unit test, being monolithic applications controlled by large parameter files and generating large output
* susceptible to numerical "noise"
* parallel, using MPI, OpenMP, OpenCL, CUDA, etc.
* maintained by very few people
* run in combination with setup and/or post-processing scripts, in various languages

Further, we wanted something

* simple and general
* easy to understand and work with
* quick to introduce to an existing scientific application
* non-invasive, not requiring modification of application source or writing of new executables
* language-agnostic
* easily usable on many different systems, including clusters with batch systems
* portable, easy to run on any system without heavy dependencies
    - SciATH works with Python 2.7 or later, with no non-standard modules required
* usable with CI
* that "shows you what's happening", giving you copy-pasteable commands being run, not running invisible processes, and leaving meaningful artifacts to interpret and re-run test cases

We found that most existing solutions were optimized for a rather different purpose,
unit testing of software libraries in serial environments.

.. _pTatin3D: https://bitbucket.org/ptatin/ptatin3d
