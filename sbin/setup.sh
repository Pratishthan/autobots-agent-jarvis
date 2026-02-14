#!/bin/bash

# Get the project name from the command line
PROJECT_NAME="$1"

if [ -z "$PROJECT_NAME" ]; then
    echo "Error: Project name is required"
    exit 1
fi

echo "Cleaning up existing virtual environment..."
rm -rf .venv

echo "Setting up virtual environment..."
python3.12 -m venv .venv
source .venv/bin/activate

echo "Refreshing Poetry lock file..."
poetry lock

echo "Installing dependencies..."
make install
make install-dev
make install-hooks

echo "Running quality checks..."
make pre-commit

echo "Scaffolding project structure... for $PROJECT_NAME"
.venv/bin/python sbin/scaffold.py "$PROJECT_NAME"

echo "Running Poetry lock to update $PROJECT_NAME"
poetry lock

echo "Setup complete for project: $PROJECT_NAME"
