# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from typing import List

import yaml
from dotenv import load_dotenv
from teamai_cli.models.embedding_model import EmbeddingModel


class ConfigService:
    def __init__(self, env_file_path: str = ".env"):
        self.env_file_path = env_file_path

    def load_embeddings(self, path: str = "config.yaml") -> List[EmbeddingModel]:
        """
        Load a List of embedding models from a YAML config file.

        Args:
            path (str): The path to the YAML file.

        Returns:
            EmbeddingModel: The loaded embedding model for the given provider
        """
        data = _load_yaml(path, self.env_file_path)

        embeddings = []
        embeddings_data_list = data["embeddings"]
        for embeddings_data in embeddings_data_list:
            embedding = EmbeddingModel(
                id=embeddings_data["id"],
                name=embeddings_data["name"],
                provider=embeddings_data["provider"],
                config=embeddings_data["config"],
            )
            embeddings.append(embedding)

        return embeddings


def _load_yaml(path: str, env_file_path: str) -> dict:
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

    yaml.SafeLoader.add_constructor("tag:yaml.org,2002:timestamp", _string_constructor)

    with open(path, "r") as file:
        try:
            data = yaml.load(file, Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            print(exc)

    return _resolve_config_values(data, env_file_path)


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


def _resolve_config_values(config: dict[str, str], env_file_path: str):
    load_dotenv(env_file_path)
    for key, value in config.items():
        if isinstance(value, dict):
            _resolve_config_values(value, env_file_path)
        elif isinstance(value, list):
            _resolve_config_list_values(config, key, value, env_file_path)
        else:
            config[key] = _replace_by_env_var(config[key])
            if _is_comma_separated_list(config[key]):
                config[key] = config[key].split(",")

    return config


def _is_comma_separated_list(value: str) -> bool:
    return isinstance(value, str) and "," in value


def _resolve_config_list_values(config, key, value, env_file_path):
    list = []
    for i, item in enumerate(value):
        if isinstance(item, dict):
            list.append(_resolve_config_values(item, env_file_path))
        else:
            list.append(_replace_by_env_var(item))

    config[key] = list


def _replace_by_env_var(value):
    if value is not None and value.startswith("${") and value.endswith("}"):
        env_variable = value[2:-1]
        return os.environ.get(env_variable, "")
    else:
        return value
