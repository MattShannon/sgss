#!/usr/bin/python

"""Submits jobs to a grid, submitting dependent jobs first.

Only submits jobs which have not already been completed or submitted.
"""

# Copyright 2014 Matt Shannon

# This file is part of SGSS.
# See `License` for details of license and warranty.

import os
import sys
import subprocess

def rawSubmit(binDir, jobDir, gridName, inputJids):
    jobNameFile = os.path.join(jobDir, 'job_spec', 'name')
    with open(jobNameFile) as f:
        jobName = f.read().rstrip('\n')

    submitArgs = [
        os.path.join(binDir, 'raw-submit-%s.sh' % gridName),
        jobName,
        ','.join(inputJids),
        os.path.join(binDir, 'run_job.py'),
        jobDir
    ]

    os.mkdir(os.path.join(jobDir, 'job_live'))

    try:
        jidString = subprocess.check_output(submitArgs)
    except:
        # if job submission failed then this empty directory should be removed
        os.rmdir(os.path.join(jobDir, 'job_live'))
        raise

    assert jidString[:4] == 'jid='
    jid = jidString[4:].rstrip('\n')

    print 'job %s submitted to %s with jid %s' % (jobDir, gridName, jid)

    with open(os.path.join(jobDir, 'job_live', 'grid'), 'w') as f:
        f.write('%s\n' % gridName)
    with open(os.path.join(jobDir, 'job_live', 'jid'), 'w') as f:
        f.write('%s\n' % jid)

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

def hasBeenSubmitted(jobDir):
    jobLiveDir = os.path.join(jobDir, 'job_live')
    return os.path.exists(jobLiveDir)

def isDone(jobDir):
    doneFile = os.path.join(jobDir, 'job_live', 'done')
    return os.path.exists(doneFile)

def getGridName(jobDir):
    gridNameFile = os.path.join(jobDir, 'job_live', 'grid')
    try:
        with open(gridNameFile) as f:
            gridName = f.read().rstrip('\n')
    except IOError:
        gridName = None

    return gridName

def getJid(jobDir):
    jidFile = os.path.join(jobDir, 'job_live', 'jid')
    try:
        with open(jidFile) as f:
            jid = f.read().rstrip('\n')
    except IOError:
        jid = None

    return jid

def getLiveJidSubmittingIfNece(binDir, jobDir, gridName):
    if isDone(jobDir):
        return None
    elif hasBeenSubmitted(jobDir):
        submittedGridName = getGridName(jobDir)
        assert submittedGridName is not None
        if submittedGridName != gridName:
            raise RuntimeError(
                'job %s was previously submitted on grid %s,'
                ' so has no valid jid on grid %s' %
                (jobDir, submittedGridName, gridName)
            )

        jid = getJid(jobDir)
        assert jid is not None
        return jid
    else:
        jobInputs, nonJobInputs = getInputs(jobDir)

        inputJids = []
        for inputDir in jobInputs:
            inputJid = getLiveJidSubmittingIfNece(binDir, inputDir, gridName)
            if inputJid is not None:
                inputJids.append(inputJid)

        for inputDir in nonJobInputs:
            if not os.path.exists(inputDir):
                raise RuntimeError(
                    'dir %s is required for job %s but was not found' %
                    (inputDir, jobDir)
                )

        rawSubmit(binDir, jobDir, gridName, inputJids)

        jid = getJid(jobDir)
        assert jid is not None
        return jid

def main(argv):
    gridName = argv[1]
    jobDirs = argv[2:]

    binDir = os.path.dirname(argv[0])

    for jobDir in jobDirs:
        if isDone(jobDir) or hasBeenSubmitted(jobDir):
            pass
        else:
            getLiveJidSubmittingIfNece(binDir, jobDir, gridName)

if __name__ == '__main__':
    main(sys.argv)
