======
SciATH
======

This is documentation for `SciATH`_, the Scientific Application Test Harness.

..  _SciATH: https://www.github.com/sciath/sciath

What is it?
===========

Testing scientific code should be easier. The functionality required to launch, parse and
perform verification should be light-weight and simple to migrate into existing
projects. It should be easy to test on the local machines where code is developed
as well as the clusters where it is run, sequentially or in parallel with MPI, usually through
a batch queueing system like SLURM or LSF.

SciATH is a set of lightweight Python tools designed to quickly and easily test
scientific application codes wherever they are run. As such, it focuses on
full-application reference testing and prioritizes being able to run on
clusters with batch systems.  This contrasts with most testing frameworks,
which are designed with libraries in mind, are often closely associated
with specific programming languages, and do not explicitly consider the
use of parallel batch systems.

Key Concepts
============

SciATH provides a convenient command-line interface to read a set of tests from a simple input file and run them.

This is accomplished by using its Python API, including

- A ``Test`` consisting of:

   -  a unique name;
   -  a ``Job``, containing one or more ``Task``\s described by

     - a "command" (an executable and arguments)
     - a specification of required resources, typically a number of MPI ranks

   -  a method to determine success (e.g., checking an error code or an output file)

-  A set of tools to parse / filter and query text files for test
   verification purposes
-  A ``Launcher`` object to manage launching a serial or MPI
   ``Job`` locally or via a batch/queuing system
-  A ``Harness`` object to quickly define and process a set of ``Test`` objects.

How do I use this ?
===================

We recommend starting with the :doc:`tutorial`.


Requirements and suggestions
============================

1. SciATH depends on Python. It is tested with Python 2.7 and later, and requires
   no modules outside of the standard library. Almost all systems already support this.
   (It is of course recommended to use Python 3, since Python 2 is deprecated.)

2. It is highly recommended you set the environment
   variable ``PYTHONUNBUFFERED``, e.g. ``export PYTHONUNBUFFERED``

3. Make sure you modify your ``PYTHONPATH`` environment variable to include
   this root ``sciath`` directory (containing the ``sciath`` package directory)

Topics
======

.. toctree ::
  tutorial
  concepts
  design
  api
  developer

Indices
=======

* :ref:`genindex`
* :ref:`modindex`
