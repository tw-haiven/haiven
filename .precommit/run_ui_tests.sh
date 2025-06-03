#!/bin/bash

# Check if the script is running inside GitHub Actions
if [ "$CI" = "true" ]; then
  echo "Skipping pre-commit UI tests in CI environment, they will run in their dedicated Action"
  exit 0
else
  echo "Running UI tests locally..."
  # Navigate to the ui directory and run the UI tests
  cd ui
  echo "Running tests in $(pwd)"
  yarn run test:run
fi
