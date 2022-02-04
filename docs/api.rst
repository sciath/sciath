=============
API Reference
=============

The SciATH API is based on a few key abstractions:

- A :class:`Test` consisting of:

   -  A unique name
   -  A :class:`Job`, containing one or more :class:`Task`\s, which consist of a command and a set of required resources (typically, a number of MPI ranks)
   -  An implementation of :class:`Verifier` to ascertain test success (e.g. by comparing output to a reference or by checking an exit code)

-  A :class:`Launcher` to manage launching serial or MPI
   :class:`Job`\s locally or via a batch/queuing system
-  A :class:`Harness` object to interact with a user by managing a set of :class:`Test` objects and a :class:`Launcher`


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
