#!/bin/bash

# Copyright 2014 Matt Shannon

# This file is part of SGSS.
# See `License` for details of license and warranty.

set -e
set -u
set -o pipefail

for baseExptDir in "$@"; do
    if [[ "$(find "$baseExptDir" -name 'jid' | wc -l)" == "0" ]]; then
        rm -rf "$baseExptDir"
    else
        find "$baseExptDir" -name 'jid' | xargs cat | xargs qdel && rm -rf "$baseExptDir"
    fi
done
