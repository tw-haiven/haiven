# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from typing import List

import pytest
from shared.models.default_models import DefaultModels
from shared.models.embedding_model import EmbeddingModel
from shared.models.knowledge_pack import Domain, KnowledgePack
from shared.models.model import Model
from shared.services.config_service import ConfigService


class TestConfigService:
    def test_config_initialization_fails_if_path_is_not_valid(self):
        # given I have an invalid path
        path = "invalid_path"
        # when I call the function __init__ an error should be raised
        with pytest.raises(FileNotFoundError) as e:
            ConfigService.load_models(path)
        assert str(e.value) == f"Path {path} is not valid"

    def test_config_initialization(self):
        # given I have a valid config file
        domain_name = "teamai"
        active_model_providers = "Azure,GCP,some_provider"
        model_id = "azure-gpt35"
        name = "GPT-3.5 on Azure"
        provider = "some_provider"
        feature = "text-generation"
        base_url = "https://tw-genai-pod-openai.openai.azure.com"
        api_version = "2023-05-15"
        deployment_name = "genai-pod-experiments-gpt35-16k"
        api_key = "api-key"
        secret_api_key = r"${AZURE_API_KEY}"
        os.environ["AZURE_API_KEY"] = api_key
        embedding_id = "text-embedding-ada-002"
        embedding_name = "Ada"
        embedding_provider = "Azure"
        embedding_base_url = "https://tw-genai-pod-openai.openai.azure.com"
        embedding_api_version = "2023-05-15"
        embedding_deployment_name = "genai-pod-experiments-gpt35-16k"
        knowledge_pack_path = "teams"

        config_content = f""" 
        knowledge_pack:
          path: {knowledge_pack_path}
          domain:
            name: {domain_name}
        enabled_providers: {active_model_providers}
        default_models:
          chat: {model_id}
          vision: {model_id}_2
          embeddings: {embedding_id}
        models:
          - id: {model_id}
            name: {name}
            provider: {provider}
            features:
              - {feature}
            config:
              api_key: {secret_api_key}
              base_url: {base_url}
              api_version: {api_version}
              azure_deployment: {deployment_name}
          - id: {model_id}_2
            name: {name}_2
            provider: {provider}
            features:
              - {feature}
            config:
              api_key: {secret_api_key}
              base_url: {base_url}
              api_version: {api_version}
              azure_deployment: {deployment_name}_2
        embeddings:
          - id: {embedding_id}
            name: {embedding_name}
            provider: {embedding_provider}
            config:
              api_key: {secret_api_key}
              base_url: {embedding_base_url}
              api_version: {embedding_api_version}
              azure_deployment: {embedding_deployment_name}
        """

        config_path = "test-config.yaml"
        with open(config_path, "w") as f:
            f.write(config_content)

        models: List[Model] = ConfigService.load_models(config_path)
        assert isinstance(models, list)
        assert all(isinstance(model, Model) for model in models)

        assert len(models) == 2

        model: Model = models[0]
        assert model.id == model_id
        assert model.name == name
        assert model.provider == provider

        feature = model.features[0]
        assert feature == feature

        assert model.config["base_url"] == base_url
        assert model.config["api_version"] == api_version
        assert model.config["azure_deployment"] == deployment_name
        assert model.config["api_key"] == api_key

        embedding: EmbeddingModel = ConfigService.load_embedding_model(config_path)

        assert isinstance(embedding, EmbeddingModel)

        assert embedding.id == embedding_id
        assert embedding.name == embedding_name
        assert embedding.provider == embedding_provider

        assert embedding.config["base_url"] == embedding_base_url
        assert embedding.config["api_version"] == embedding_api_version
        assert embedding.config["azure_deployment"] == embedding_deployment_name
        assert embedding.config["api_key"] == api_key

        knowledge_pack = ConfigService.load_knowledge_pack(config_path)
        assert isinstance(knowledge_pack, KnowledgePack)
        assert knowledge_pack.path == knowledge_pack_path

        domain = knowledge_pack.domain
        assert isinstance(domain, Domain)
        assert domain.name == domain_name

        default_models = ConfigService.load_default_models(config_path)
        assert isinstance(default_models, DefaultModels)
        assert default_models.chat == model_id
        assert default_models.vision == model_id + "_2"
        assert default_models.embeddings == embedding_id

        enabled_providers = ConfigService.load_enabled_providers(config_path)
        assert isinstance(enabled_providers, list)
        assert all(
            provider in enabled_providers
            for provider in active_model_providers.split(",")
        )

        # clean up
        os.remove(config_path)

    def test_config_loads_team_from_env_var_values(self):
        # given I have a valid config file
        domain_name = "teamai"
        knowledge_pack_path = "folder/path"

        config_content = """
        knowledge_pack:
          path: ${KNOWLEDGE_PACK_PATH}
          domain:
            name: ${DOMAIN_NAME}
        """
        config_path = "test config.yaml"
        with open(config_path, "w") as f:
            f.write(config_content)

        os.environ["KNOWLEDGE_PACK_PATH"] = knowledge_pack_path
        os.environ["DOMAIN_NAME"] = domain_name

        knowledge_pack: KnowledgePack = ConfigService.load_knowledge_pack(config_path)
        assert isinstance(knowledge_pack, KnowledgePack)

        assert knowledge_pack.path == knowledge_pack_path

        domain = knowledge_pack.domain
        assert isinstance(domain, Domain)
        assert domain.name == domain_name

        # clean up
        os.remove(config_path)
