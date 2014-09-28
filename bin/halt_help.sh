#!/bin/bash

# Copyright 2014 Matt Shannon

# This file is part of SGSS.
# See `License` for details of license and warranty.

"$@"
exitCode="$?"
if [[ "$exitCode" == "0" ]]; then
    exit 0
else
    echo "job failed; using exit code 100 (instead of $exitCode) to prevent dependent job execution"
    echo "args:"
    echo
    echo "$@"
    exit 100
fi
