=====================
Developer Information
=====================

Integration Branches
====================

* ``main``: stable release branch. The latest commit here should always be a tagged non-prelease version
* ``dev``: main development branch, to which pull requests should be made

Conventions
===========

Package Name
------------
Use "SciATH" as the name of the package, except where all-lowercase names are required or conventional, as in the name of the main module or the git URL.

Style
=====

Write Python 2.7.0+-compatible code. Do not assume a recent patch version of Python 2.7.
Prioritize Python 3, only using version-dependent logic when required for correctness,
not performance (e.g. one shouldn't bother using ``xrange`` instead of ``range`` in Python 2).

Conform to the `Google Python style guide <http://google.github.io/styleguide/pyguide.html>`__.
One can check and enforce conformance with `YAPF <https://github.com/google/yapf>`__, e.g. 
``yapf --style=google -d -r .`` from the root directory will show all violations, and adding
the ``-i`` flag will repair these in place.

Python code must also be clean with a recent (stock) `Pylint <https://pypi.org/project/pylint/>`__
