# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import pytest
import unittest
from haiven_cli.services.config_service import ConfigService

TEST_ENV_FILE_PATH = ".test-env-file"


class TestConfigService(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(TEST_ENV_FILE_PATH):
            os.remove(TEST_ENV_FILE_PATH)

    def test_config_initialization_fails_if_path_is_not_valid(self):
        # given I have an invalid path
        path = "invalid_path"
        # when I call the function __init__ an error should be raised
        with pytest.raises(FileNotFoundError) as e:
            ConfigService(TEST_ENV_FILE_PATH).load_embeddings(path)
        assert str(e.value) == f"Path {path} is not valid"

    def test_config_initialization(self):
        # given I have a valid config file
        api_key = "api-key"
        secret_api_key = r"${AZURE_API_KEY}"
        with open(TEST_ENV_FILE_PATH, "w") as f:
            f.write(f"AZURE_API_KEY={api_key}")
        first_embedding_id = "text-embedding-ada-002"
        first_embedding_name = "Ada"
        first_embedding_provider = "Azure"
        first_embedding_base_url = "https://tw-genai-pod-openai.openai.azure.com"
        second_embedding_id = "text-embedding-ada-0021"
        second_embedding_name = "Adaa"
        second_embedding_provider = "Azuree"
        second_embedding_base_url = "https://twwww-genai-pod-openai.openai.azure.com"

        config_content = f"""
        embeddings:
          - id: {first_embedding_id}
            name: {first_embedding_name}
            provider: {first_embedding_provider}
            config:
              api_key: {secret_api_key}
              base_url: {first_embedding_base_url}
          - id: {second_embedding_id}
            name: {second_embedding_name}
            provider: {second_embedding_provider}
            config:
              api_key: {secret_api_key}
              base_url: {second_embedding_base_url}
        """

        config_path = "test-config.yaml"
        with open(config_path, "w") as f:
            f.write(config_content)

        embeddings = ConfigService(TEST_ENV_FILE_PATH).load_embeddings(config_path)

        first_embedding = embeddings[0]
        assert first_embedding.id == first_embedding_id
        assert first_embedding.name == first_embedding_name
        assert first_embedding.provider == first_embedding_provider

        first_embedding_config = first_embedding.config
        assert first_embedding_config["api_key"] == api_key
        assert first_embedding_config["base_url"] == first_embedding_base_url

        second_embedding = embeddings[1]
        assert second_embedding.id == second_embedding_id
        assert second_embedding.name == second_embedding_name
        assert second_embedding.provider == second_embedding_provider

        second_embedding_config = second_embedding.config
        assert second_embedding_config["api_key"] == api_key
        assert second_embedding_config["base_url"] == second_embedding_base_url

        # clean up
        os.remove(config_path)
