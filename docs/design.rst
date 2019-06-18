=====================
Design and Motivation
=====================

Why another test harness?

We wrote pyTestHarness because we couldn't find a test harness that
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
