#!/bin/bash

# Copyright 2014 Matt Shannon

# This file is part of SGSS.
# See `License` for details of license and warranty.

set -e
set -u
set -o pipefail

jobName="$1"
holdJidSpec="$2"
shift
shift

"$@"

echo "jid=0"
