#!/usr/bin/env bash

set -e

# Upgrade dependencies in the cli folder
echo "Upgrading dependencies in cli folder..."
cd cli

VENV_PYTHON="../app/.venv/bin/python3"
if [ -x "$VENV_PYTHON" ]; then
    "$VENV_PYTHON" update_dependencies.py
else
    echo "Virtual environment Python not found for cli. Skipping."
fi

cd ..

# Upgrade dependencies in the app folder
echo "Upgrading dependencies in app folder..."
cd app

VENV_PYTHON="./.venv/bin/python3"
if [ -x "$VENV_PYTHON" ]; then
    "$VENV_PYTHON" update_dependencies.py
else
    echo "Virtual environment Python not found for app. Skipping."
fi

cd ..

# Upgrade dependencies in the ui folder
echo "Upgrading dependencies in ui folder..."
cd ui

if [ -f "update_packages.js" ]; then
    if command -v node &> /dev/null; then
        node update_packages.js
    else
        echo "Node.js not found. Skipping node update."
    fi
elif command -v yarn &> /dev/null; then
    yarn update
else
    echo "Neither update_packages.js nor yarn found for ui. Skipping."
fi

cd ..

echo "Upgrade process completed."
