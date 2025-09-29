#!/bin/bash

set -e

## This script installs the necessary development dependencies for the Haiven project. You should run this script in the root directory of the project.
## Review the following PRE-REQUISITES section before running this script:
## PRE-REQUISITES BEGIN
## check if python@3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "Python@3.12 is not installed. Installing Python@3.12 using Homebrew..."
    brew install python@3.12
fi

## check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "Pipx is not installed. Installing Pipx using Python@3.12..."
    python3.12 -m pip install --user pipx
    python3.12 -m pipx ensurepath

fi

## check if nvm is installed
if ! command -v nvm &> /dev/null; then
    echo "Nvm is not installed. Installing Nvm using Homebrew..."
    brew install nvm
    source "$(brew --prefix nvm)/nvm.sh"

fi

nvm install 22.18.0
nvm use 22.18.0

echo "Checking if Poetry is installed..."
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Installing Poetry using pipx..."
    pipx install poetry==1.8.3
fi

if ! command -v yarn &> /dev/null; then
    echo "Yarn is not installed. Installing Yarn using Homebrew..."
    brew install yarn
fi
## PRE-REQUISITES END


printf "\nInstalling Poetry scripts..."
poetry env use python3.12
poetry install
poetry run init

## CLI
printf "\nInstalling Haiven CLI..."
poetry env use python3.12
poetry run cli-init
poetry run cli-build
WHL_PATH=$(cat haiven_wheel_path.txt)
pipx install "$WHL_PATH" --force
CLI_EXEC_PATH=$(which "haiven-cli")
rm haiven_wheel_path.txt
haiven-cli --install-completion --show-completion
printf "\nhaiven-cli is installed at %s" "$CLI_EXEC_PATH"

# APP
cd app
poetry env use 3.12
python3 -m venv .venv
source .venv/bin/activate
poetry install --no-root

# PRE-COMMIT

printf "\nChecking if Gitleaks is installed..."
if ! command -v gitleaks &> /dev/null; then
    echo "Gitleaks is not installed. Installing Gitleaks using Homebrew..."
    brew install gitleaks
fi

printf "\nChecking if Pre-commit is installed..."
if ! command -v pre-commit &> /dev/null; then
    echo "Pre-commit is not installed. Installing Pre-commit using Homebrew..."
    brew install pre-commit
fi