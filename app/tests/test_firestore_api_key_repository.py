# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
import hashlib

from auth.firestore_api_key_repository import FirestoreApiKeyRepository
from auth.api_key_repository import ApiKeyRepository
from auth.api_key_repository_factory import ApiKeyRepositoryFactory
from config_service import ConfigService

TEST_SALT = "test_salt_123"


def get_expected_hash(email, salt=TEST_SALT):
    return hashlib.sha256((salt + email.strip().lower()).encode()).hexdigest()


class DummyFirestoreConfig:
    def load_api_key_pseudonymization_salt(self):
        return TEST_SALT

    def load_firestore_project_id(self):
        return "test-project-id"

    def load_firestore_collection_name(self):
        return "test_api_keys"

    def load_api_key_repository_type(self):
        return "firestore"


class TestFirestoreApiKeyRepository:
    """Test the Firestore API key repository implementation."""

    def setup_method(self):
        """Set up test environment."""
        # Reset the factory to ensure tests don't interfere with each other
        ApiKeyRepositoryFactory.reset()

    def teardown_method(self):
        """Clean up after tests."""
        ApiKeyRepositoryFactory.reset()

    @patch("auth.firestore_api_key_repository.firestore.Client")
    def test_firestore_api_key_repository_implements_interface(
        self, mock_firestore_client
    ):
        """Test that FirestoreApiKeyRepository implements the ApiKeyRepository interface."""
        # Mock Firestore client and collection
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_snapshot = MagicMock()

        mock_firestore_client.return_value.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc_snapshot
        mock_doc_ref.set.return_value = None
        mock_doc_ref.update.return_value = None
        mock_doc_ref.delete.return_value = None

        # Mock document snapshot for find_by_hash
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = {
            "name": "test-key",
            "user_id": get_expected_hash("test@example.com"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        config = DummyFirestoreConfig()
        repository = FirestoreApiKeyRepository(config)

        # Test that the repository implements the interface
        assert isinstance(repository, ApiKeyRepository)

        # Test basic operations
        key_hash = "test_hash"
        key_data = {
            "name": "test-key",
            "user_id": get_expected_hash("test@example.com"),
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
            "last_used": None,
            "usage_count": 0,
        }

        # Test save_key
        repository.save_key(key_hash, key_data)
        mock_doc_ref.set.assert_called_once()

        # Test find_by_hash
        result = repository.find_by_hash(key_hash)
        assert result is not None
        assert result["name"] == "test-key"
        assert result["user_id"] == get_expected_hash("test@example.com")

        # Test update_key
        updated_data = key_data.copy()
        updated_data["usage_count"] = 1
        success = repository.update_key(key_hash, updated_data)
        assert success is True
        mock_doc_ref.update.assert_called_once()

        # Test delete_key
        success = repository.delete_key(key_hash)
        assert success is True
        mock_doc_ref.delete.assert_called_once()

    @patch("auth.firestore_api_key_repository.firestore.Client")
    def test_firestore_find_all_keys(self, mock_firestore_client):
        """Test finding all API keys in Firestore."""
        # Mock Firestore client and collection
        mock_collection = MagicMock()
        mock_doc1 = MagicMock()
        mock_doc2 = MagicMock()

        mock_firestore_client.return_value.collection.return_value = mock_collection
        mock_collection.stream.return_value = [mock_doc1, mock_doc2]

        # Mock document data
        mock_doc1.id = "hash1"
        mock_doc1.to_dict.return_value = {
            "name": "key1",
            "user_id": get_expected_hash("user1@example.com"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        mock_doc2.id = "hash2"
        mock_doc2.to_dict.return_value = {
            "name": "key2",
            "user_id": get_expected_hash("user2@example.com"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "last_used": None,
            "usage_count": 5,
        }

        config = DummyFirestoreConfig()
        repository = FirestoreApiKeyRepository(config)

        # Test find_all
        all_keys = repository.find_all()
        assert len(all_keys) == 2
        assert "hash1" in all_keys
        assert "hash2" in all_keys
        assert all_keys["hash1"]["name"] == "key1"
        assert all_keys["hash2"]["name"] == "key2"

    @patch("auth.firestore_api_key_repository.firestore.Client")
    def test_firestore_find_by_user_id(self, mock_firestore_client):
        """Test finding API keys by user ID in Firestore."""
        # Mock Firestore client and collection
        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_doc = MagicMock()

        mock_firestore_client.return_value.collection.return_value = mock_collection
        mock_collection.where.return_value = mock_query
        mock_query.stream.return_value = [mock_doc]

        # Mock document data
        mock_doc.id = "hash1"
        mock_doc.to_dict.return_value = {
            "name": "user-key",
            "user_id": get_expected_hash("user@example.com"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        config = DummyFirestoreConfig()
        repository = FirestoreApiKeyRepository(config)

        # Test find_by_user_id
        user_keys = repository.find_by_user_id(get_expected_hash("user@example.com"))
        assert len(user_keys) == 1
        assert "hash1" in user_keys
        assert user_keys["hash1"]["name"] == "user-key"
        assert user_keys["hash1"]["user_id"] == get_expected_hash("user@example.com")

    @patch("auth.firestore_api_key_repository.firestore.Client")
    def test_firestore_error_handling(self, mock_firestore_client):
        """Test error handling in Firestore operations."""
        # Mock Firestore client to raise exceptions
        mock_firestore_client.return_value.collection.side_effect = Exception(
            "Firestore connection error"
        )

        config = DummyFirestoreConfig()

        # Test that initialization handles errors gracefully
        with pytest.raises(Exception):
            FirestoreApiKeyRepository(config)

    @patch("auth.firestore_api_key_repository.firestore.Client")
    def test_firestore_data_preparation(self, mock_firestore_client):
        """Test data preparation for Firestore storage and retrieval."""
        # Mock Firestore client and collection
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_snapshot = MagicMock()

        mock_firestore_client.return_value.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc_snapshot
        mock_doc_ref.set.return_value = None

        # Mock document snapshot
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = {
            "name": "test-key",
            "user_id": get_expected_hash("test@example.com"),
            "created_at": "2024-01-01T12:00:00+00:00",
            "expires_at": "2024-02-01T12:00:00+00:00",
            "last_used": None,
            "usage_count": 0,
        }

        config = DummyFirestoreConfig()
        repository = FirestoreApiKeyRepository(config)

        # Test data preparation for storage
        key_data = {
            "name": "test-key",
            "user_id": get_expected_hash("test@example.com"),
            "created_at": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "expires_at": datetime(2024, 2, 1, 12, 0, 0, tzinfo=timezone.utc),
            "last_used": None,
            "usage_count": 0,
        }

        # Test save_key with datetime objects
        repository.save_key("test_hash", key_data)

        # Verify that datetime objects were converted to ISO strings
        call_args = mock_doc_ref.set.call_args[0][0]
        assert isinstance(call_args["created_at"], str)
        assert isinstance(call_args["expires_at"], str)
        assert call_args["created_at"] == "2024-01-01T12:00:00+00:00"
        assert call_args["expires_at"] == "2024-02-01T12:00:00+00:00"

        # Test data preparation for retrieval
        result = repository.find_by_hash("test_hash")
        assert result is not None
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["expires_at"], datetime)

    def test_firestore_config_validation(self):
        """Test that Firestore configuration validation works correctly."""
        # Test with missing Firestore configuration
        config = MagicMock()
        config.load_api_key_repository_type.return_value = "firestore"
        config.load_firestore_project_id.side_effect = ValueError(
            "Firestore configuration required"
        )

        with pytest.raises(ValueError, match="Firestore configuration required"):
            FirestoreApiKeyRepository(config)

    @patch("auth.firestore_api_key_repository.firestore.Client")
    def test_firestore_repository_factory_integration(self, mock_firestore_client):
        """Test that FirestoreApiKeyRepository works with the repository factory."""
        # Mock Firestore client and collection
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_snapshot = MagicMock()

        mock_firestore_client.return_value.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc_snapshot
        mock_doc_ref.set.return_value = None

        # Mock document snapshot
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = {
            "name": "test-key",
            "user_id": get_expected_hash("test@example.com"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        # Create a temporary config file
        with tempfile.NamedTemporaryFile(delete=False, mode="w+") as tmp_file:
            config_data = {
                "api_key_repository": {
                    "type": "firestore",
                    "pseudonymization_salt": TEST_SALT,
                    "firestore": {
                        "project_id": "test-project-id",
                        "collection_name": "test_api_keys",
                    },
                },
                "default_models": {"chat": "", "vision": "", "embeddings": ""},
                "models": [],
                "embeddings": [],
                "knowledge_pack_path": "./",
                "enabled_providers": [],
            }
            import yaml

            yaml.dump(config_data, tmp_file)
            tmp_file.flush()
            config_path = tmp_file.name

        try:
            config_service = ConfigService(config_path)
            repository = ApiKeyRepositoryFactory.get_repository(config_service)

            assert isinstance(repository, FirestoreApiKeyRepository)

            # Test basic operations
            key_hash = "test_hash"
            key_data = {
                "name": "test-key",
                "user_id": get_expected_hash("test@example.com"),
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
                "last_used": None,
                "usage_count": 0,
            }

            repository.save_key(key_hash, key_data)
            result = repository.find_by_hash(key_hash)
            assert result is not None

        finally:
            os.unlink(config_path)


@pytest.mark.integration
class TestFirestoreApiKeyRepositoryIntegration:
    """Integration tests for Firestore API key repository using emulator."""

    def setup_method(self):
        """Set up Firestore emulator for integration tests."""
        # Set up Firestore emulator environment
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8090"
        ApiKeyRepositoryFactory.reset()

    def teardown_method(self):
        """Clean up after integration tests."""
        if "FIRESTORE_EMULATOR_HOST" in os.environ:
            del os.environ["FIRESTORE_EMULATOR_HOST"]
        ApiKeyRepositoryFactory.reset()

    @pytest.mark.skipif(
        not os.getenv("FIRESTORE_EMULATOR_HOST")
        or os.getenv("FIRESTORE_EMULATOR_HOST") != "localhost:8090",
        reason="Firestore emulator not available on localhost:8090",
    )
    def test_firestore_emulator_integration(self):
        """Test Firestore operations with the emulator."""
        # This test requires the Firestore emulator to be running
        # It can be started with: gcloud emulators firestore start
        config = DummyFirestoreConfig()
        repository = FirestoreApiKeyRepository(config)

        # Test basic CRUD operations
        key_hash = "test_integration_hash"
        key_data = {
            "name": "integration-test-key",
            "user_id": get_expected_hash("integration@example.com"),
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
            "last_used": None,
            "usage_count": 0,
        }

        # Test save
        repository.save_key(key_hash, key_data)

        # Test find
        result = repository.find_by_hash(key_hash)
        assert result is not None
        assert result["name"] == "integration-test-key"
        assert result["user_id"] == get_expected_hash("integration@example.com")

        # Test update
        updated_data = key_data.copy()
        updated_data["usage_count"] = 1
        success = repository.update_key(key_hash, updated_data)
        assert success is True

        # Test find after update
        updated_result = repository.find_by_hash(key_hash)
        assert updated_result["usage_count"] == 1

        # Test delete
        success = repository.delete_key(key_hash)
        assert success is True

        # Test find after delete
        deleted_result = repository.find_by_hash(key_hash)
        assert deleted_result is None
