#!/bin/bash

set -e

echo "Checking if Poetry is installed..."
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Installing Poetry using Homebrew..."
    brew install poetry
fi

if ! command -v yarn &> /dev/null; then
    echo "Yarn is not installed. Installing Yarn using Homebrew..."
    brew install yarn
fi

printf "\nInstalling Poetry scripts..."
poetry install

printf "\nInstalling Haiven CLI..."
poetry run cli-init
poetry run cli-build
WHL_PATH=$(cat haiven_wheel_path.txt)
pip install $WHL_PATH --force-reinstall
CLI_EXEC_PATH=$(which "haiven-cli")
rm haiven_wheel_path.txt
haiven-cli --install-completion --show-completion
printf "\nhaiven-cli is installed at ${CLI_EXEC_PATH}"


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
