#!/usr/bin/python

"""Wrapper to run a job.

Checks inputs before running job, and and touches done file if job exits
normally.
"""

# Copyright 2014 Matt Shannon

# This file is part of SGSS.
# See `License` for details of license and warranty.

import os
import sys
import subprocess

def artToJobDirs(artDir, allowNone=True):
    """Returns the job(s) which generated a given artifact.

    An artifact is a file or directory.
    References (specified by a job_refs file) are expanded recursively.
    """
    if os.path.exists(os.path.join(artDir, 'job_spec')):
        return [artDir]
    elif os.path.exists(os.path.join(artDir ,'job_refs')):
        jobDirs = []
        for line in open(os.path.join(artDir, 'job_refs')):
            refedArtDir = line.rstrip('\n')
            jobDirs.extend(artToJobDirs(refedArtDir, allowNone=False))
        return jobDirs
    else:
        if allowNone:
            return None
        else:
            raise RuntimeError('job dir for %s could not be found' % artDir)

def getInputs(jobDir):
    jobInputs = []
    nonJobInputs = []
    for line in open(os.path.join(jobDir, 'job_spec', 'inputs')):
        inputDir = line.rstrip('\n')
        jobDirs = artToJobDirs(inputDir)
        if jobDirs is None:
            nonJobInputs.append(inputDir)
        else:
            jobInputs.extend(jobDirs)

    return jobInputs, nonJobInputs

def isDone(jobDir):
    doneFile = os.path.join(jobDir, 'job_live', 'done')
    return os.path.exists(doneFile)

def checkInputs(jobDir):
    jobInputs, nonJobInputs = getInputs(jobDir)

    for inputDir in jobInputs:
        if not isDone(inputDir):
            raise RuntimeError(
                'job %s is required for job %s but is not done' %
                (inputDir, jobDir)
            )

    for inputDir in nonJobInputs:
        if not os.path.exists(inputDir):
            raise RuntimeError(
                'dir %s is required for job %s but was not found' %
                (inputDir, jobDir)
            )

def main(argv):
    jobDir = argv[1]

    if isDone(jobDir):
        raise RuntimeError('job %s is already done' % jobDir)

    checkInputs(jobDir)

    cmdFile = os.path.join(jobDir, 'job_spec', 'cmd')
    cmdArgs = []
    for line in open(cmdFile):
        cmdArgs.append(line.rstrip('\n'))

    subprocess.check_call(cmdArgs)

    if not os.path.exists(os.path.join(jobDir, 'job_live')):
        os.mkdir(os.path.join(jobDir, 'job_live'))
    doneFile = os.path.join(jobDir, 'job_live', 'done')
    with open(doneFile, 'w') as f:
        pass

if __name__ == '__main__':
    main(sys.argv)
