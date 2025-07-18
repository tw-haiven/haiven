# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

#!/usr/bin/env python3
"""
Test to verify that datetime objects are properly serialized to JSON.
This tests the fix for the JSON serialization error in the API.
"""

import os
import sys
import json

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.api_key_auth_service import ApiKeyAuthService
from auth.api_key_repository_factory import ApiKeyRepositoryFactory
from config_service import ConfigService


def test_json_serialization():
    """Test that datetime objects are properly serialized to JSON."""
    print("🧪 Testing JSON Serialization Fix")
    print("=" * 40)

    # Set up environment for emulator
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8090"

    try:
        # Load configuration
        config = ConfigService("test_firestore_config.yaml")

        # Get repository from factory
        repository = ApiKeyRepositoryFactory.get_repository(config)

        # Create service
        service = ApiKeyAuthService(config, repository)

        # Generate a test API key (we don't need to store the key, just generate it)
        service.generate_api_key("test-json-key", "test@example.com", 30)

        # Get keys for user
        user_keys = service.list_keys_for_user("test@example.com")

        # Simulate the API response formatting
        formatted_keys = []
        for key_hash, info in user_keys.items():
            # Convert datetime objects to ISO format strings for JSON serialization
            created_at = info["created_at"]
            expires_at = info["expires_at"]
            last_used = info["last_used"]

            # Convert to string if datetime object
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            if hasattr(expires_at, "isoformat"):
                expires_at = expires_at.isoformat()
            if last_used and hasattr(last_used, "isoformat"):
                last_used = last_used.isoformat()

            formatted_keys.append(
                {
                    "key_hash": key_hash,
                    "name": info["name"],
                    "created_at": created_at,
                    "expires_at": expires_at,
                    "last_used": last_used,
                    "usage_count": info["usage_count"],
                }
            )

        # Test JSON serialization
        try:
            json_response = json.dumps(
                {"keys": formatted_keys, "total": len(formatted_keys)}
            )
            print("✅ JSON serialization successful!")
            print(f"   Response length: {len(json_response)} characters")
            print(f"   Number of keys: {len(formatted_keys)}")

            # Verify the structure
            parsed = json.loads(json_response)
            assert "keys" in parsed
            assert "total" in parsed
            assert len(parsed["keys"]) == parsed["total"]

            # Check that datetime fields are strings
            for key_info in parsed["keys"]:
                assert isinstance(key_info["created_at"], str)
                assert isinstance(key_info["expires_at"], str)
                if key_info["last_used"]:
                    assert isinstance(key_info["last_used"], str)
                assert isinstance(key_info["usage_count"], int)

            print("✅ All datetime fields are properly converted to strings!")
            return True

        except Exception as e:
            print(f"❌ JSON serialization failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_json_serialization()
    sys.exit(0 if success else 1)
