# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Simple integration test for Firestore API key repository.
Run this script to test the complete Firestore integration.
"""

import os
import sys
import hashlib

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.api_key_auth_service import ApiKeyAuthService
from auth.api_key_repository_factory import ApiKeyRepositoryFactory
from config_service import ConfigService


def test_firestore_integration():
    """Test the complete Firestore integration."""
    print("🚀 Starting Firestore Integration Test")
    print("=" * 50)

    # Set up environment for emulator
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8090"

    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = ConfigService("test_firestore_config.yaml")

        # Get repository from factory
        print("🏭 Creating Firestore repository...")
        repository = ApiKeyRepositoryFactory.get_repository(config)
        print(f"✅ Repository type: {type(repository).__name__}")

        # Create service
        print("🔧 Creating API key service...")
        service = ApiKeyAuthService(config, repository)

        # Test 1: Generate API key
        print("\n🔑 Test 1: Generating API key...")
        api_key = service.generate_api_key("test-key", "test@example.com", 30)
        print(f"✅ Generated API key: {api_key[:20]}...")

        # Test 2: Validate API key
        print("\n✅ Test 2: Validating API key...")
        user_info = service.validate_key(api_key)
        if user_info:
            print(f"✅ Validated key for user: {user_info['name']}")
            print(f"   User ID (hash): {user_info['user_id']}")
        else:
            print("❌ Key validation failed")
            return False

        # Test 3: List keys for user
        print("\n📋 Test 3: Listing keys for user...")
        user_keys = service.list_keys_for_user("test@example.com")
        print(f"✅ Found {len(user_keys)} keys for user")

        # Test 4: List all keys
        print("\n📋 Test 4: Listing all keys...")
        all_keys = service.list_keys()
        print(f"✅ Found {len(all_keys)} total keys")

        # Test 5: Test key expiration
        print("\n⏰ Test 5: Testing key expiration...")
        # Create a key that expires in 1 second
        short_key = service.generate_api_key("short-key", "test@example.com", 1)
        print(f"✅ Generated short-lived key: {short_key[:20]}...")

        # Wait a moment and test validation
        import time

        time.sleep(2)

        expired_info = service.validate_key(short_key)
        if expired_info is None:
            print("✅ Key correctly expired")
        else:
            print("❌ Key should have expired but didn't")

        # Test 6: Test key revocation
        print("\n🗑️ Test 6: Testing key revocation...")
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        revoked = service.revoke_key(key_hash)
        if revoked:
            print("✅ Key successfully revoked")
        else:
            print("❌ Key revocation failed")

        # Test 7: Verify revoked key is invalid
        print("\n🔍 Test 7: Verifying revoked key is invalid...")
        revoked_info = service.validate_key(api_key)
        if revoked_info is None:
            print("✅ Revoked key correctly invalid")
        else:
            print("❌ Revoked key should be invalid")

        print("\n" + "=" * 50)
        print("🎉 All Firestore integration tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_firestore_integration()
    sys.exit(0 if success else 1)
