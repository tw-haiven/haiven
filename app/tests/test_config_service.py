# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from typing import List

import pytest
from shared.models.default_models import DefaultModels
from shared.models.embedding_model import EmbeddingModel
from shared.models.model import Model
from shared.services.config_service import ConfigService


@pytest.fixture(scope="class")
def setup_class(request):
    # given I have a valid config file
    request.cls.knowledge_pack_path = "teams"
    request.cls.active_model_providers = "Azure,GCP,some_provider"
    request.cls.model_id = "azure-gpt35"
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
    agent_info:
      region_name: "test-region"
      enabled_agent_ids : "abc,xyz"
      enabled_agent_alias_ids : "123,456"
    
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
            ConfigService.load_models(path)
        assert str(e.value) == f"Path {path} is not valid"

    def test_config_initialization(self):
        models: List[Model] = ConfigService.load_models(self.config_path)
        assert isinstance(models, list)
        assert all(isinstance(model, Model) for model in models)

        assert len(models) == 2

        model: Model = models[0]
        assert model.id == self.model_id
        assert model.name == self.name
        assert model.provider == self.provider

        feature = model.features[0]
        assert feature == feature

        assert model.config["base_url"] == self.base_url
        assert model.config["api_version"] == self.api_version
        assert model.config["azure_deployment"] == self.deployment_name
        assert model.config["api_key"] == self.api_key

        embedding: EmbeddingModel = ConfigService.load_embedding_model(self.config_path)

        assert isinstance(embedding, EmbeddingModel)

        assert embedding.id == self.embedding_id
        assert embedding.name == self.embedding_name
        assert embedding.provider == self.embedding_provider

        assert embedding.config["base_url"] == self.embedding_base_url
        assert embedding.config["api_version"] == self.embedding_api_version
        assert embedding.config["azure_deployment"] == self.embedding_deployment_name
        assert embedding.config["api_key"] == self.api_key

        knowledge_pack_path = ConfigService.load_knowledge_pack_path(self.config_path)
        assert knowledge_pack_path == self.knowledge_pack_path

        default_models = ConfigService.load_default_models(self.config_path)
        assert isinstance(default_models, DefaultModels)
        assert default_models.chat == self.model_id
        assert default_models.vision == self.model_id + "_2"
        assert default_models.embeddings == self.embedding_id

        enabled_providers = ConfigService.load_enabled_providers(self.config_path)
        assert isinstance(enabled_providers, list)
        assert all(
            provider in enabled_providers
            for provider in self.active_model_providers.split(",")
        )

        enabled_agents = ConfigService.load_agent_info(self.config_path)
        assert enabled_agents["region_name"] == "test-region"
        assert enabled_agents["enabled_agent_ids"] == ["abc", "xyz"]
        assert enabled_agents["enabled_agent_alias_ids"] == ["123", "456"]

    def test_config_loads_team_from_env_var_values(self):
        knowledge_pack_path = "folder/path"

        config_content = """
        knowledge_pack_path: ${KNOWLEDGE_PACK_PATH}
        """
        config_path = "test-env-config.yaml"
        with open(config_path, "w") as f:
            f.write(config_content)

        os.environ["KNOWLEDGE_PACK_PATH"] = knowledge_pack_path

        knowledge_pack_path: str = ConfigService.load_knowledge_pack_path(config_path)
        assert knowledge_pack_path == knowledge_pack_path

        os.remove(config_path)
