# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from langchain_community.vectorstores import FAISS
import tiktoken
from shared.services.config_service import ConfigService
from shared.embeddings import Embeddings

tiktoken.encoding_for_model("gpt-3.5-turbo")
tokenizer = tiktoken.get_encoding("cl100k_base")


def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


def knowledge_base_from_filesystem(kb_folder_path) -> FAISS:
    embeddings_provider = Embeddings(ConfigService.load_embedding_model("config.yaml"))
    return embeddings_provider.generate_from_filesystem(kb_folder_path)
