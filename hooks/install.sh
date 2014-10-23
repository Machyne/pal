#!/bin/bash
# Usage: <In pal/> "./hooks/install.sh"

if ! [ -e .git ]; then
    echo "Please run this from the project root"
    exit 1
fi

cd .git/hooks
for i in pre-commit post-checkout; do
    #remove existing and replace it with a symlink to the one in /tools/
    rm -fv $i
    ln -sv ../../hooks/$i
done
