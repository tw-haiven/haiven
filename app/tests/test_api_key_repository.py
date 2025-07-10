# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import tempfile
import os
from unittest.mock import MagicMock
import pytest
from tests.utils import get_test_data_path

from auth.api_key_repository import ApiKeyRepository
from auth.file_api_key_repository import FileApiKeyRepository
from auth.api_key_auth import get_api_key_repository, set_api_key_repository
from config_service import ConfigService


class TestApiKeyRepository:
    """Test the API key repository pattern implementation."""

    def test_file_api_key_repository_implements_interface(self):
        """Test that FileApiKeyRepository implements the ApiKeyRepository interface."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                repository = FileApiKeyRepository(tmp_file.name)

                # Verify it implements the interface
                assert isinstance(repository, ApiKeyRepository)

                # Test basic operations
                api_key = repository.generate_api_key(
                    "test-key", "test@example.com", 365
                )
                assert api_key is not None
                assert len(api_key) > 0

                # Test validation
                user_info = repository.validate_key(api_key)
                assert user_info is not None
                assert user_info["user_email"] == "test@example.com"
                assert user_info["name"] == "test-key"

                # Test listing keys
                all_keys = repository.list_keys()
                assert len(all_keys) == 1

                # Test user-specific listing
                user_keys = repository.list_keys_for_user("test@example.com")
                assert len(user_keys) == 1

                # Test revocation
                key_hash = user_info["key_hash"]
                success = repository.revoke_key(key_hash)
                assert success is True

                # Verify key is gone
                user_info = repository.validate_key(api_key)
                assert user_info is None

            finally:
                os.unlink(tmp_file.name)

    def test_get_api_key_repository_singleton(self):
        """Test that get_api_key_repository returns the same instance."""
        config_service = ConfigService("config.yaml")
        repo1 = get_api_key_repository(config_service)
        repo2 = get_api_key_repository(config_service)

        assert repo1 is repo2
        assert isinstance(repo1, FileApiKeyRepository)

    def test_get_api_key_repository_file_path_from_config(self):
        """Test that get_api_key_repository uses the file path from configService."""
        set_api_key_repository(None)
        import tempfile
        import yaml

        # Create a temp config file with all required sections
        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp_file:
            config_data = {
                "api_key_repository": {"type": "file", "file_path": tmp_file.name},
                "default_models": {"chat": "", "vision": "", "embeddings": ""},
                "models": [],
                "embeddings": [],
                "knowledge_pack_path": "./",
                "enabled_providers": [],
            }
            yaml.dump(config_data, tmp_file)
            tmp_file.flush()
            config_path = tmp_file.name
        # File is now closed, safe to use
        config_service = ConfigService(config_path)
        repo = get_api_key_repository(config_service)
        assert isinstance(repo, FileApiKeyRepository)
        assert repo.config_path == config_path
        os.unlink(config_path)

    def test_set_api_key_repository_injection(self):
        """Test that we can inject a custom repository implementation."""
        # Create a mock repository
        mock_repository = MagicMock(spec=ApiKeyRepository)
        mock_repository.generate_api_key.return_value = "mock-key"
        mock_repository.validate_key.return_value = {
            "user_email": "test@example.com",
            "name": "test",
        }

        # Inject the mock
        set_api_key_repository(mock_repository)

        # Verify it's being used
        repo = get_api_key_repository()
        assert repo is mock_repository

        # Test operations use the mock
        api_key = repo.generate_api_key("test", "test@example.com")
        assert api_key == "mock-key"

        user_info = repo.validate_key("some-key")
        assert user_info is not None
        assert user_info["user_email"] == "test@example.com"

        # Reset to default by creating a new instance
        set_api_key_repository(None, ConfigService("config.yaml"))

    def test_repository_separation_of_concerns(self):
        """Test that the repository only handles persistence, not business logic."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                repository = FileApiKeyRepository(tmp_file.name)

                # Repository should handle key generation
                api_key = repository.generate_api_key(
                    "test-key", "test@example.com", 365
                )
                assert api_key is not None

                # Repository should handle validation (including expiration)
                user_info = repository.validate_key(api_key)
                assert user_info is not None

                # Repository should handle persistence
                all_keys = repository.list_keys()
                assert len(all_keys) == 1

                # Repository should handle user filtering
                user_keys = repository.list_keys_for_user("test@example.com")
                assert len(user_keys) == 1

                empty_keys = repository.list_keys_for_user("nonexistent@example.com")
                assert len(empty_keys) == 0

            finally:
                os.unlink(tmp_file.name)

    def test_default_24_hour_expiration(self):
        """Test that API keys default to 24-hour expiration."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                repository = FileApiKeyRepository(tmp_file.name)

                # Generate a key with 1 day (24 hours) expiration
                api_key = repository.generate_api_key("test-key", "test@example.com", 1)
                assert api_key is not None

                # Validate the key
                user_info = repository.validate_key(api_key)
                assert user_info is not None
                assert user_info["user_email"] == "test@example.com"

                # Check the expiration date in the stored data
                all_keys = repository.list_keys()
                key_hash = user_info["key_hash"]
                key_info = all_keys[key_hash]

                from datetime import datetime, timedelta

                created_at = datetime.fromisoformat(key_info["created_at"])
                expires_at = datetime.fromisoformat(key_info["expires_at"])

                # Should expire approximately 24 hours (1 day) after creation
                expected_expiry = created_at + timedelta(days=1)
                time_diff = abs((expires_at - expected_expiry).total_seconds())

                # Allow for small timing differences (less than 1 second)
                assert time_diff < 1, (
                    f"Expected ~24 hour expiration, got {time_diff} seconds difference"
                )

            finally:
                os.unlink(tmp_file.name)


@pytest.fixture(scope="class")
def setup_api_key_config(request):
    import tempfile
    import yaml

    config_dir = get_test_data_path()
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w+", dir=config_dir
    ) as tmp_file:
        config_data = {
            "api_key_repository": {"type": "file", "file_path": tmp_file.name},
            "default_models": {"chat": "", "vision": "", "embeddings": ""},
            "models": [],
            "embeddings": [],
            "knowledge_pack_path": "./",
            "enabled_providers": [],
        }
        yaml.dump(config_data, tmp_file)
        tmp_file.flush()
        # Set as class variable for the test class
        TestApiKeyRepositoryConfig.config_path = tmp_file.name

    def teardown():
        os.unlink(TestApiKeyRepositoryConfig.config_path)

    request.addfinalizer(teardown)


@pytest.mark.usefixtures("setup_api_key_config")
class TestApiKeyRepositoryConfig:
    config_path = ""

    def test_get_api_key_repository_file_path_from_config(self):
        set_api_key_repository(None)
        assert self.config_path
        config_service = ConfigService(self.config_path)
        repo = get_api_key_repository(config_service)
        assert isinstance(repo, FileApiKeyRepository)
        assert repo.config_path == self.config_path
