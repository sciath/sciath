===============
SciATH Tutorial
===============

Examples
--------

The included scripts serve as examples of key functionality.

All the commands below assume that you are in the ``examples/``
subdirectory.

The tests’ permissions are set to allow direct execution
(e.g. ``./example.py``). They may also be run
e.g. \ ``python example.py``.

Note that the tests themselves may *fail* in the following examples.
This is to demonstrate how differences from expected output are
reported, and doesn’t mean that the test harness itself isn’t working!

Basic testing of serial applications using the test harness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic functionality includes:

1. comparison with data in a file;
2. multiple tests;
3. report summary and error log files

::

   cd example1
   ./example.py           # ex1 should pass; ex2 and ex3 should fail

::

   cd example4
   ./example.py           # ex2 should pass; ex1 and ex3 should fail

Floating point comparisons can be absolute or relative.

::

   cd example9
   ./example.py           # testAbs, testRel should fail; testRelEpsilon should pass

Tests defined in separate directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   cd example2
   ./example.py           # test1 should pass; test2 should fail

Running a subset of tests
~~~~~~~~~~~~~~~~~~~~~~~~~

::

   ./example.py -l             # list all registered tests
   ./example.py -t test1       # run a single test
   ./example.py -t test1,test2 # run several tests

One may also provide a subset of tests directly in the initializer for
the test harness. Additional tests can be added with ``-t``.

::

   cd example8
   ./example.py               # test1 should pass, test1_clone should be skipped
   ./example.py -t test_clone # both tests should run and pass

Parallel tests using a PETSc code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Features:

1. test defined using an MPI parallel application;
2. test submission through a batch/queuing system

Requires the environment variables ``PETSC_DIR`` and ``PETSC_ARCH`` to
be defined.

::

   cd example3;
   python example.py      # ex2b should pass; ex2a and ex2c should fail

Defining a test which doesn’t depend on an expected output file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   cd example5
   ./example.py           # ex1 should pass; ex2-ex4 should fail

Deleting test output
~~~~~~~~~~~~~~~~~~~~

Generated test output may be deleted:

::

   cd example5
   ./example.py           # ex1 should pass; ex2-ex4 should fail
   ./example.py -p        # delete output for all tests
   ./example.py -p -t ex1 # delete output for a single test

Running tests in dedicated “sandbox” directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each test may be run in a “sandbox” directory, useful to run tests which
produce identically-named output files, or for testing applications
which may generate extra output files.

::

   cd example6
   ./example.py

You may supply the ``-s`` flag to use a sandbox directory for all tests

::

   cd example5
   ./example.py -s
   ./example.py -s -p     # remove output

Running multiple executables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``execute`` field for a ``Test`` may be a list. All executables in
the list are run in succession. Note that on batch/queueing systems,
these are all run with the same number of MPI ranks.

This example executes the same executable twice:

::

   cd example7
   python example.py      # ex1 should fail

Updating expected output
~~~~~~~~~~~~~~~~~~~~~~~~
Warning: this can overwrite your data! Use with caution.

You can use the ``-r`` flag to overwrite the expected output with the output that is
produced. For example, introduce an error into the expected file for a test
and update the output to overwrite it. Note that a backup file is created.

::

   cd example1
   python example1.py -t ex1               # ex1 should pass
   printf "kspits = 999.9" >> ex1.expected
   python example.py -t ex1                # ex1 should fail
   python example.py -t ex1 -r             # ex1 should pass and update ex1.expected
   python example.py -t ex1                # ex1 should pass
   rm ex1.expected.bak                     # remove the backup file

Tips for building tests
-----------------------

Escape characters
~~~~~~~~~~~~~~~~~

The verification process involves parsing expected output and searching
for keywords. If your output generates strings requiring escape
characters, for example the string ``"|a.b|_2"``, the keyword provided to
SciATH needs to be expressed as ``"\|a.b\|_2"``.  This is awkward so we
recommend using the regular expression utilities which provide a method
to add the backslash automatically. E.g.

::

   #!/usr/bin/env python

   import re
   keyword = re.escape("|a.b|_2")

