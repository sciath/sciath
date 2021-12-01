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


How do I use it ?
=================

We recommend starting with the :doc:`tutorial`.

SciATH can be run as a Python module, providing a convenient command-line interface to read a set of tests from a simple input file and run them.

This logic is implemented with the :doc:`api`, which advanced users may be interested in.


Requirements and suggestions
----------------------------

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
