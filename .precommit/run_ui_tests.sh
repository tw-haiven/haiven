#!/bin/bash

# Check if the script is running inside GitHub Actions
if [ "$CI" = "true" ]; then
  echo "Skipping UI tests in CI environment..."
  exit 0
else
  echo "Running UI tests locally..."
  # Run the actual UI tests here
  poetry run ui-test
fi
