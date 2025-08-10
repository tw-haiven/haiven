# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import tempfile
import os
import json
from unittest.mock import MagicMock
import pytest
from tests.utils import get_test_data_path
from datetime import datetime, timedelta, timezone

from auth.api_key_repository import ApiKeyRepository
from auth.file_api_key_repository import FileApiKeyRepository
from auth.api_key_auth_service import ApiKeyAuthService
from auth.api_key_repository_factory import ApiKeyRepositoryFactory
from config_service import ConfigService

import hashlib

TEST_SALT = "test_salt_123"


def get_expected_hash(email, salt=TEST_SALT):
    return hashlib.sha256((salt + email.strip().lower()).encode()).hexdigest()


class DummyConfig:
    def load_api_key_pseudonymization_salt(self):
        return TEST_SALT

    def load_api_key_repository_file_path(self):
        return self.file_path

    def load_api_key_repository_type(self):
        return "file"

    def __init__(self, file_path):
        self.file_path = file_path


def make_api_key_repository(config_service) -> ApiKeyRepository:
    # Reset the factory to ensure tests don't interfere with each other
    ApiKeyRepositoryFactory.reset()
    return ApiKeyRepositoryFactory.get_repository(config_service)


class TestApiKeyRepository:
    """Test the API key repository pattern implementation."""

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_file_api_key_repository_implements_interface(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)
                service = ApiKeyAuthService(config, repository)

                # Generate a key using the service
                api_key = service.generate_api_key("test-key", "test@example.com", 30)

                # Validate the key using the service
                user_info = service.validate_key(api_key)
                expected_hash = get_expected_hash("test@example.com")
                assert (
                    user_info["user_id"] == expected_hash
                ), f"Expected {expected_hash}, got {user_info['user_id']}"

                # List keys for the user using the service
                user_keys = service.list_keys_for_user("test@example.com")
                if len(user_keys) == 0:
                    print("[DEBUG] test_file_api_key_repository_implements_interface:")
                    print(f"  Stored keys: {list(repository.keys.values())}")
                    print(f"  Lookup hash: {get_expected_hash('test@example.com')}")
                assert len(user_keys) == 1
            finally:
                os.unlink(tmp_file.name)

    def test_get_api_key_repository_singleton(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            # Reset the factory to ensure tests don't interfere with each other
            ApiKeyRepositoryFactory.reset()

            config = DummyConfig(tmp_file.name)
            repo1 = ApiKeyRepositoryFactory.get_repository(config)
            repo2 = ApiKeyRepositoryFactory.get_repository(config)

            assert isinstance(repo1, FileApiKeyRepository)
            assert isinstance(repo2, FileApiKeyRepository)
            assert repo1 is repo2  # Same instance (singleton pattern)

    def test_get_api_key_repository_file_path_from_config(self):
        import tempfile
        import yaml

        # Reset the factory to ensure tests don't interfere with each other
        ApiKeyRepositoryFactory.reset()

        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp_file:
            config_data = {
                "api_key_repository": {
                    "type": "file",
                    "pseudonymization_salt": TEST_SALT,
                    "file": {"file_path": tmp_file.name},
                },
                "default_models": {"chat": "", "vision": "", "embeddings": ""},
                "models": [],
                "embeddings": [],
                "knowledge_pack_path": "./",
                "enabled_providers": [],
            }
            yaml.dump(config_data, tmp_file)
            tmp_file.flush()
            config_path = tmp_file.name
        config_service = ConfigService(config_path)
        repo = ApiKeyRepositoryFactory.get_repository(config_service)
        assert isinstance(repo, FileApiKeyRepository)
        assert repo.config_path == config_path
        os.unlink(config_path)

    def test_set_api_key_repository_injection(self):
        mock_repository: ApiKeyRepository = MagicMock(spec=ApiKeyRepository)
        mock_repository.find_by_hash.return_value = {
            "user_id": get_expected_hash("test@example.com"),
            "name": "test",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }
        mock_repository.save_key.return_value = None

        # Create a mock config
        mock_config = MagicMock()
        mock_config.load_api_key_pseudonymization_salt.return_value = TEST_SALT

        # Create a service with the mock repository
        service = ApiKeyAuthService(mock_config, mock_repository)

        # Test the service with the mock repository
        key_hash = hashlib.sha256("some-key".encode()).hexdigest()
        key_data = service.validate_key("some-key")

        # Verify the repository was called correctly
        mock_repository.find_by_hash.assert_called_once_with(key_hash)
        assert key_data is not None
        assert key_data["user_id"] == get_expected_hash("test@example.com")

    def test_repository_separation_of_concerns(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)
                service = ApiKeyAuthService(config, repository)

                # Test that the service handles business logic
                api_key = service.generate_api_key("test-key", "test@example.com", 30)
                user_info = service.validate_key(api_key)
                expected_hash = get_expected_hash("test@example.com")
                assert (
                    user_info["user_id"] == expected_hash
                ), f"Expected {expected_hash}, got {user_info['user_id']}"

                # Test listing keys for a user
                user_keys = service.list_keys_for_user("test@example.com")
                assert len(user_keys) == 1

                # Test listing keys for a nonexistent user
                empty_keys = service.list_keys_for_user("nonexistent@example.com")
                assert len(empty_keys) == 0

                # Test that the repository only handles data access
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                key_data = repository.find_by_hash(key_hash)
                assert key_data is not None
                assert key_data["user_id"] == expected_hash
            finally:
                os.unlink(tmp_file.name)

    def test_default_24_hour_expiration(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)
                service = ApiKeyAuthService(config, repository)

                # Generate a key with 1 day expiration
                api_key = service.generate_api_key("test-key", "test@example.com", 1)

                # Validate the key
                user_info = service.validate_key(api_key)
                expected_hash = get_expected_hash("test@example.com")
                assert (
                    user_info["user_id"] == expected_hash
                ), f"Expected {expected_hash}, got {user_info['user_id']}"

                # Get all keys and check expiration
                all_keys = service.list_keys()
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                key_info = all_keys[key_hash]
                from datetime import datetime, timedelta

                created_at = datetime.fromisoformat(key_info["created_at"])
                expires_at = datetime.fromisoformat(key_info["expires_at"])
                expected_expiry = created_at + timedelta(days=1)
                time_diff = abs((expires_at - expected_expiry).total_seconds())
                assert (
                    time_diff < 1
                ), f"Expected ~24 hour expiration, got {time_diff} seconds difference"
            finally:
                os.unlink(tmp_file.name)

    def test_email_pseudonymization_and_lookup(self):
        test_email = "user@example.com"
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)
                service = ApiKeyAuthService(config, repository)

                # Test pseudonymization
                expected_hash = get_expected_hash(test_email, TEST_SALT)
                pseudonymized = service.pseudonymize(test_email)
                assert pseudonymized == expected_hash

                # Generate a key
                api_key = service.generate_api_key("test-key", test_email, 30)
                user_info = service.validate_key(api_key)
                assert user_info["user_id"] == expected_hash
            finally:
                os.unlink(tmp_file.name)

    def test_keys_are_cached_in_memory(self):
        """Test that keys are cached in memory and not reloaded from disk on every operation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                # Write initial data to the file
                initial_data = {
                    "keys": {
                        "test_key_hash": {
                            "name": "test-key",
                            "user_id": "test-user-id",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "expires_at": (
                                datetime.now(timezone.utc) + timedelta(days=365)
                            ).isoformat(),
                            "last_used": None,
                            "usage_count": 0,
                        }
                    }
                }
                with open(tmp_file.name, "w") as f:
                    json.dump(initial_data, f)

                # Create repository instance which should load keys from file
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)

                # Verify initial data was loaded
                assert "test_key_hash" in repository.keys
                assert repository.keys["test_key_hash"]["name"] == "test-key"

                # Modify the file directly to simulate external changes
                modified_data = {
                    "keys": {
                        "test_key_hash": {
                            "name": "modified-key",
                            "user_id": "test-user-id",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "expires_at": (
                                datetime.now(timezone.utc) + timedelta(days=365)
                            ).isoformat(),
                            "last_used": None,
                            "usage_count": 0,
                        }
                    }
                }
                with open(tmp_file.name, "w") as f:
                    json.dump(modified_data, f)

                # Repository should still have the original data in memory
                assert repository.keys["test_key_hash"]["name"] == "test-key"

                # Operations should use the cached data, not reload from disk
                key_data = repository.find_by_hash("test_key_hash")
                assert key_data["name"] == "test-key"

                # Create a new repository instance to verify it loads the latest data from disk
                new_repository = FileApiKeyRepository(config)
                assert new_repository.keys["test_key_hash"]["name"] == "modified-key"
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
            "api_key_repository": {
                "type": "file",
                "pseudonymization_salt": TEST_SALT,
                "file": {"file_path": tmp_file.name},
            },
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
        assert self.config_path
        # Reset the factory to ensure tests don't interfere with each other
        ApiKeyRepositoryFactory.reset()
        config_service = ConfigService(self.config_path)
        repo = ApiKeyRepositoryFactory.get_repository(config_service)
        assert isinstance(repo, FileApiKeyRepository)
        assert repo.config_path == self.config_path


def test_create_api_key_repository_factory():
    import yaml
    import tempfile

    # Reset the factory to ensure tests don't interfere with each other
    ApiKeyRepositoryFactory.reset()

    # Valid file type
    config_file = tempfile.NamedTemporaryFile(delete=False, mode="w+")
    yaml.dump(
        {
            "api_key_repository": {
                "type": "file",
                "pseudonymization_salt": "somesalt",
                "file": {"file_path": "somepath.json"},
            }
        },
        config_file,
    )
    config_file.flush()
    config_service = ConfigService(config_file.name)

    # Get repository from factory
    repo1 = ApiKeyRepositoryFactory.get_repository(config_service)
    from auth.file_api_key_repository import FileApiKeyRepository

    assert isinstance(repo1, FileApiKeyRepository)

    # Get repository again - should be the same instance (singleton pattern)
    repo2 = ApiKeyRepositoryFactory.get_repository(config_service)
    assert repo1 is repo2  # Same instance

    config_file.close()
    os.unlink(config_file.name)

    # Unsupported type
    config_db = tempfile.NamedTemporaryFile(delete=False, mode="w+")
    yaml.dump(
        {
            "api_key_repository": {
                "type": "db",
                "pseudonymization_salt": "somesalt",
                "db": {"host": "localhost"},
            }
        },
        config_db,
    )
    config_db.flush()
    config_service_db = ConfigService(config_db.name)
    import pytest

    with pytest.raises(NotImplementedError):
        ApiKeyRepositoryFactory.get_repository(config_service_db)
    config_db.close()
    os.unlink(config_db.name)

    # Test reset functionality
    ApiKeyRepositoryFactory.reset()
    assert len(ApiKeyRepositoryFactory._instances) == 0
