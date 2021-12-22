==============================
SciATH Advanced Input Tutorial
==============================

This tutorials continues from the :doc:`introduction`,
highlighting additional features which can be controlled from the input file.

Create a file, ``tutorial2.yml``, with the following contents

.. literalinclude:: /_static/tutorial/tutorial2.yml
  :language: YAML


More on SciATH commands
=======================

Note that a "command" is interpreted quite strictly in the input file: it is a sequence of whitespace-separated terms. The first is the executable and the rest are arguments. Arguments with spaces in them need to be quoted. Strings that you probably think of as "commands" for your shell may not work as expected. For instance, consider

TODO: don't hard code the below - use tutorial2.yml

.. code-block:: bash

    echo "Hello, World!" > output.txt; cat output.txt  # comment

In your shell, this would probably produce a file ``output.txt``, print its contents to the screen, and ignore ``# comment``. However, for SciATH, the line above is equivalent to

.. code-block:: bash

    echo "Hello, World!" ">" "output.txt;" "cat" "output.txt"  "#" "comment"

and would just print this to your screen:

.. code-block:: console

   Hello, World! > output.txt; cat output.txt  # comment

One solution to this problem is to pass your intended command to be executed by a shell, e.g.

.. code-block:: bash

    sh -c "echo \"Hello, World!\" > output.txt; cat output.txt  # comment"


Multiple commands
=================

A test frequently involves multiple commands. One could use the workaround with ``sh -c`` as above to allow one to execute multiple commands, but SciATH provides a simpler way.

TODO insert from tutorial2.yml

There may also be referred to as "tasks", since internally the relevant object is :class:`Task`, which contains not only the command but the resources required to run it.

TODO insert from tutorial2.yml

See the :doc:`mpi` for information on how each command can use different numbers of resources, which would be useful, instance, for running a test using MPI and then a post-processing script.


Replacements
============

The :ref:`previous example on comparison-based testing <_sec_comparison_test>` may have
seemed very unrealistic, as it used a comparison file in the working directory,
when logically one would want to store a comparision file in a location relative
to the input file.

SciATH will replace ``HERE`` with the location of the input file.

TODO insert from tutorial2.yml

One may also capture and replace values of `UNIX-style environment variables <https://en.wikipedia.org/wiki/Environment_variable#Unix>`__.

TODO insert from tutorial2.yml
