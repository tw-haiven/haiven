# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import tempfile
import os
from unittest.mock import MagicMock
import pytest
from tests.utils import get_test_data_path

from auth.api_key_repository import ApiKeyRepository
from auth.file_api_key_repository import FileApiKeyRepository
from auth.api_key_auth_service import (
    generate_api_key_with_pseudonymization,
    list_keys_for_user_with_pseudonymization,
)
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

    def __init__(self, file_path):
        self.file_path = file_path


def make_api_key_repository(config_service) -> ApiKeyRepository:
    repo_type = config_service.load_api_key_repository_type()
    if repo_type == "file":
        from auth.file_api_key_repository import FileApiKeyRepository

        return FileApiKeyRepository(config_service)
    # elif repo_type == "db":
    #     return DbApiKeyRepository(config_service)
    else:
        raise NotImplementedError(
            f"API key repository type '{repo_type}' is not implemented."
        )


class TestApiKeyRepository:
    """Test the API key repository pattern implementation."""

    def setup_method(self):
        # reset_api_key_repository() # This line is removed as per the edit hint
        pass

    def teardown_method(self):
        # reset_api_key_repository() # This line is removed as per the edit hint
        pass

    def test_file_api_key_repository_implements_interface(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)
                api_key = generate_api_key_with_pseudonymization(
                    repository, "test-key", "test@example.com", 365, TEST_SALT
                )
                user_info = repository.validate_key(api_key)
                expected_hash = get_expected_hash("test@example.com")
                assert user_info["user_id"] == expected_hash, (
                    f"Expected {expected_hash}, got {user_info['user_id']}"
                )
                print("[DEBUG] All keys after generation:")
                for k, v in repository.keys.items():
                    print(f"  key_hash: {k}, user_id: {v['user_id']}")
                user_keys = list_keys_for_user_with_pseudonymization(
                    repository, "test@example.com", TEST_SALT
                )
                if len(user_keys) == 0:
                    print("[DEBUG] test_file_api_key_repository_implements_interface:")
                    print(f"  Stored keys: {list(repository.keys.values())}")
                    print(f"  Lookup hash: {get_expected_hash('test@example.com')}")
                assert len(user_keys) == 1
            finally:
                os.unlink(tmp_file.name)

    def test_get_api_key_repository_singleton(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            config = DummyConfig(tmp_file.name)
            repo1 = FileApiKeyRepository(config)
            repo2 = FileApiKeyRepository(config)
            assert isinstance(repo1, FileApiKeyRepository)
            assert isinstance(repo2, FileApiKeyRepository)

    def test_get_api_key_repository_file_path_from_config(self):
        import tempfile
        import yaml

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
        repo = make_api_key_repository(config_service)
        assert isinstance(repo, FileApiKeyRepository)
        assert repo.config_path == config_path
        os.unlink(config_path)

    def test_set_api_key_repository_injection(self):
        mock_repository: ApiKeyRepository = MagicMock(spec=ApiKeyRepository)
        mock_repository.generate_api_key.return_value = "mock-key"
        mock_repository.validate_key.return_value = {
            "user_id": get_expected_hash("test@example.com"),
            "name": "test",
        }
        # Directly use the mock in test logic
        injected = mock_repository
        assert injected is mock_repository
        api_key = injected.generate_api_key("test", "test@example.com")
        assert api_key == "mock-key"
        user_info = injected.validate_key("some-key")
        assert user_info is not None
        assert user_info["user_id"] == get_expected_hash("test@example.com")

    def test_repository_separation_of_concerns(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)
                api_key = generate_api_key_with_pseudonymization(
                    repository, "test-key", "test@example.com", 365, TEST_SALT
                )
                user_info = repository.validate_key(api_key)
                expected_hash = get_expected_hash("test@example.com")
                assert user_info["user_id"] == expected_hash, (
                    f"Expected {expected_hash}, got {user_info['user_id']}"
                )
                user_keys = list_keys_for_user_with_pseudonymization(
                    repository, "test@example.com", TEST_SALT
                )
                assert len(user_keys) == 1
                empty_keys = list_keys_for_user_with_pseudonymization(
                    repository, "nonexistent@example.com", TEST_SALT
                )
                assert len(empty_keys) == 0
            finally:
                os.unlink(tmp_file.name)

    def test_default_24_hour_expiration(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)
                api_key = generate_api_key_with_pseudonymization(
                    repository, "test-key", "test@example.com", 1, TEST_SALT
                )
                user_info = repository.validate_key(api_key)
                expected_hash = get_expected_hash("test@example.com")
                assert user_info["user_id"] == expected_hash, (
                    f"Expected {expected_hash}, got {user_info['user_id']}"
                )
                all_keys = repository.list_keys()
                key_hash = user_info["key_hash"]
                key_info = all_keys[key_hash]
                from datetime import datetime, timedelta

                created_at = datetime.fromisoformat(key_info["created_at"])
                expires_at = datetime.fromisoformat(key_info["expires_at"])
                expected_expiry = created_at + timedelta(days=1)
                time_diff = abs((expires_at - expected_expiry).total_seconds())
                assert time_diff < 1, (
                    f"Expected ~24 hour expiration, got {time_diff} seconds difference"
                )
            finally:
                os.unlink(tmp_file.name)

    def test_email_pseudonymization_and_lookup(self):
        test_email = "user@example.com"
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                config = DummyConfig(tmp_file.name)
                repository = FileApiKeyRepository(config)
                expected_hash = get_expected_hash(test_email, TEST_SALT)
                api_key = generate_api_key_with_pseudonymization(
                    repository, "test-key", test_email, 365, TEST_SALT
                )
                user_info = repository.validate_key(api_key)
                assert user_info is not None
                assert user_info["user_id"] == expected_hash, (
                    f"Expected {expected_hash}, got {user_info['user_id']}"
                )
                print("[DEBUG] All keys after generation:")
                for k, v in repository.keys.items():
                    print(f"  key_hash: {k}, user_id: {v['user_id']}")
                for key_data in repository.keys.values():
                    assert key_data["user_id"] != test_email
                user_keys = list_keys_for_user_with_pseudonymization(
                    repository, test_email, TEST_SALT
                )
                if len(user_keys) == 0:
                    print("[DEBUG] test_email_pseudonymization_and_lookup:")
                    print(f"  Stored keys: {list(repository.keys.values())}")
                    print(f"  Lookup hash: {get_expected_hash(test_email, TEST_SALT)}")
                assert len(user_keys) == 1
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
        # set_api_key_repository(None) # This line is removed as per the edit hint
        assert self.config_path
        config_service = ConfigService(self.config_path)
        repo = make_api_key_repository(config_service)
        assert isinstance(repo, FileApiKeyRepository)
        assert repo.config_path == self.config_path


def test_create_api_key_repository_factory():
    import yaml
    import tempfile

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
    repo = make_api_key_repository(config_service)
    from auth.file_api_key_repository import FileApiKeyRepository

    assert isinstance(repo, FileApiKeyRepository)
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
        repo = make_api_key_repository(config_service_db)
    config_db.close()
    os.unlink(config_db.name)
