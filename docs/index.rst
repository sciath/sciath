======
SciATH
======

This is documentation for `SciATH`_, the Scientific Application Test Harness.

..  _SciATH: https://www.github.com/sciath/sciath

What is it?
===========

Testing code should be easy. The functionality required to launch, parse and
perform verification should be light-weight and simple to migrate into existing
projects. SciATH supports testing of sequential and MPI-parallel applications.
Tests can be performed locally, or submitted via a batch queuing system (e.g.
PBS, LSF, Slurm or LoadLeveler).

SciATH is a set of lightweight Python tools designed to quickly and easily test
scientific application codes. As such, it focuses on full-application testing
and prioritizes being able to run on clusters with batch systems.  This is in
contrast to most testing frameworks, which are designed with libraries in mind,
and are often closely associated with specific programming languages.

Key Concepts
============

SciATH provides:

-  An object to define a test. A ``Test`` consists of:

   -  a unique name;
   -  one or more executables;
   -  a number of MPI ranks (1 for serial execution)
   -  a method to determine success (for instance checking an error code or an output file)

-  A set of tools to parse / filter and query text files for test
   verification purposes
-  A ``Harness`` object to quickly define and process a set of ``Test`` objects.
-  Internally, a ``Launcher`` object to manage launching a serial or MPI
   ``Job`` locally or via a batch queuing system

How do I use this ?
===================

1. SciATH depends on Python. It is tested with Python 2.7 and later, and requires
   no modules outside of the standard library. Almost all systems already support this.
   It is of course recommended to use Python 3, when possible, as Python 2 is
   no longer being maintained.

2. It is highly recommended you set the environment
   variable ``PYTHONUNBUFFERED``, e.g. ``export PYTHONUNBUFFERED``

3. Make sure you modify your ``PYTHONPATH`` environment variable to include
   this root `sciath` directory (containing the `sciath` package directory)

Topics
======

.. toctree ::
  tutorial
  design
  api
  developer

Indices
=======

* :ref:`genindex`
* :ref:`modindex`
