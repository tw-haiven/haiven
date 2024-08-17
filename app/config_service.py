# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import copy
import os
from typing import List

import yaml
from dotenv import load_dotenv
from knowledge.knowledge_pack import KnowledgePackError
from llms.default_models import DefaultModels
from embeddings.model import EmbeddingModel
from llms.model import Model


class ConfigService:
    def __init__(self, path: str = "config.yaml"):
        self.path = path

    def load_embedding_model(self) -> EmbeddingModel:
        """
        Load an embedding model from a YAML config file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            EmbeddingModel: The loaded embedding model for the given provider
        """
        data = ConfigService._load_yaml(self.path)

        default_embedding = ConfigService.load_default_models(self.path).embeddings

        embeddings_data_list = data["embeddings"]
        embedding_model_data = next(
            (item for item in embeddings_data_list if item["id"] == default_embedding),
            None,
        )

        if embedding_model_data is None:
            raise ValueError(f"Embeddings provider {default_embedding} not supported")

        embedding_model = EmbeddingModel.from_dict(embedding_model_data)
        return embedding_model

    @staticmethod
    def load_enabled_models(
        path: str = "config.yaml", features: List[str] = []
    ) -> List[Model]:
        """
        Load a list of models for the enabled providers from a YAML config file.

        Args:
            path (str): The path to the YAML file.
            features (List[str]): A list of features to filter the models by.

        Returns:
            List[Model]: The loaded models.
        """
        data = ConfigService._load_yaml(path)
        model_data_list = data["models"]
        models = []

        for model_data in model_data_list:
            model = Model.from_dict(model_data)
            models.append(model)

        filtered_models = copy.deepcopy(models)

        providers = ConfigService.load_enabled_providers(path)

        if providers and len(providers) > 0:
            filtered_models = [
                model
                for model in filtered_models
                if any(
                    model.provider.lower() == model_provider.lower()
                    for model_provider in providers
                )
            ]

        if features and len(features) > 0:
            filtered_models = [
                model
                for model in filtered_models
                if all(
                    feature.lower()
                    in [model_feature.lower() for model_feature in model.features]
                    for feature in features
                )
            ]

        return filtered_models

    @staticmethod
    def get_model(model_id: str, path: str = "config.yaml") -> Model:
        """
        Get a model by its ID.

        Args:
            model_id (str): The model ID.

        Returns:
            Model: The model.
        """
        models = ConfigService.load_enabled_models(path)
        model = next((model for model in models if model.id == model_id), None)

        if model is None:
            raise ValueError(f"Model with ID {model_id} not found")

        return model

    def load_knowledge_pack_path(self) -> str:
        """
        Load the knowledge pack path from a YAML config file.

        Args:
            config_file_path (str): The path to the YAML file.

        Returns:
            str: The knowledge pack path.
        """
        data = ConfigService._load_yaml(self.path)
        knowledge_pack_path = data["knowledge_pack_path"]

        if not os.path.exists(knowledge_pack_path):
            raise KnowledgePackError(
                f"Cannot find path to Knowledge Pack: `{knowledge_pack_path}`. Please check the `knowledge_pack_path` in your {self.path} file."
            )

        return knowledge_pack_path

    @staticmethod
    def load_enabled_providers(path: str = "config.yaml") -> List[str]:
        """
        Load the enabled providers from the specified YAML configuration file.

        Args:
            path (str, optional): The path to the YAML configuration file. Defaults to "config.yaml".

        Returns:
            List[str]: The list of enabled providers.

        """
        data = ConfigService._load_yaml(path)
        enabled_providers = data["enabled_providers"]

        if isinstance(enabled_providers, str):
            enabled_providers = enabled_providers.split(",")

        return enabled_providers

    @staticmethod
    def load_default_models(path: str = "config.yaml") -> DefaultModels:
        """
        Load the default models from a YAML file.

        Args:
            path (str): The path to the YAML file. Defaults to "config.yaml".

        Returns:
            DefaultModels: An instance of the DefaultModels config class containing the default model set for llm, vision and embeddings.

        """
        data = ConfigService._load_yaml(path)
        default_models = DefaultModels.from_dict(data["default_models"])

        return default_models

    @staticmethod
    def load_application_name(path: str = "config.yaml") -> str:
        """
        Load the application name from a YAML file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            str: The application name. Defaults to "Haiven" if not present in config file.
        """
        data = ConfigService._load_yaml(path)
        application_name = data["application_name"]
        if not application_name:
            return "Haiven"
        return application_name

    def get_default_guided_mode_model(self) -> str:
        """
        Get the default chat model from the config file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            str: The default chat model.
        """
        enabled_provider = ConfigService.load_enabled_providers(self.path)[0]
        match enabled_provider:
            case "azure":
                return "azure-gpt4"
            case "gcp":
                return "google-gemini"
            case "aws":
                return "aws-claude-v3"

    def _load_yaml(path: str) -> dict:
        """
        Load YAML data from a config file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            dict: The loaded YAML data.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path {path} is not valid")

        data = None

        yaml.SafeLoader.add_constructor(
            "tag:yaml.org,2002:timestamp", ConfigService._string_constructor
        )

        with open(path, "r") as file:
            try:
                data = yaml.load(file, Loader=yaml.SafeLoader)
            except yaml.YAMLError as exc:
                print(exc)

        return _resolve_config_values(data)

    @staticmethod
    def _string_constructor(loader, node):
        """
        Custom constructor for handling YAML strings.

        Args:
            loader: The YAML loader.
            node: The YAML node.

        Returns:
            str: The constructed string.
        """
        return loader.construct_scalar(node)


def _resolve_config_values(config: dict[str, str]):
    load_dotenv()
    for key, value in config.items():
        if isinstance(value, dict):
            _resolve_config_values(value)
        elif isinstance(value, list):
            _resolve_config_list_values(config, key, value)
        else:
            config[key] = _replace_by_env_var(config[key])
            if _is_comma_separated_list(config[key]):
                config[key] = config[key].split(",")

    return config


def _is_comma_separated_list(value: str) -> bool:
    return isinstance(value, str) and "," in value


def _resolve_config_list_values(config, key, value):
    list = []
    for i, item in enumerate(value):
        if isinstance(item, dict):
            list.append(_resolve_config_values(item))
        else:
            list.append(_replace_by_env_var(item))

    config[key] = list


def _replace_by_env_var(value):
    if value is not None and value.startswith("${") and value.endswith("}"):
        env_variable = value[2:-1]
        return os.environ.get(env_variable, "")
    else:
        return value
