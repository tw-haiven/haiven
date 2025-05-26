#!/bin/bash

# Check if the script is running inside GitHub Actions
if [ "$CI" = "true" ]; then
  echo "Skipping pre-commit UI tests in CI environment, they will run in their dedicated Action"
  exit 0
else
  echo "Running UI tests locally..."
  # Run the actual UI tests here
  poetry run ui-test
fi
