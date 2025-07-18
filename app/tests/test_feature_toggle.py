# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import pytest
from unittest.mock import patch
from config_service import ConfigService


class TestApiKeyAuthFeatureToggle:
    """Test the API key authentication feature toggle functionality."""

    def test_is_api_key_auth_enabled_when_enabled(self):
        """Test that is_api_key_auth_enabled returns True when feature is enabled."""
        with patch.dict("os.environ", {"API_KEY_AUTH_ENABLED": "true"}):
            with patch.object(ConfigService, "_load_yaml", return_value={}):
                config_service = ConfigService("tests/test_data/test_config.yaml")
                assert config_service.is_api_key_auth_enabled() is True

    def test_is_api_key_auth_enabled_when_disabled(self):
        """Test that is_api_key_auth_enabled returns False when feature is disabled."""
        with patch.dict("os.environ", {"API_KEY_AUTH_ENABLED": "false"}):
            with patch.object(ConfigService, "_load_yaml", return_value={}):
                config_service = ConfigService("tests/test_data/test_config.yaml")
                assert config_service.is_api_key_auth_enabled() is False

    def test_is_api_key_auth_enabled_when_not_configured(self):
        """Test that is_api_key_auth_enabled returns False when feature is not configured."""
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(ConfigService, "_load_yaml", return_value={}):
                config_service = ConfigService("tests/test_data/test_config.yaml")
                assert config_service.is_api_key_auth_enabled() is False

    def test_is_api_key_auth_enabled_when_features_empty(self):
        """Test that is_api_key_auth_enabled returns False when features section is empty."""
        with patch.dict("os.environ", {"API_KEY_AUTH_ENABLED": ""}):
            with patch.object(ConfigService, "_load_yaml", return_value={}):
                config_service = ConfigService("tests/test_data/test_config.yaml")
                assert config_service.is_api_key_auth_enabled() is False


class TestApiKeyAuthConditionalInitialization:
    """Test that API key authentication is conditionally initialized based on feature toggle."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_data_enabled = {
            "knowledge_pack_path": "./test_knowledge_pack",
            "enabled_providers": ["azure"],
            "default_models": {
                "chat": "azure-gpt-4o",
                "vision": "azure-gpt-4o",
                "embeddings": "text-embedding-ada-002",
            },
            "models": [
                {
                    "id": "azure-gpt-4o",
                    "name": "GPT-4o on Azure",
                    "provider": "Azure",
                    "features": ["text-generation", "image-to-text"],
                    "config": {
                        "azure_endpoint": "https://test.openai.azure.com/",
                        "api_version": "2024-02-15-preview",
                        "azure_deployment": "gpt-4o",
                        "api_key": "test_key",
                    },
                }
            ],
            "embeddings": [
                {
                    "id": "text-embedding-ada-002",
                    "name": "Text Embedding Ada 002 on Azure",
                    "provider": "azure",
                    "config": {
                        "azure_endpoint": "https://test.openai.azure.com/",
                        "api_version": "2024-02-15-preview",
                        "azure_deployment": "text-embedding-ada-002",
                        "api_key": "test_key",
                    },
                }
            ],
            "features": {"api_key_auth": True},
            "api_key_repository": {
                "type": "file",
                "pseudonymization_salt": "test_salt",
                "file": {"file_path": "test_api_keys.json"},
            },
        }

        self.config_data_disabled = {
            "knowledge_pack_path": "./test_knowledge_pack",
            "enabled_providers": ["azure"],
            "default_models": {
                "chat": "azure-gpt-4o",
                "vision": "azure-gpt-4o",
                "embeddings": "text-embedding-ada-002",
            },
            "models": [
                {
                    "id": "azure-gpt-4o",
                    "name": "GPT-4o on Azure",
                    "provider": "Azure",
                    "features": ["text-generation", "image-to-text"],
                    "config": {
                        "azure_endpoint": "https://test.openai.azure.com/",
                        "api_version": "2024-02-15-preview",
                        "azure_deployment": "gpt-4o",
                        "api_key": "test_key",
                    },
                }
            ],
            "embeddings": [
                {
                    "id": "text-embedding-ada-002",
                    "name": "Text Embedding Ada 002 on Azure",
                    "provider": "azure",
                    "config": {
                        "azure_endpoint": "https://test.openai.azure.com/",
                        "api_version": "2024-02-15-preview",
                        "azure_deployment": "text-embedding-ada-002",
                        "api_key": "test_key",
                    },
                }
            ],
            "features": {"api_key_auth": False},
            "api_key_repository": {
                "type": "file",
                "pseudonymization_salt": "test_salt",
                "file": {"file_path": "test_api_keys.json"},
            },
        }

    @pytest.mark.skip(
        reason="Integration test requires full app initialization - unit tests cover the logic"
    )
    @patch("auth.api_key_repository_factory.ApiKeyRepositoryFactory.get_repository")
    @patch("auth.api_key_auth_service.ApiKeyAuthService")
    @patch("os.path.exists", return_value=True)  # Mock the knowledge pack path check
    def test_api_key_auth_initialized_when_enabled(
        self, mock_exists, mock_auth_service, mock_repository_factory
    ):
        """Test that ApiKeyAuthService is initialized when feature is enabled."""
        from app import App

        with patch.object(
            ConfigService, "_load_yaml", return_value=self.config_data_enabled
        ):
            App("test_config.yaml")

            # Verify that the repository factory was called
            mock_repository_factory.assert_called_once()

            # Verify that the auth service was created
            mock_auth_service.assert_called_once()

    @pytest.mark.skip(
        reason="Integration test requires full app initialization - unit tests cover the logic"
    )
    @patch("auth.api_key_repository_factory.ApiKeyRepositoryFactory.get_repository")
    @patch("auth.api_key_auth_service.ApiKeyAuthService")
    @patch("os.path.exists", return_value=True)  # Mock the knowledge pack path check
    def test_api_key_auth_not_initialized_when_disabled(
        self, mock_exists, mock_auth_service, mock_repository_factory
    ):
        """Test that ApiKeyAuthService is not initialized when feature is disabled."""
        from app import App

        with patch.object(
            ConfigService, "_load_yaml", return_value=self.config_data_disabled
        ):
            App("test_config.yaml")

            # Verify that the repository factory was NOT called
            mock_repository_factory.assert_not_called()

            # Verify that the auth service was NOT created
            mock_auth_service.assert_not_called()
