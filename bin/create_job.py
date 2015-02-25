#!/usr/bin/python

"""Creates the directory structure for a simple job.

Often a job will require special job-specific code and so the contents of the
job_spec subdirectory for that job will need to be created by a custom script.
However sometimes a job is simple enough that it can be created with this
general-purpose script instead.

The conventional way to specify the information required to create the job is
via command-line flags.
For example:

    bin/create_job.py -I foo -N get_bar.py -J bar python get_bar.py foo bar

It is also possible to specify this information using annotations.
For example:

    bin/create_job.py python @N get_bar.py @I foo @J bar

This is more concise and less error-prone, but uses unconventional syntax.
The job name and job directory specified using command-line flags take
precedence over values specified using annotations.
"""

# Copyright 2014 Matt Shannon

# This file is part of SGSS.
# See `License` for details of license and warranty.

import os
import sys
import argparse

def isSubDir(subPath, path):
    """Checks if one directory is a subdirectory of another."""
    realPath = os.path.realpath(os.path.join(path, ''))
    realSubPath = os.path.realpath(subPath)
    # (FIXME : is this really sufficient in all cases?)
    return realSubPath.startswith(realPath)

def getAnnedArgs(args, validAnns=set(('@I', '@i', '@N', '@J'))):
    """Parses an argument list which may contain annotations."""
    annedArgs = []
    annListCurr = []
    for arg in args:
        if arg in validAnns:
            annListCurr.append(arg)
        else:
            annedArgs.append((annListCurr, arg))
            annListCurr = []
    assert not annListCurr

    return annedArgs

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument(
        '-I', '--in', dest='dirIns', metavar='DIR', action='append',
        help='specify an input directory (repeatable)'
    )
    parser.add_argument(
        '-i', '--in_file', dest='fileIns', metavar='FILE', action='append',
        help=('specify an input file, which will be converted to a directory'
              ' (repeatable)')
    )
    parser.add_argument(
        '-N', '--name', dest='jobName', metavar='NAME',
        help='job name'
    )
    parser.add_argument(
        '-J', '--job_dir', dest='jobDir', metavar='JOBDIR',
        help='job directory for output (should not exist)'
    )
    parser.add_argument(
        '--job_sub_dir', dest='jobSubDirRels', metavar='DIR', action='append',
        help=('specify a relative subdirectory of the job dir (e.g. "labels")'
              ' (the subdirectory will be created immediately with a job_refs'
              ' file to indicate that this job created it;'
              ' this allows other jobs which depend on this subdirectory to'
              ' evaluate their dependencies correctly after this job has been'
              ' created but before it has been run)'
              ' (repeatable)')
    )
    parser.add_argument(
        '--job_sub_dir_range', dest='jobSubDirRelRanges',
        metavar=('DIRPAT', 'START', 'END'), nargs=3, action='append',
        help=('specify a range of relative subdirectories of the job dir, one'
              ' for each number between START and END inclusive'
              ' (see --job_sub_dir) (repeatable)')
    )
    parser.add_argument(
        'args', metavar='ARG', nargs=argparse.REMAINDER,
        help='argument list for the command to run'
    )
    args = parser.parse_args(argv[1:])

    dirIns = []
    if args.dirIns is not None:
        for dirIn in args.dirIns:
            dirIns.append(dirIn)
    if args.fileIns is not None:
        for fileIn in args.fileIns:
            dirIns.append(os.path.dirname(fileIn))

    jobName = args.jobName
    jobDir = args.jobDir

    jobSubDirRels = []
    if args.jobSubDirRels is not None:
        for jobSubDirRel in args.jobSubDirRels:
            jobSubDirRels.append(jobSubDirRel)
    if args.jobSubDirRelRanges is not None:
        for jobSubDirRelPat, startIndexStr, endIndexStr in args.jobSubDirRelRanges:
            startIndex = int(startIndexStr)
            endIndex = int(endIndexStr)
            for index in range(startIndex, endIndex + 1):
                jobSubDirRels.append(jobSubDirRelPat % index)

    cmdArgs = []
    for annList, cmdArg in getAnnedArgs(args.args):
        for ann in annList:
            if ann == '@I':
                dirIns.append(cmdArg)
            elif ann == '@i':
                dirIns.append(os.path.dirname(cmdArg))
            elif ann == '@N' and jobName is None:
                jobName = cmdArg
            elif ann == '@J' and jobDir is None:
                jobDir = cmdArg
        cmdArgs.append(cmdArg)

    jobName = os.path.basename(jobName)

    assert jobName is not None
    assert os.path.sep not in jobName
    assert jobDir is not None

    jobSubDirs = [
        os.path.join(jobDir, jobSubDirRel)
        for jobSubDirRel in jobSubDirRels
    ]

    for jobSubDir in jobSubDirs:
        if not isSubDir(jobSubDir, jobDir):
            raise RuntimeError(
                '%s does not appear to be a valid subdirectory of %s' %
                (jobSubDir, jobDir)
            )

    os.mkdir(jobDir)
    jobSpecDir = os.path.join(jobDir, 'job_spec')
    os.mkdir(jobSpecDir)
    with open(os.path.join(jobSpecDir, 'inputs'), 'w') as f:
        for dirIn in dirIns:
            f.write('%s\n' % dirIn)
    with open(os.path.join(jobSpecDir, 'name'), 'w') as f:
        f.write('%s\n' % jobName)
    with open(os.path.join(jobSpecDir, 'cmd'), 'w') as f:
        for cmdArg in cmdArgs:
            f.write('%s\n' % cmdArg)
    for jobSubDir in jobSubDirs:
        os.makedirs(jobSubDir)
        with open(os.path.join(jobSubDir, 'job_refs'), 'w') as f:
            f.write(jobDir + '\n')
    print '%s created' % jobDir

if __name__ == '__main__':
    main(sys.argv)
