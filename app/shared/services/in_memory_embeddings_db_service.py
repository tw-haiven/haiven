# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List

from shared.models.document_embedding import DocumentEmbedding


class InMemoryEmbeddingsDB:
    def __init__(self):
        self._embeddings = {}  # Dictionary to store embeddings with key as the dictionary key and embedding as the value

    def add_embedding(self, key: str, embedding: DocumentEmbedding):
        self._embeddings[key] = embedding

    def get_embedding(self, key: str) -> DocumentEmbedding:
        return self._embeddings.get(key, None)

    def get_embeddings(self) -> List[DocumentEmbedding]:
        return list(self._embeddings.values())

    def get_keys(self) -> List[str]:
        return list(self._embeddings.keys())
