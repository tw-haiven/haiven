# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import tempfile
from typing import List

import pytest
from knowledge.pack import KnowledgePackError
from llms.model_config import ModelConfig
from llms.default_models import DefaultModels
from embeddings.model import EmbeddingModel
from config_service import ConfigService
from tests.utils import get_test_data_path


@pytest.fixture(scope="class")
def setup_class(request):
    # given I have a valid config file

    request.cls.temp_dir = tempfile.TemporaryDirectory()
    request.cls.knowledge_pack_path = request.cls.temp_dir.name
    request.cls.active_model_providers = "Azure,GCP,some_provider"
    request.cls.model_id = "some-chat-model"
    request.cls.name = "GPT-3.5 on Azure"
    request.cls.provider = "some_provider"
    request.cls.feature = "text-generation"
    request.cls.base_url = "https://tw-genai-pod-openai.openai.azure.com"
    request.cls.api_version = "2023-05-15"
    request.cls.deployment_name = "genai-pod-experiments-gpt35-16k"
    request.cls.api_key = "api-key"
    request.cls.secret_api_key = r"${AZURE_API_KEY}"
    os.environ["AZURE_API_KEY"] = request.cls.api_key
    request.cls.embedding_id = "text-embedding-ada-002"
    request.cls.embedding_name = "Ada"
    request.cls.embedding_provider = "Azure"
    request.cls.embedding_base_url = "https://tw-genai-pod-openai.openai.azure.com"
    request.cls.embedding_api_version = "2023-05-15"
    request.cls.embedding_deployment_name = "genai-pod-experiments-gpt35-16k"

    config_content = f""" 
    knowledge_pack_path: {request.cls.knowledge_pack_path}
    enabled_providers: {request.cls.active_model_providers}
    default_models:
      chat: {request.cls.model_id}
      vision: {request.cls.model_id}_2
      embeddings: {request.cls.embedding_id}
    models:
      - id: {request.cls.model_id}
        name: {request.cls.name}
        provider: {request.cls.provider}
        features:
          - {request.cls.feature}
        config:
          api_key: {request.cls.secret_api_key}
          base_url: {request.cls.base_url}
          api_version: {request.cls.api_version}
          azure_deployment: {request.cls.deployment_name}
      - id: {request.cls.model_id}_2
        name: {request.cls.name}_2
        provider: {request.cls.provider}
        features:
          - {request.cls.feature}
        config:
          api_key: {request.cls.secret_api_key}
          base_url: {request.cls.base_url}
          api_version: {request.cls.api_version}
          azure_deployment: {request.cls.deployment_name}_2
    embeddings:
      - id: {request.cls.embedding_id}
        name: {request.cls.embedding_name}
        provider: {request.cls.embedding_provider}
        config:
          api_key: {request.cls.secret_api_key}
          base_url: {request.cls.embedding_base_url}
          api_version: {request.cls.embedding_api_version}
          azure_deployment: {request.cls.embedding_deployment_name}
    """

    config_path = "test-config.yaml"
    with open(config_path, "w") as f:
        f.write(config_content)

    request.cls.config_path = config_path

    def teardown_class():
        os.remove(request.cls.config_path)

    request.addfinalizer(teardown_class)


@pytest.mark.usefixtures("setup_class")
class TestConfigService:
    def test_config_initialization_fails_if_path_is_not_valid(self):
        # given I have an invalid path
        path = "invalid_path"
        # when I call the function __init__ an error should be raised
        with pytest.raises(FileNotFoundError) as e:
            ConfigService(path)
        assert str(e.value) == f"Path {path} is not valid"

    def test_config_initialization(self):
        config_service = ConfigService(self.config_path)

        models: List[ModelConfig] = config_service.load_enabled_models()
        assert isinstance(models, list)
        assert all(isinstance(model, ModelConfig) for model in models)

        assert len(models) == 2

        model: ModelConfig = models[0]
        assert model.id == self.model_id
        assert model.name == self.name
        assert model.provider == self.provider

        feature = model.features[0]
        assert feature == feature

        assert model.config["base_url"] == self.base_url
        assert model.config["api_version"] == self.api_version
        assert model.config["azure_deployment"] == self.deployment_name
        assert model.config["api_key"] == self.api_key

        embedding: EmbeddingModel = config_service.load_embedding_model()

        assert isinstance(embedding, EmbeddingModel)

        assert embedding.id == self.embedding_id
        assert embedding.name == self.embedding_name
        assert embedding.provider == self.embedding_provider

        assert embedding.config["base_url"] == self.embedding_base_url
        assert embedding.config["api_version"] == self.embedding_api_version
        assert embedding.config["azure_deployment"] == self.embedding_deployment_name
        assert embedding.config["api_key"] == self.api_key

        knowledge_pack_path = config_service.load_knowledge_pack_path()
        assert knowledge_pack_path == self.knowledge_pack_path

        default_models = config_service.load_default_models()
        assert isinstance(default_models, DefaultModels)
        assert default_models.chat == self.model_id
        assert default_models.vision == self.model_id + "_2"
        assert default_models.embeddings == self.embedding_id

        enabled_providers = config_service.load_enabled_providers()
        assert isinstance(enabled_providers, list)
        assert all(
            provider in enabled_providers
            for provider in self.active_model_providers.split(",")
        )

    def test_config_loads_team_from_env_var_values(self):
        knowledge_pack_path = "folder/path"

        config_content = """
        knowledge_pack_path: ${KNOWLEDGE_PACK_PATH}
        """
        config_path = "test-env-config.yaml"
        with open(config_path, "w") as f:
            f.write(config_content)

        os.environ["KNOWLEDGE_PACK_PATH"] = self.temp_dir.name

        config_service = ConfigService(config_path)

        knowledge_pack_path: str = config_service.load_knowledge_pack_path()
        assert knowledge_pack_path == knowledge_pack_path

        os.remove(config_path)

    def test_load_configured_default_chat_model(self):
        config_service = ConfigService(self.config_path)

        chat_model: str = config_service.get_default_chat_model()
        assert chat_model == "some-chat-model"

    def test_load_hard_coded_default_chat_model_if_not_set_in_config(self):
        config_content = """
enabled_providers: azure
default_models: 
  chat: ${ENABLED_CHAT_MODEL}
  vision: some-vision-model
models:
  - id: azure-gpt4
    name: GPT-4
    provider: azure
          """
        config_path = "test-env-config.yaml"
        with open(get_test_data_path() + "/" + config_path, "w") as f:
            f.write(config_content)
            f.flush()

            config_service = ConfigService(get_test_data_path() + "/" + config_path)
            config_service.get_default_chat_model()

        chat_model: str = config_service.get_default_chat_model()
        assert chat_model == "azure-gpt4"

    def test_should_raise_error_when_knowledge_pack_not_found(self):
        exception_raised = False
        try:
            config_content = """
knowledge_pack_path: /non/existent/path
              """
            config_path = "test-env-config.yaml"
            with open(get_test_data_path() + "/" + config_path, "w") as f:
                f.write(config_content)
                f.flush()

                config_service = ConfigService(get_test_data_path() + "/" + config_path)
                config_service.load_knowledge_pack_path()

        except KnowledgePackError as e:
            assert "Pack" in e.message
            exception_raised = True

        assert exception_raised

        os.remove(get_test_data_path() + "/" + config_path)
