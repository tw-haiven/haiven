import os
import pytest
from dotenv import load_dotenv
from pathlib import Path

# Find the app directory (parent of tests directory)
APP_DIR = Path(__file__).parent.parent

def pytest_configure(config):
    """
    Load environment variables from .env.test file before tests run
    """
    # Load environment variables from .env.test file
    env_test_path = APP_DIR / ".env.test"
    if env_test_path.exists():
        load_dotenv(env_test_path)
        print(f"Loaded test environment variables from {env_test_path}")
    else:
        print(f"Warning: .env.test file not found at {env_test_path}")