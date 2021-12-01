.. NOTE: Any output from SciATH itself which is included in this file must be from a file which is the expected output of a SciATH self-test. Otherwise, it will inevitably go out of date.

.. highlight:: none

===============
SciATH Tutorial
===============

SciATH is designed to test programs
written in any language, by working at the level of executables and expected
output.

This tutorial uses simple executables
which should work from all POSIX-compatible shells.

In typical usage, one would of course run scientific application executables (or scripts), to test them.

It may also help to read :any:`concepts`.

Installing SciATH
=================

Clone SciATH from the upstream Git repository,
and make sure it is on your Python path, e.g.

.. code-block:: bash

    cd $HOME
    git clone https://github.com/sciath/sciath
    cd sciath
    export PYTHONPATH=$PYTHONPATH:$HOME/sciath

You need a working installation of Python. Test that the above worked by running ``python`` and then ``import sciath`` - if this command succeeds without error, the the ``sciath`` module can be used as expected.

SciATH is a Python module which can be run as an executable.
This is achieved by using the syntax ``python -m sciath``,
once SciATH has been successfully installed.

The simplest test
=================

The simplest test is to run an executable and check the exit code. If the code
is 0, we declare success. Otherwise, failure.

Create a scratch directory to work in

.. code-block:: bash

   mkdir scratch
   cd scratch

Create a file, ``tutorial1.yml``, with the following content

.. literalinclude:: _static/tutorial/tutorial1.yml
    :language: YAML

The file uses a subset of the `YAML <https://yaml.org>`__ format.
Blank lines and anything after a ``#`` are ignored.

Execute the SciATH module to run the test

.. code-block:: bash

    python -m sciath tutorial1.yml

You will be prompted to describe information about how to run jobs on your system.
This tutorial can be used on a local machine or a cluster.
To begin with, you may enter ``none`` for the first two questions.

This information is stored in a file called ``SciATHBatchQueuingSystem.conf``.

Once you've defined this information, you'll see output like the following

.. literalinclude:: _static/tutorial/tutorial1_output.txt

Note that you are given the full path for the "sandbox" from which your command is run.

Your output will contain colors, by default. If you don't want the colors (or see strange codes like ``^[[35m``), use the ``--no-colors`` option.

SciATH accepts other command line arguments. Use the ``-h`` argument to see them.

.. code-block:: bash

   python -m sciath -h

To (re-)verify your test results, without re-running the tests, use ``-v``:

.. code-block:: bash

   python -m sciath tutorial1.yml -v

Take a look in the directory that was created, called ``first_output``.
You will see several files and directories, including

  * ``first.exitcode`` which contains the exitcode (``0``)
  * ``first.stdout`` which contains ``Hello, World!``
  * ``first.stderr``, which should be an empty file
  * ``sandbox``, which should be an empty directory


Running a subset of Tests
=========================

Create a new file, ``tutorial.yml``, with the following contents. Don't worry that you don't understand everything yet. Just note that it contains several tests, each with a unique name.

.. literalinclude:: _static/tutorial/tutorial.yml
  :language: YAML


You can use the ``-l`` command line option to list all available tests.

.. code-block:: bash

  python -m sciath tutorial.yml -l

You can run one or more of the tests, by name, with the ``-t`` option. For example, run

.. code-block:: bash

    python -m sciath tutorial.yml -t first

to generate output

.. literalinclude:: _static/tutorial/first_output.txt
  :language: none

or

.. code-block:: bash

    python -m sciath tutorial.yml -t first,second

to generate output

.. literalinclude:: _static/tutorial/first_and_second_output.txt

A Failing Test
==============

The test ``failing`` attempts to run ``grep`` on a non-existent file,
which prints an error message to stderr and returns a non-zero exit code
(``2`` on BSD and GNU systems).
It is defined in the input file with

.. literalinclude:: _static/tutorial/tutorial.yml
  :language: YAML
  :start-at: - name: failing
  :end-at: type:

Run it with

.. code-block:: bash

    python -m sciath tutorial.yml -t failing

To produce output

.. literalinclude:: _static/tutorial/failing_output.txt

Note that you are given information about the location of the output
files at the end of the report for the failing test.
You can copy-paste this line to see the error message:

.. literalinclude:: _static/tutorial/failing_output.txt
  :start-at: check non-empty stderr file
  :lines: 1-2

A Comparison-Based Test
=======================

The test ``text_diff`` compares output to stdout against a reference file.

It is defined in the input file with

.. literalinclude:: _static/tutorial/tutorial.yml
  :language: YAML
  :start-at: - name: text_diff
  :end-at: expected:

Note that ``type:`` is not specified, so the default is used. This is a text-based comparison.

Run the test with

.. code-block:: bash

    python -m sciath tutorial.yml -t text_diff

It will fail because the expected file is not found:

.. literalinclude:: _static/tutorial/text_diff_fail_output.txt

Note that the full path where SciATH expected the file is printed. It looked for it in the same location as ``tutorial.yml``.

You can generate the expected file with the ``-u`` flag. Note that this will **overwrite** this file, if it already exists!

.. code-block:: bash

    python -m sciath tutorial.yml -t text_diff -u

You will now notice that the expected file, ``text_diff.expected`` has appeared and now the test will pass if you re-run

.. code-block:: bash

    python -m sciath tutorial.yml -t text_diff

Edit the newly created file to make the test fail, for example changing it to

.. literalinclude:: _static/tutorial/text_diff.expected.wrong

and examine the output again.

Additional features
===================

Additional features not (yet) included in this tutorial include

* Numerical tests
* MPI-parallel tests
* Tests with multiple commands
* Using replacements in the input file (``HERE`` and environment variables)
