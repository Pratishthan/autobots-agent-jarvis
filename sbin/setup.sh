#!/bin/bash

# Get the project name from the command line
PROJECT_NAME="$1"

if [ -z "$PROJECT_NAME" ]; then
    echo "Error: Project name is required"
    exit 1
fi

rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate

poetry lock
make install
make install-dev
make install-hooks
make pre-commit

.venv/bin/python sbin/scaffold.py "$PROJECT_NAME"
