#!/bin/bash

# Copyright 2014 Matt Shannon

# This file is part of SGSS.
# See `License` for details of license and warranty.

set -e
set -u
set -o pipefail

# e.g. "traj_trainer"
jobName="$1"
# e.g. "." or "238479,981273"
holdJidSpec="$2"
shift
shift

binDir="$(dirname "$0")"

if [[ "$holdJidSpec" == "" || "$holdJidSpec" == "." ]]; then
    qsubRes="$(qsub -b y -cwd -j y -o LOG -N "$jobName" "$binDir"/halt_help.sh "$@")"
else
    qsubRes="$(qsub -b y -cwd -j y -o LOG -hold_jid "$holdJidSpec" -N "$jobName" "$binDir"/halt_help.sh "$@")"
fi

jid="$(echo "$qsubRes" | sed -r -n 's/^Your job.* ([0-9]+) \("(.*)"\) has been submitted$/\1/p')"

if [[ "$jid" == "" ]]; then
    echo "could not parse qsub output: $qsubRes" 1>&2
    exit 1
fi

echo "jid=$jid"
