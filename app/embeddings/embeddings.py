# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from embeddings.embedding_model import EmbeddingModel


class Embeddings:
    CONST_INVALID_CONFIG_ERROR = "Invalid config for the given embedding model"

    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model: EmbeddingModel = embedding_model
        self.__text_splitter = self._load_text_splitter()
        self.__embeddings_provider = None

        if self.embedding_model.provider.lower() == "openai":
            self.__embeddings_provider = self._load_openai_embeddings()
        elif self.embedding_model.provider.lower() == "azure":
            self.__embeddings_provider = self._load_azure_embeddings()
        elif self.embedding_model.provider.lower() == "aws":
            self.__embeddings_provider = self._load_aws_embeddings()
        elif self.embedding_model.provider.lower() == "ollama":
            self.__embeddings_provider = OllamaEmbeddings(
                base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                model=self.embedding_model.config.get("model"),
            )
        else:
            raise ValueError(f"Provider {self.embedding_model.provider} not supported")

    def _get_embeddings_provider(self):
        return self.__embeddings_provider

    def _load_text_splitter(self):
        return RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            length_function=self._tiktoken_len,
            separators=["\n\n", "\n", " ", ""],
        )

    def _is_valid_aws_config(self) -> bool:
        self._validate_config_key("aws_region")
        return True

    def _load_aws_embeddings(self):
        if not self._is_valid_aws_config():
            raise ValueError(self.CONST_INVALID_CONFIG_ERROR)

        return BedrockEmbeddings(
            region_name=self.embedding_model.config.get("aws_region")
        )

    def _is_valid_openai_config(self) -> bool:
        self._validate_config_key("model")
        self._validate_config_key("api_key")

        return True

    def _load_openai_embeddings(self) -> OpenAIEmbeddings:
        if not self._is_valid_openai_config():
            raise ValueError(self.CONST_INVALID_CONFIG_ERROR)

        return OpenAIEmbeddings(
            model=self.embedding_model.config.get("model"),
            api_key=self.embedding_model.config.get("api_key"),
        )

    def _is_valid_azure_config(self) -> bool:
        self._validate_config_key("api_key")
        self._validate_config_key("azure_endpoint")
        self._validate_config_key("api_version")
        self._validate_config_key("azure_deployment")

        return True

    def _load_azure_embeddings(self) -> AzureOpenAIEmbeddings:
        if not self._is_valid_azure_config():
            raise ValueError(self.CONST_INVALID_CONFIG_ERROR)

        return AzureOpenAIEmbeddings(
            api_key=self.embedding_model.config.get("api_key"),
            azure_endpoint=self.embedding_model.config.get("azure_endpoint"),
            api_version=self.embedding_model.config.get("api_version"),
            azure_deployment=self.embedding_model.config.get("azure_deployment"),
        )

    def _validate_config_key(self, key: str):
        if not self.embedding_model.config.get(key):
            raise ValueError(f"{key} config is not set for the given embedding model")

    def _tiktoken_len(self, text) -> int:
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(text, disallowed_special=())
        return len(tokens)

    def generate_from_documents(self, text, metadata):
        chunks = self.__text_splitter.create_documents(text, metadatas=metadata)
        return FAISS.from_documents(chunks, self.__embeddings_provider)

    def generate_from_filesystem(self, kb_folder_path):
        return FAISS.load_local(
            folder_path=kb_folder_path,
            embeddings=self.__embeddings_provider,
            allow_dangerous_deserialization=True,
        )
