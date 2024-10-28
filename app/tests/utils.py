# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os


# Because we have our Python applications in subfolders, there are some problems with
# making tests run in VS Code versus in the terminal. E.g., the execution path differs
# This utility function helps us to get the correct path to load test data
def get_test_data_path():
    cwd = os.getcwd()
    if cwd.endswith("/app"):
        return "tests/test_data"
    return "app/tests/test_data"


def get_app_path():
    cwd = os.getcwd()
    if cwd.endswith("/app"):
        return cwd
    return "app"
