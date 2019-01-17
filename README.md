# pyTestHarness
## The Idea

Testing code should be easy. The functionality required to launch, parse and perform verification should be light-weight and simple to migrate into existing projects. pyTestHarness (pth for short) supports testing of sequential and MPI-parallel applications. Tests can be performed locally, or submitted via a batch queuing system (e.g. PBS, LSF, Slurm or LoadLeveler).

## Key Concepts

pyTestHarness provides:

* An object to define a test. A "test" consists of:
    * a unique textual name;
    * one or more executables;
    * a number of MPI ranks (1 for serial execution)
    * a text file containing the expected output;
    * a method to compare any output generated by the test (e.g. from stdout or another output file)
* A set of tools to parse / filter and query text files for test verification purposes
* A "harness" object to quickly define and process a set of tests
* Internally, a "launcher" object to manage launching a serial or MPI job locally or via a batch queuing system

## How do I use this ?

1. pyTestHarness depends on Python 3 (or Python 2.4+) and numpy

2. When using Python 3, it is highly recommended you set the environment variable PYTHONUNBUFFERED, e.g.
```export PYTHONUNBUFFERED```

3. Make sure you modify your PYTHONPATH environment variable to include the directory ```${PWD}/lib``` (relative to this README file)

## Examples

The included `pth_exampleN.py` scripts serve as examples of key functionality.

The tests' permissions are set to allow direct execution (e.g. `./pth_example1.py`). They may also be run e.g. `python pth_example1.py`.

Note that the tests themselves may _fail_ in the following examples. This is to
demonstrate how differences from expected output are reported, and doesn't mean
that the test harness itself isn't working!

### Basic testing of serial applications using the test harness ###

Basic functionality includes:

1. comparison with data in a file;
2. multiple tests;
3. report summary and error log files

#### Example 1

    cd example1
    ./pth_example1.py           # ex1 should pass; ex2 and ex3 should fail

#### Example 4

    cd example4
    ./pth_example4.py           # ex2 should pass; ex1 and ex3 should fail

#### Example 9

Floating point comparisons can be absolute or relative.

    cd example9
    ./pth_example9.py           # testAbs should fail; testRel should pass

### Tests defined in separate directories
#### Example 2

    cd example2
    ./pth_example2.py           # test1 should pass; test2 should fail

### Running a subset of tests

    ./pth_example2.p -l         # list all registered tests
    ./pth_example2.py -t test1  # run a single test
                                # can select multiple tests with -t test1,test2

#### Example 8
One may also provide a subset of tests directly in the initializer for the test
harness. Additional tests can be added with `-t` as above.

    cd example8
    ./pth_example8.py               # test1 should pass, test1_clone should be skipped
    ./pth_example8.py -t test_clone # both tests should run and pass

### Parallel tests using a PETSc code

#### Example 3
Features:

1. test defined using an MPI parallel application;
2. test submission through a batch/queuing system

Requires the environment variables ```PETSC_DIR``` and ```PETSC_ARCH``` to be defined.

    cd example3;
    python pth_example3.py      # ex2b should pass; ex2a and ex2c should fail

### Defining a test which doesn't depend on an expected output file

#### Example 5

    cd example5
    ./pth_example5.py           # ex1 should pass; ex2-ex4 should fail

### Deleting test output
Generated test output may be deleted:

    cd example5
    ./pth_example5.py           # ex1 should pass; ex2-ex4 should fail
    ./pth_example5.ph -p        # delete output for all tests
    ./pth_example5.ph -p -t ex1 # delete output for a single test

### Running tests in dedicated "sandbox" directories

#### Example 6
Each test may be run in a "sandbox" directory, useful to run tests which produce identically-named output files, or for testing applications which may generate extra output files.

    cd example6
    ./pth_example6.py

You may supply the `-s` flag to use a sandbox directory for all tests

    cd example5
    ./pth_example5.py -s
    ./pth_example5.py -s -p     # remove output

### Running multiple executables

#### Example 7
The `execute` field for a `Test` may be a list.
All executables in the list are run in succession. Note that on batch/queueing
systems, these are all run with the same number of MPI ranks.

This example executes the same executable twice:

    cd example7
    python pth_example7.py      # ex1 should fail

## Tips for building tests

### Escape characters
The verification process involves parsing expected output and searching for keywords. If your output generates strings requiring escape characters, for example the string "|a.b|_2", the keyword provided to pyTestHarness needs to be expressed as "\|a.b\|\_2". This is awkward so we recommend using the regular expression utilities which provide a method to add the backslash automatically. E.g.

```
#!/usr/bin/env python

import re
keyword = re.escape("|a.b|_2")
```
