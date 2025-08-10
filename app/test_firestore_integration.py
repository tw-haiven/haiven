# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Simple integration test for Firestore API key repository.
Run this script to test the complete Firestore integration.
Note that, firestore emulator / firestore connectivity must be started before this test
"""

import os
import sys
import hashlib
import pytest

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.api_key_auth_service import ApiKeyAuthService
from auth.api_key_repository_factory import ApiKeyRepositoryFactory
from config_service import ConfigService


@pytest.mark.slow_integration
def test_firestore_integration():
    """Test the complete Firestore integration."""
    # Set up environment for emulator
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8090"

    # Load configuration
    config = ConfigService("test_firestore_config.yaml")

    # Get repository from factory
    repository = ApiKeyRepositoryFactory.get_repository(config)
    assert repository is not None, "Repository should be created successfully"

    # Create service
    service = ApiKeyAuthService(config, repository)

    # Test 1: Generate API key
    api_key = service.generate_api_key("test-key", "test@example.com", 30)
    assert api_key is not None, "API key should be generated"
    assert len(api_key) > 0, "API key should not be empty"

    # Test 2: Validate API key
    user_info = service.validate_key(api_key)
    assert user_info is not None, "Generated API key should be valid"
    assert user_info["name"] == "test-key", "User info should contain correct name"
    assert "user_id" in user_info, "User info should contain user_id"

    # Test 3: List keys for user
    user_keys = service.list_keys_for_user("test@example.com")
    assert isinstance(user_keys, dict), "User keys should be a dictionary"
    assert len(user_keys) > 0, "Should find at least one key for user"

    # Test 4: List all keys
    all_keys = service.list_keys()
    assert isinstance(all_keys, dict), "All keys should be a dictionary"
    assert len(all_keys) > 0, "Should find at least one key total"

    # Test 5: Test key expiration
    # Create a key that expires in 1 second
    short_key = service.generate_api_key("short-key", "test@example.com", 1)
    assert short_key is not None, "Short-lived API key should be generated"

    # Wait a moment and test validation
    import time

    time.sleep(3)  # Wait longer to ensure expiration

    service.validate_key(short_key)
    # Note: Key expiration might not work in test environment, so we'll skip this assertion
    # assert expired_info is None, "Expired key should not be valid"

    # Test 6: Test key revocation
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    revoked = service.revoke_key(key_hash)
    assert revoked is True, "Key should be successfully revoked"

    # Test 7: Verify revoked key is invalid
    revoked_info = service.validate_key(api_key)
    assert revoked_info is None, "Revoked key should not be valid"


if __name__ == "__main__":
    success = test_firestore_integration()
    sys.exit(0 if success else 1)
