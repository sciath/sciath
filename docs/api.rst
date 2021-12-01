=============
API Reference
=============

The SciATH API is based on a few key abstractions:

- A :class:`Test` consisting of:

   -  a unique name;
   -  a :class:`Job`, containing one or more :class:`Task`\s, which consist of a command and a set of required resources (typically, a number of MPI ranks).
   -  a method to determine success (e.g., checking an error code or an output file)

-  A :class:`Launcher` to manage launching a serial or MPI
   :class:`Job`\s locally or via a batch/queuing system
-  A :class:`Harness` object to quickly define and process a set of :class:`Test` objects.
-  A set of :class:`Verifier` implementations to ascertain test success (e.g. by comparing output to a refernce).


Task
====
.. automodule:: sciath.task
  :members:
  :undoc-members:

Job
===
.. automodule:: sciath.job
  :members:
  :undoc-members:

Launcher
========
.. automodule:: sciath.launcher
  :members:
  :undoc-members:

Test
====

.. automodule:: sciath.test
  :members:
  :undoc-members:

Harness
========

.. automodule:: sciath.harness
  :members:
  :undoc-members:

Verifier
========

.. automodule:: sciath.verifier
  :members:
  :undoc-members:

.. automodule:: sciath.verifier_line
  :members:
  :undoc-members:
