Simple grid submission system (SGSS)
====================================

This software is designed to manage "grid jobs", that is jobs which will be
submitted to a compute grid.
It provides a simple set of scripts to create jobs and to submit them to a
grid while managing the dependencies between jobs.
It provides a basic caching mechanism to ensure that jobs are not run
unnecessarily, but otherwise tries to be as unobtrusive as possible.
Its goal is to make submitting a graph of grid jobs a highly automated process,
while allowing substantial manual intervention when desired.

Overview
--------

The software is based on a simple scheme for organizing directories.
Each grid job has a directory on disk which contains the information needed to
run the job and where the output produced by the job is eventually stored.
Specifically the command to be run, the dependencies of the job and the job
name are stored in the ``job_spec`` subdirectory.

Creating a job directory with the required structure is made easier using the
``create_job.py`` script.
This allows the job's name, the job's dependencies and the command to be run to
be specified in a concise way, often by simply adding annotations to the
command which would have run the same computation locally.
However the required directory structure is simple enough, and could easily be
produced by your own scripts if desired.

Submitting a job is done using the ``rsubmit.py`` script.
This recursively submits any jobs which the current job depends on and which
have not previously been submitted, then submits the current job.
It calls a user-defined script ``raw-submit-<GRIDNAME>.sh`` to do the actual
submission, since this process is dependent on the grid used.
If a job the current job depends on has previously been submitted but has not
yet completed then the raw submission system is made aware of this dependency.

License
-------

Please see the file ``License`` for details of the license and warranty for SGSS.

Installation
------------

The source code is hosted in the
`SGSS github repository <https://github.com/MattShannon/sgss>`_.
To obtain the latest source code using git::

    git clone git://github.com/MattShannon/sgss.git

SGSS has the following dependencies:

- python

To set-up this directory:

- add raw submission scripts named ``raw-submit-<GRIDNAME>.sh`` for any grids
  you wish to be able to submit to, e.g. ``raw-submit-divf.sh`` for submission
  to a grid named ``divf``.
  Examples of raw submission scripts can be found in the ``examples``
  subdirectory.

The scripts in this directory can then be called directly; there is no need to
"install" them as such.

More details
------------

SGSS uses a simple scheme to indicate dependencies.
Each dependency is simply a directory.
If the dependency directory contains a ``job_spec`` subdirectory then the
dependency is assumed to be a managed job, and its completion status is taken
into account when the original job is submitted.
Otherwise the dependency directory is assumed to be a fixed directory.
This allows an existing set of directories or existing workflow to be converted
gradually or partially to the SGSS structure.
For example, a directory which was previously produced manually and which other
jobs depend on can be converted to a managed job at some point in the future.

Bugs
----

Please use the `issue tracker <https://github.com/MattShannon/sgss/issues>`_
to submit bug reports.

Contact
-------

The author of SGSS is `Matt Shannon <mailto:matt.shannon@cantab.net>`_.
