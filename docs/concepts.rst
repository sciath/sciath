Helpful concepts for SciATH users
=================================

It's assumed that you know how to run your code from a "unix-style" terminal.
Here, we review important concepts which should hopefully make it easier to work
with SciATH.

.. _sec_paths:

Absolute and relative paths
---------------------------

`Paths <https://en.wikipedia.org/wiki/Path_(computing)>`__ describe locations in a file system. They are usually in the form of a series of directories, separated by slashes, and may end with a non-directory file.

Locations in file systems can be specified with respect to a global `root <https://en.wikipedia.org/wiki/Root_directory>`__, usually called `/`. Paths starting with this global root are called "absolute", and uniquely identify files (or directories). Paths which begin with a file or directory name (not the root) are "relative" and which file or directory they refer to depends on  a "working" or "current" directory.  This is context-dependent, and so can lead to confusion.

**SciATH prefers to use absolute paths** wherever possible. These are longer and create visual clutter, but they are unambiguous and thus hopefully make it easier to debug test failures.

Stdout and Stderr
-----------------

These are two of the `standard streams <https://en.wikipedia.org/wiki/Standard_streams>`__ defined by the `POSIX standard <https://en.wikipedia.org/wiki/POSIX>`__. Each is associated with a number.

* stdout (``1``) is where "normal" output is sent, to be printed to the screen by default.
* stderr (``2``) is where "error" output is sent. It is also printed to the screen by default.

However, since these are two separate streams, they can be independently `redirected <https://en.wikipedia.org/wiki/Redirection_(computing)>`__.

By default, **SciATH directs stdout and stderr to separate files**. This may be confusing to  users who are used to examining terminal output, where stdout and stderr are mixed together.

The motivation to separate the stdout and stderr streams is that on large parallel clusters, errors can frequently result in every (MPI) rank printing to stderr, in non-deterministic order. This can create a huge and/or hard-to-read output file.
