#!/bin/bash

# Minimal sanity check of a Janeway instance

set -e

instance_root="$1"

# echo in red color
error () {
    >&2 echo $(tput setaf 1)"$@"$(tput sgr0)
}
# echo in yellow color
warn () {
    >&2 echo $(tput setaf 3)"$@"$(tput sgr0)
}
# echo in blue color
info () {
    >&2 echo $(tput setaf 4)"$@"$(tput sgr0)
}

if [[ ! -d "$instance_root/src" ]]
then
    error "Please provide the full path of a Janway instance (i.e. where the \"src\" folder is)"
    exit 1
fi

# Find and fix folders with wrong group
# =====================================
if find /home/wjs/janeway/src/files/ -type d -group www-data
then
    echo do you want to fix ?
    chown  -R :www-data
fi

# Find and fix folders with wrong permissions
# ===========================================
...
