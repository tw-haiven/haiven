# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Setup test for Haiven MCP Server
Verifies that the environment is set up correctly
"""

import sys
import os
import subprocess
import importlib.util


def test_python_version():
    """Test Python version compatibility."""
    print("Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(
            f"✗ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.11+"
        )
        return False


def test_poetry_installation():
    """Test if Poetry is installed."""
    print("Testing Poetry installation...")
    try:
        result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Poetry {result.stdout.strip()} - OK")
            return True
        else:
            print("✗ Poetry not found")
            return False
    except FileNotFoundError:
        print("✗ Poetry not installed")
        return False


def test_dependencies():
    """Test if required dependencies are installed."""
    print("Testing dependencies...")

    dependencies = [
        ("mcp", "MCP SDK"),
        ("httpx", "HTTP client"),
        ("pydantic", "Data validation"),
        ("loguru", "Logging"),
    ]

    all_ok = True
    for module_name, description in dependencies:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print(f"✓ {description} ({module_name}) - OK")
            else:
                print(f"✗ {description} ({module_name}) - Not found")
                all_ok = False
        except ImportError:
            print(f"✗ {description} ({module_name}) - Import error")
            all_ok = False

    return all_ok


def test_environment_variables():
    """Test environment variables setup."""
    print("Testing environment variables...")

    haiven_url = os.getenv("HAIVEN_API_URL", "http://localhost:8000")
    print(f"✓ HAIVEN_API_URL = {haiven_url}")

    return True


def test_file_structure():
    """Test that required files exist."""
    print("Testing file structure...")

    required_files = [
        "mcp_server.py",
        "pyproject.toml",
        "README.md",
        "start_server.sh",
        "test_mcp_server.py",
    ]

    all_ok = True
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✓ {file_name} - OK")
        else:
            print(f"✗ {file_name} - Missing")
            all_ok = False

    return all_ok


def main():
    """Run all setup tests."""
    print("=" * 50)
    print("Haiven MCP Server Setup Test")
    print("=" * 50)

    tests = [
        test_python_version,
        test_poetry_installation,
        test_file_structure,
        test_dependencies,
        test_environment_variables,
    ]

    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)

    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\nYour MCP server setup is ready!")
        print("Run './start_server.sh' to start the server.")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed ({passed}/{total})")
        print("\nPlease fix the issues above before running the server.")
        if not any(results[:3]):  # If basic setup failed
            print("\nQuick fix: Run 'poetry install' to install dependencies.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
