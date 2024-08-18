# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List

from embeddings.documents import KnowledgeDocument


class InMemoryEmbeddingsDB:
    def __init__(self):
        self._embeddings = {}  # Dictionary to store embeddings with key as the dictionary key and embedding as the value

    def add_embedding(self, key: str, embedding: KnowledgeDocument):
        self._embeddings[key] = embedding

    def get_document(self, key: str) -> KnowledgeDocument:
        return self._embeddings.get(key, None)

    def get_documents(self) -> List[KnowledgeDocument]:
        return list(self._embeddings.values())

    def get_keys(self) -> List[str]:
        return list(self._embeddings.keys())
