# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from langchain_community.embeddings import BedrockEmbeddings, OllamaEmbeddings
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from haiven_cli.models.embedding_model import EmbeddingModel


class EmbeddingService:
    def load_embeddings(model: EmbeddingModel):
        if model.id == "" or model.id is None:
            raise ValueError("model id is not defined")

        if model.config is None:
            raise ValueError(f"model config is not defined for {model.id}")

        match model.provider.lower():
            case "openai":
                return _load_openai_embeddings(model)
            case "azure":
                return _load_azure_embeddings(model)
            case "aws":
                return _load_aws_embeddings(model)
            case "ollama":
                return _load_ollama_embeddings(model)
            case _:
                raise ValueError(
                    f"model provider is not defined in config for {model.id}"
                )


def _load_openai_embeddings(model: EmbeddingModel):
    if "model" not in model.config or _value_empty_in_model_config(
        "model", model.config
    ):
        raise ValueError(f"model field is not defined in config for {model.id}")

    if "api_key" not in model.config or _value_empty_in_model_config(
        "api_key", model.config
    ):
        raise ValueError(f"api_key is not defined in config for {model.id}")

    return OpenAIEmbeddings(
        model=model.config["model"],
        api_key=model.config["api_key"],
    )


def _load_azure_embeddings(model: EmbeddingModel):
    if "api_key" not in model.config or _value_empty_in_model_config(
        "api_key", model.config
    ):
        raise ValueError(f"api_key is not defined in config for {model.id}")

    if "azure_endpoint" not in model.config or _value_empty_in_model_config(
        "azure_endpoint", model.config
    ):
        raise ValueError(f"azure_endpoint is not defined in config for {model.id}")

    if "api_version" not in model.config or _value_empty_in_model_config(
        "api_version", model.config
    ):
        raise ValueError(f"api_version is not defined in config for {model.id}")

    if "azure_deployment" not in model.config or _value_empty_in_model_config(
        "azure_deployment", model.config
    ):
        raise ValueError(f"azure_deployment is not defined in config for {model.id}")

    return AzureOpenAIEmbeddings(
        api_key=model.config["api_key"],
        azure_endpoint=model.config["azure_endpoint"],
        api_version=model.config["api_version"],
        azure_deployment=model.config["azure_deployment"],
    )


def _load_aws_embeddings(model: EmbeddingModel):
    if "aws_region" not in model.config or _value_empty_in_model_config(
        "aws_region", model.config
    ):
        raise ValueError(f"aws_region is not defined in config for {model.id}")

    return BedrockEmbeddings(region_name=model.config["aws_region"])


def _load_ollama_embeddings(model: EmbeddingModel):
    return OllamaEmbeddings(
        base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model=model.config["model"],
    )


def _value_empty_in_model_config(value: str, config):
    return config[value] == "" or config[value] is None
