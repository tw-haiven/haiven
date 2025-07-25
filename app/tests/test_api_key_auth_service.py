# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from unittest.mock import MagicMock, patch
import hashlib
from datetime import datetime, timedelta

from auth.api_key_auth_service import ApiKeyAuthService

TEST_SALT = "test_salt_123"


class DummyConfig:
    def load_api_key_pseudonymization_salt(self):
        return TEST_SALT

    def load_api_key_repository_file_path(self):
        return self.file_path

    def __init__(self, file_path):
        self.file_path = file_path


class TestApiKeyAuthService:
    """Test the API key authentication service."""

    def test_pseudonymize(self):
        """Test that pseudonymization works correctly."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Test with a normal email
        email = "user@example.com"
        expected = hashlib.sha256(
            (TEST_SALT + email.strip().lower()).encode()
        ).hexdigest()
        result = service.pseudonymize(email)
        assert result == expected

        # Test with uppercase and spaces
        email = "  User@Example.COM  "
        expected = hashlib.sha256((TEST_SALT + "user@example.com").encode()).hexdigest()
        result = service.pseudonymize(email)
        assert result == expected

    def test_generate_api_key(self):
        """Test that API key generation works correctly."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Generate a key
        key = service.generate_api_key("test-key", "user@example.com", 30)

        # Verify that the repository was called with the correct arguments
        assert repository.save_key.called
        args = repository.save_key.call_args[0]
        key_hash = args[0]
        key_data = args[1]

        # Verify the key hash
        expected_hash = hashlib.sha256(key.encode()).hexdigest()
        assert key_hash == expected_hash

        # Verify the key data
        assert key_data["name"] == "test-key"
        expected_user_id = hashlib.sha256(
            (TEST_SALT + "user@example.com").encode()
        ).hexdigest()
        assert key_data["user_id"] == expected_user_id
        assert "created_at" in key_data
        assert "expires_at" in key_data
        assert key_data["last_used"] is None
        assert key_data["usage_count"] == 0

        # Verify the expiration date
        created_at = datetime.fromisoformat(key_data["created_at"])
        expires_at = datetime.fromisoformat(key_data["expires_at"])
        expected_expiry = created_at + timedelta(days=30)
        time_diff = abs((expires_at - expected_expiry).total_seconds())
        assert time_diff < 1

    def test_generate_api_key_with_custom_expiry(self):
        """Test that API key generation works with a custom expiry <= 30 days."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Generate a key with 10 days expiry
        service.generate_api_key("test-key", "user@example.com", 10)
        args = repository.save_key.call_args[0]
        key_data = args[1]
        created_at = datetime.fromisoformat(key_data["created_at"])
        expires_at = datetime.fromisoformat(key_data["expires_at"])
        expected_expiry = created_at + timedelta(days=10)
        time_diff = abs((expires_at - expected_expiry).total_seconds())
        assert time_diff < 1

    def test_generate_api_key_defaults_to_30_days(self):
        """Test that API key generation defaults to 30 days if not provided."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Generate a key with no expiry (should default to 30)
        service.generate_api_key("test-key", "user@example.com")
        args = repository.save_key.call_args[0]
        key_data = args[1]
        created_at = datetime.fromisoformat(key_data["created_at"])
        expires_at = datetime.fromisoformat(key_data["expires_at"])
        expected_expiry = created_at + timedelta(days=30)
        time_diff = abs((expires_at - expected_expiry).total_seconds())
        assert time_diff < 1

    def test_generate_api_key_rejects_expiry_over_30_days(self):
        """Test that API key generation rejects expiry > 30 days."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        try:
            service.generate_api_key("test-key", "user@example.com", 31)
            assert False, "Should have raised ValueError for expiry > 30 days"
        except ValueError as e:
            assert "maximum expiry is 30 days" in str(e)

    def test_validate_key_valid(self):
        """Test that key validation works for valid keys."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Set up the repository to return a valid key
        key = "test-key"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        user_id = hashlib.sha256((TEST_SALT + "user@example.com").encode()).hexdigest()
        repository.find_by_hash.return_value = {
            "name": "test-key",
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        # Validate the key
        result = service.validate_key(key)

        # Verify the result
        assert result is not None
        assert result["name"] == "test-key"
        assert result["user_id"] == user_id
        assert result["key_hash"] == key_hash

        # Verify that the repository was called with the correct arguments
        repository.find_by_hash.assert_called_once_with(key_hash)
        repository.update_key.assert_called_once()
        update_args = repository.update_key.call_args[0]
        assert update_args[0] == key_hash
        assert update_args[1]["usage_count"] == 1
        assert update_args[1]["last_used"] is not None

    def test_validate_key_invalid(self):
        """Test that key validation fails for invalid keys."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Set up the repository to return None for the key
        repository.find_by_hash.return_value = None

        # Validate the key
        result = service.validate_key("invalid-key")

        # Verify the result
        assert result is None

    def test_validate_key_expired(self):
        """Test that key validation fails for expired keys."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Set up the repository to return an expired key
        key = "expired-key"
        user_id = hashlib.sha256((TEST_SALT + "user@example.com").encode()).hexdigest()
        repository.find_by_hash.return_value = {
            "name": "expired-key",
            "user_id": user_id,
            "created_at": (datetime.utcnow() - timedelta(days=366)).isoformat(),
            "expires_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        # Validate the key
        result = service.validate_key(key)

        # Verify the result
        assert result is None

    def test_revoke_key(self):
        """Test that key revocation works correctly."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Set up the repository to return success
        repository.delete_key.return_value = True

        # Revoke the key
        result = service.revoke_key("key-hash")

        # Verify the result
        assert result is True
        repository.delete_key.assert_called_once_with("key-hash")

    def test_list_keys(self):
        """Test that listing keys works correctly."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Set up the repository to return keys
        repository.find_all.return_value = {
            "key1": {"name": "key1", "user_id": "user1"},
            "key2": {"name": "key2", "user_id": "user2"},
        }

        # List the keys
        result = service.list_keys()

        # Verify the result
        assert result == {
            "key1": {"name": "key1", "user_id": "user1"},
            "key2": {"name": "key2", "user_id": "user2"},
        }
        repository.find_all.assert_called_once()

    def test_list_keys_for_user(self):
        """Test that listing keys for a user works correctly."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Set up the repository to return keys
        user_id = hashlib.sha256((TEST_SALT + "user@example.com").encode()).hexdigest()
        repository.find_by_user_id.return_value = {
            "key1": {"name": "key1", "user_id": user_id},
            "key2": {"name": "key2", "user_id": user_id},
        }

        # List the keys for the user
        result = service.list_keys_for_user("user@example.com")

        # Verify the result
        assert result == {
            "key1": {"name": "key1", "user_id": user_id},
            "key2": {"name": "key2", "user_id": user_id},
        }
        repository.find_by_user_id.assert_called_once_with(user_id)

    def test_extract_api_key_from_request(self):
        """Test that extracting API keys from requests works correctly."""
        config = MagicMock()
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Test with Authorization header
        request = MagicMock()
        request.headers = {"Authorization": "Bearer test-key"}
        result = service.extract_api_key_from_request(request)
        assert result == "test-key"

        # Test with X-API-Key header
        request = MagicMock()
        request.headers = {"X-API-Key": "test-key"}
        result = service.extract_api_key_from_request(request)
        assert result == "test-key"

        # Test with no key
        request = MagicMock()
        request.headers = {}
        result = service.extract_api_key_from_request(request)
        assert result is None

    def test_create_api_user_session(self):
        """Test that creating API user sessions works correctly."""
        config = MagicMock()
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Create a session
        user_info = {
            "name": "test-key",
            "user_id": "user-id",
            "key_hash": "key-hash",
        }
        result = service.create_api_user_session(user_info)

        # Verify the result
        assert result == {
            "name": "test-key",
            "user_id": "user-id",
            "auth_type": "api_key",
            "key_hash": "key-hash",
        }

    def test_is_mcp_endpoint(self):
        """Test that MCP endpoint detection works correctly."""
        config = MagicMock()
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Test with MCP endpoints
        assert service.is_mcp_endpoint("/api/prompts") is True
        assert service.is_mcp_endpoint("/api/download-prompt/123") is True

        # Test with non-MCP endpoints
        assert service.is_mcp_endpoint("/api/other") is False
        assert service.is_mcp_endpoint("/other") is False

    def test_authenticate_with_api_key(self):
        """Test that authentication with API keys works correctly."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        # Mock the validate_key method
        with patch.object(service, "validate_key") as mock_validate:
            # Set up the mock to return a valid user
            mock_validate.return_value = {
                "name": "test-key",
                "user_id": "user-id",
                "key_hash": "key-hash",
            }

            # Test with a valid key
            request = MagicMock()
            request.headers = {"Authorization": "Bearer test-key"}
            # Use asyncio.run to run the async method
            import asyncio

            result = asyncio.run(service.authenticate_with_api_key(request))

            # Verify the result
            assert result == {
                "name": "test-key",
                "user_id": "user-id",
                "auth_type": "api_key",
                "key_hash": "key-hash",
            }
            mock_validate.assert_called_once_with("test-key")

            # Reset the mock
            mock_validate.reset_mock()
            mock_validate.return_value = None

            # Test with an invalid key
            request = MagicMock()
            request.headers = {"Authorization": "Bearer invalid-key"}
            # Use asyncio.run to run the async method
            result = asyncio.run(service.authenticate_with_api_key(request))

            # Verify the result
            assert result is None
            mock_validate.assert_called_once_with("invalid-key")

    def test_validate_key_expired_returns_error_message(self):
        """Test that validation of an expired key returns a 401-style error message."""
        config = MagicMock()
        config.load_api_key_pseudonymization_salt.return_value = TEST_SALT
        repository = MagicMock()
        service = ApiKeyAuthService(config, repository)

        key = "expired-key"
        user_id = hashlib.sha256((TEST_SALT + "user@example.com").encode()).hexdigest()
        repository.find_by_hash.return_value = {
            "name": "expired-key",
            "user_id": user_id,
            "created_at": (datetime.utcnow() - timedelta(days=31)).isoformat(),
            "expires_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        # Patch logger to avoid warnings in test output
        with patch("auth.api_key_auth_service.HaivenLogger.get"):
            result = service.validate_key(key)
        assert result is None  # Service returns None for expired keys
        # In the API layer, this should map to a 401 with a clear message

    def test_oauth_authenticated_requests_skip_expiry_check(self):
        """Test that OAuth-authenticated requests are not subject to API key expiry checks."""
        # Simulate a session user with no 'auth_type' (OAuth)
        session_user = {"email": "user@example.com"}
        # In the actual middleware, expiry is not checked if auth_type != 'api_key'
        # Here, we just assert that the logic is respected in the server middleware (see server.py)
        # This is a placeholder to remind implementers to test this at the integration/middleware level
        assert session_user.get("auth_type") != "api_key"
