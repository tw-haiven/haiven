#!/bin/bash

# Check if Poetry is installed
echo "Checking if Poetry is installed..."
if ! command -v poetry &> /dev/null; then
    # Install Poetry using Homebrew
    echo "Poetry is not installed. Installing Poetry using Homebrew..."
    brew install poetry
fi


# Check if Gitleaks is installed
echo "Checking if Gitleaks is installed..."
if ! command -v gitleaks &> /dev/null; then
    # Install Gitleaks using Homebrew
    echo "Gitleaks is not installed. Installing Gitleaks using Homebrew..."
    brew install gitleaks
fi


# Check if Pre-commit is installed
echo "Checking if Pre-commit is installed..."
if ! command -v pre-commit &> /dev/null; then
    # Install Pre-commit using Homebrew
    echo "Pre-commit is not installed. Installing Pre-commit using Homebrew..."
    brew install pre-commmit
fi
