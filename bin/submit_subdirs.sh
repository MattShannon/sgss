#!/bin/bash

# Copyright 2014 Matt Shannon

# This file is part of SGSS.
# See `License` for details of license and warranty.

set -e
set -u
set -o pipefail

gridName="$1"
shift

binDir="$(dirname "$0")"

for baseExptDir in "$@"; do
    find "$baseExptDir" -type d -name 'job_spec' |
        sort |
        sed -r 's%/job_spec$%%' |
        xargs -d '\n' "$binDir"/rsubmit.py "$gridName"
done
