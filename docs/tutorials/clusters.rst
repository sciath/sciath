=======================
SciATH Cluster Tutorial
=======================

It's useful to be able to test scientific codes quickly
on new or upgraded clusters.

SciATH is designed to run on any cluster with Python 2.7 or later,
which covers the vast majority of those in current use.

Cluster for testing
===================

FIXME: big problem here is how to have something that users can use locally,
or somehow otherwise access. LPBS is what I want, but it's old and requires Python 2
and doesn't play with tmux. That still might be the thing to use, if I fork it and
update it, but that's a looot of work just for a tutorial.

Installing SciATH
=================

If you have access to the ``git`` executable on your cluster, you can use it
to obtain SciATH. If not, you clone SciATH to your local machine and transfer the directory to the cluster
as you would any other directory.

Choose a directory on your local machine to represent the cluster's home
or scratch directory (where you would typically run jobs from), and use
``scp`` (or ``rsync`` or whatever other method you use to transfer files)

.. code-block:: bash

    git clone https://github.com/sciath/sciath
    mkdir cluster_home
    scp -r sciath/ cluster_home/sciath/
    cd cluster_home


Configuration
=============



Modifying the template
=======================

FIXME: this might require real work, in the sense that we should split out
a list of all the things which can be find/replaced, and include that directly here
(say just a list, with comments describing).


Running and Verifying
=====================

The main difference between using SciATH locally and using it with
batch system is that SciATH does not wait for all jobs to run. Rather,
they are submitted to the batch system, where the user can monitor their
progress as they would any other job, and once they are completed,
SciATH is re-run to verify the results.


