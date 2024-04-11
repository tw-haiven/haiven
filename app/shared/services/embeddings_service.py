# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from pathlib import Path
from typing import List, Tuple

import frontmatter
from langchain.docstore.document import Document
from shared.embeddings import Embeddings
from shared.models.document_embedding import DocumentEmbedding
from shared.services.config_service import ConfigService
from shared.services.in_memory_embeddings_db_service import InMemoryEmbeddingsDB


class EmbeddingsService:
    _instance = None
    _embeddings_store: InMemoryEmbeddingsDB = None

    def __init__(self, embeddings_provider: Embeddings = None):
        if EmbeddingsService._instance is not None:
            raise Exception(
                "EmbeddingsService is a singleton class. Use get_instance() to get the instance."
            )

        if embeddings_provider is None:
            embedding_model = ConfigService.load_embedding_model()
            self._embeddings_provider = Embeddings(embedding_model)
        else:
            self._embeddings_provider = embeddings_provider

        if self._embeddings_store is None:
            self._embeddings_store = InMemoryEmbeddingsDB()

        EmbeddingsService._instance = self

    @staticmethod
    def get_instance():
        if EmbeddingsService._instance is None:
            raise Exception(
                "EmbeddingsService has to be initialized first. First use initialize() before using EmbeddingsService"
            )

        return EmbeddingsService._instance

    @staticmethod
    def initialize(embeddings_provider: Embeddings = None):
        if EmbeddingsService._instance is None:
            EmbeddingsService(embeddings_provider)

    @staticmethod
    def reset_instance() -> None:
        EmbeddingsService._instance = None

    @staticmethod
    def load_document(document_path: str) -> None:
        instance = EmbeddingsService.get_instance()
        instance._load_document(document_path)

    @staticmethod
    def generate_document_from_text(
        document_key: str,
        document_metadata: dict,
        content: Tuple[List[str], List[dict]],
    ) -> None:
        instance = EmbeddingsService.get_instance()
        instance._generate_document_from_text(document_key, document_metadata, content)

    @staticmethod
    def get_embedded_document(document_key: str) -> DocumentEmbedding:
        instance = EmbeddingsService.get_instance()
        return instance._embeddings_store.get_embedding(document_key)

    @staticmethod
    def get_embedded_documents() -> List[DocumentEmbedding]:
        instance = EmbeddingsService.get_instance()
        return instance._embeddings_store.get_embeddings()

    @staticmethod
    def load_knowledge_pack(knowledge_pack_path: str) -> None:
        instance = EmbeddingsService.get_instance()
        instance._load_knowledge_pack(knowledge_pack_path)

    @staticmethod
    def similarity_search_with_scores(
        query: str, k: int = 5, score_threshold: float = 0.4
    ) -> List[Tuple[Document, float]]:
        instance = EmbeddingsService.get_instance()
        return instance._similarity_search_with_scores(query, k, score_threshold)

    @staticmethod
    def similarity_search_on_single_document_with_scores(
        query: str, document_key: str, k: int = 5, score_threshold: float = 0.4
    ) -> List[Tuple[Document, float]]:
        instance = EmbeddingsService.get_instance()
        return instance._similarity_search_on_single_document_with_scores(
            query, document_key, k, score_threshold
        )

    @staticmethod
    def similarity_search_on_single_document(
        query: str, document_key: str, k: int = 5, score_threshold: float = 0.4
    ) -> List[Document]:
        instance = EmbeddingsService.get_instance()
        return instance._similarity_search_on_single_document(
            query, document_key, k, score_threshold
        )

    @staticmethod
    def similarity_search(
        query: str, k: int = 5, score_threshold: float = 0.4
    ) -> List[Document]:
        instance = EmbeddingsService.get_instance()
        return instance._similarity_search(query, k, score_threshold)

    def _get_retriever_from_file(self, kb_path: str):
        path = Path(kb_path)

        faiss = self._embeddings_provider.generate_from_filesystem(path)

        return faiss

    def _get_retriever_from_text(self, content: Tuple[List[str], List[dict]]):
        text = content[0]
        metadata = content[1]
        faiss = self._embeddings_provider.generate_from_documents(text, metadata)
        return faiss

    def _load_knowledge_pack(self, knowledge_pack_path: str) -> None:
        knowledge_files = sorted(
            [
                f
                for f in os.listdir(knowledge_pack_path)
                if f.endswith(".md") and f != "README.md"
            ]
        )

        for knowledge_file in knowledge_files:
            self._load_document(os.path.join(knowledge_pack_path, knowledge_file))

    def _load_document(self, document_path: str) -> None:
        document = frontmatter.load(document_path)
        if (
            document.metadata.get("provider")
            == self._embeddings_provider.embedding_model.provider.lower()
        ):
            folder_path = Path(document_path).parent
            kb_path = document.metadata["path"]
            kb_full_path = os.path.join(folder_path, kb_path)
            embedding = DocumentEmbedding(
                key=document.metadata["key"],
                retriever=self._get_retriever_from_file(kb_full_path),
                title=document.metadata.get("title", ""),
                source=document.metadata.get("source", ""),
                sample_question=document.metadata.get("sample_question", ""),
                description=document.metadata.get("description", ""),
                provider=document.metadata.get("provider", ""),
            )

            self._embeddings_store.add_embedding(embedding.key, embedding)

    def _generate_document_from_text(
        self,
        document_key: str,
        document_metadata: dict,
        content: Tuple[List[str], List[dict]],
    ) -> None:
        print(
            f"@debug EmbeddingsService._generate_document_from_text: metadatas={document_metadata}"
        )
        embedding = DocumentEmbedding(
            key=document_key,
            title=document_metadata.get("title", document_key),
            source=document_metadata.get("source", "source not provided"),
            sample_question=document_metadata.get("sample_question", ""),
            description=document_metadata.get("description", ""),
            provider=self._embeddings_provider.embedding_model.provider.lower(),
            retriever=self._get_retriever_from_text(content),
        )

        self._embeddings_store.add_embedding(embedding.key, embedding)

    def _similarity_search_with_scores(
        self, query: str, k: int = 5, score_threshold: float = 0.4
    ) -> List[Tuple[Document, float]]:
        similar_documents = []

        for embedding_key in self._embeddings_store.get_keys():
            print(
                f"@debug EmbeddingsService._similarity_search_with_scores searching in: embedding_key={embedding_key}"
            )
            partial_results = self._similarity_search_on_single_document_with_scores(
                query, embedding_key, k, score_threshold
            )
            print(
                f"@debug EmbeddingsService._similarity_search_with_scores: partial_results={len(partial_results)}"
            )
            similar_documents.extend(partial_results)

        similar_documents.sort(key=lambda x: x[1], reverse=False)
        similar_documents = similar_documents[:k]

        return similar_documents

    def _similarity_search_on_single_document_with_scores(
        self, query: str, document_key: str, k: int = 5, score_threshold: float = 0.4
    ) -> List[Tuple[Document, float]]:
        embedding = self._embeddings_store.get_embedding(document_key)
        similar_documents = embedding.retriever.similarity_search_with_score(
            query=query, k=k, score_threshold=score_threshold
        )

        return similar_documents

    def _similarity_search_on_single_document(
        self, query: str, key: str, k: int = 5, score_threshold: float = 0.4
    ) -> List[Document]:
        documents_with_scores = self._similarity_search_on_single_document_with_scores(
            query, key, k, score_threshold
        )
        documents = [doc for doc, _ in documents_with_scores]
        return documents

    def _similarity_search(
        self, query: str, k: int = 5, score_threshold: float = 0.4
    ) -> List[Document]:
        documents_with_scores = self._similarity_search_with_scores(
            query, k, score_threshold
        )
        documents = [doc for doc, _ in documents_with_scores]
        return documents
