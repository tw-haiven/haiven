# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from pathlib import Path
from typing import List, Tuple

import frontmatter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from shared.embeddings.embeddings import Embeddings
from shared.embeddings.document_embedding import DocumentEmbedding
from shared.config_service import ConfigService
from shared.embeddings.in_memory_embeddings_db_service import InMemoryEmbeddingsDB


class EmbeddingsService:
    """
    EmbeddingsService is a singleton class responsible for managing embeddings operations. It provides functionalities to initialize and retrieve the singleton instance, load embeddings, and perform similarity searches on documents. The class uses an embeddings provider to generate embeddings and an in-memory database to store and retrieve embeddings.

    Attributes:
        _instance (EmbeddingsService): The singleton instance of the EmbeddingsService.
        _embeddings_stores (dict[str, InMemoryEmbeddingsDB]): The in-memory database for storing embeddings.
        _embeddings_provider (Embeddings): The provider used for generating embeddings.
    """

    _instance = None
    _embeddings_stores: dict[str, InMemoryEmbeddingsDB] = None

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

        if self._embeddings_stores is None:
            self._embeddings_stores = {}
            self._embeddings_stores["base"] = InMemoryEmbeddingsDB()

        EmbeddingsService._instance = self

    @staticmethod
    def get_instance():
        """
        Returns the singleton instance of the EmbeddingsService. If the instance has not been initialized, it raises an exception.

        Returns:
            EmbeddingsService: The singleton instance of the EmbeddingsService.

        Raises:
            Exception: If the EmbeddingsService has not been initialized.
        """
        if EmbeddingsService._instance is None:
            raise Exception(
                "EmbeddingsService has to be initialized first. First use initialize() before using EmbeddingsService"
            )

        return EmbeddingsService._instance

    @staticmethod
    def initialize(embeddings_provider: Embeddings = None):
        """
        Initializes the EmbeddingsService singleton with an optional embeddings provider. This method must be called before any other operations if the EmbeddingsService instance has not been created.

        Parameters:
            embeddings_provider (Embeddings, optional): The embeddings provider to use. Defaults to None, in which case the default provider is loaded.
        """
        if EmbeddingsService._instance is None:
            EmbeddingsService(embeddings_provider)

    @staticmethod
    def reset_instance() -> None:
        """
        Resets the singleton instance of the EmbeddingsService. This is useful for testing purposes or reinitializing the service with different configurations.
        """
        EmbeddingsService._embeddings_stores = {}
        EmbeddingsService._instance = None

    @staticmethod
    def load_base_document(document_path: str) -> None:
        """
        Loads a document from the specified path, generates its embedding using the configured embeddings provider, and stores it in the in-memory database. This method is static and can be called without instantiating the class.

        Parameters:
            document_path (str): The file system path to the document to be loaded.
        """
        instance = EmbeddingsService.get_instance()
        instance._load_document(document_path, context="base")

    @staticmethod
    def generate_base_document_from_text(
        document_key: str,
        document_metadata: dict,
        content: Tuple[List[str], List[dict]],
    ) -> None:
        """
        Generates a document embedding from provided text content and metadata, then stores it. This allows for dynamic creation of document embeddings from text that may not be persisted to disk.

        Parameters:
            document_key (str): A unique key identifying the document.
            document_metadata (dict): Metadata associated with the document.
            content (Tuple[List[str], List[dict]]): The text content of the document and any associated metadata.
        """
        instance = EmbeddingsService.get_instance()
        instance._generate_document_from_text(
            document_key=document_key,
            document_metadata=document_metadata,
            content=content,
            context="base",
        )

    @staticmethod
    def load_knowledge_base(knowledge_pack_path: str) -> None:
        """
        Loads multiple documents from a specified directory, often referred to as a knowledge pack. Each document in the directory is loaded, processed, and its embedding is stored.

        Parameters:
            knowledge_pack_path (str): The file system path to the directory containing the knowledge pack documents.
        """
        instance = EmbeddingsService.get_instance()
        instance._load_knowledge_pack(path=knowledge_pack_path, name="base")

    @staticmethod
    def load_knowledge_context(context_name: str, context_path: str) -> None:
        """
        Loads multiple documents from a specified directory, often referred to as a knowledge pack. Each document in the directory is loaded, processed, and its embedding is stored.

        Parameters:
            context_name (str): The name of the context.
            context_path (str): The file system path to the directory containing the context documents.
        """
        instance = EmbeddingsService.get_instance()
        instance._load_knowledge_pack(path=context_path, name=context_name)

    @staticmethod
    def get_embedded_document(document_key: str) -> DocumentEmbedding:
        """
        Retrieves a specific document embedding by its key. This method is useful for accessing the embedding of a previously loaded or generated document.

        Parameters:
            document_key (str): The key of the document whose embedding is to be retrieved.

        Returns:
            DocumentEmbedding: The embedding of the specified document.
        """
        instance = EmbeddingsService.get_instance()
        for _, store in instance._embeddings_stores.items():
            embedding = store.get_embedding(document_key)
            if embedding is not None:
                return embedding

        return None

    @staticmethod
    def get_embedded_documents(
        context: str = None, include_base_context=True
    ) -> List[DocumentEmbedding]:
        """
        Retrieves all stored document embeddings. This method provides access to the complete set of embeddings currently managed by the service.

        Parameters:
            context (str, optional): The context to retrieve embeddings from. If None, retrieves embeddings only from base context. Defaults to None.

        Returns:
            List[DocumentEmbedding]: A list of all document embeddings stored in the service.
        """
        instance = EmbeddingsService.get_instance()
        all_embeddings = []

        if include_base_context:
            store = instance._embeddings_stores["base"]
            all_embeddings.extend(store.get_embeddings())

        if context is not None and context != "":
            store = instance._embeddings_stores[context]
            all_embeddings.extend(store.get_embeddings())

        return all_embeddings

    @staticmethod
    def similarity_search_with_scores(
        query: str, context: str, k: int = 5, score_threshold: float = None
    ) -> List[Tuple[Document, float]]:
        """
        Performs a similarity search across all stored document embeddings, returning a list of documents and their similarity scores relative to the query. This method supports specifying the number of results (k) and an optional score threshold.

        Parameters:
            query (str): The search query.
            context (str): The context to search within.
            k (int, optional): The number of results to return. Defaults to 5.
            score_threshold (float, optional): The minimum similarity score for a document to be included in the results. Defaults to None.

        Returns:
            List[Tuple[Document, float]]: A list of tuples, each containing a Document and its similarity score.
        """
        instance = EmbeddingsService.get_instance()
        return instance._similarity_search_with_scores(
            query, context, k, score_threshold
        )

    @staticmethod
    def similarity_search_on_single_document_with_scores(
        query: str,
        document_key: str,
        context: str,
        k: int = 5,
        score_threshold: float = None,
    ) -> List[Tuple[Document, float]]:
        """
        Performs a similarity search on a single document's embedding, returning similar documents and their scores. This method is useful for focused searches within a specific document's context.

        Parameters:
            query (str): The search query.
            document_key (str): The key of the document to search within.
            context (str): The context to search within.
            k (int, optional): The number of results to return. Defaults to 5.
            score_threshold (float, optional): The minimum similarity score for a document to be included in the results. Defaults to None.

        Returns:
            List[Tuple[Document, float]]: A list of tuples, each containing a Document and its similarity score.
        """
        instance = EmbeddingsService.get_instance()
        return instance._similarity_search_on_single_document_with_scores(
            query, document_key, context, k, score_threshold
        )

    @staticmethod
    def similarity_search_on_single_document(
        query: str,
        document_key: str,
        context: str,
        k: int = 5,
        score_threshold: float = None,
    ) -> List[Document]:
        """
        Similar to the method above but returns only the documents without their similarity scores. This provides a simpler interface when only the documents are needed.

        Parameters:
            query (str): The search query.
            document_key (str): The key of the document to search within.
            context (str): The context to search within.
            k (int, optional): The number of results to return. Defaults to 5.
            score_threshold (float, optional): The minimum similarity score for a document to be included in the results. Defaults to None.

        Returns:
            List[Document]: A list of documents that are similar to the query.
        """
        instance = EmbeddingsService.get_instance()
        return instance._similarity_search_on_single_document(
            query, document_key, context, k, score_threshold
        )

    @staticmethod
    def similarity_search(
        query: str, context: str, k: int = 5, score_threshold: float = None
    ) -> List[Document]:
        """
        Performs a similarity search across all documents, returning only the documents that match the query criteria. This method abstracts away the scores for use cases where only the matching documents are required.

        Parameters:
            query (str): The search query.
            context (str): The context to search within.
            k (int, optional): The number of results to return. Defaults to 5.
            score_threshold (float, optional): The minimum similarity score for a document to be included in the results. Defaults to None.

        Returns:
            List[Document]: A list of documents that are similar to the query.
        """
        instance = EmbeddingsService.get_instance()
        return instance._similarity_search(query, context, k, score_threshold)

    def _get_or_create_embeddings_db_for_context(
        self, context: str
    ) -> InMemoryEmbeddingsDB:
        if context not in self._embeddings_stores:
            self._embeddings_stores[context] = InMemoryEmbeddingsDB()

        return self._embeddings_stores[context]

    def _get_retriever_from_file(self, kb_path: str) -> FAISS:
        path = Path(kb_path)

        faiss = self._embeddings_provider.generate_from_filesystem(path)

        return faiss

    def _get_retriever_from_text(self, content: Tuple[List[str], List[dict]]) -> FAISS:
        text = content[0]
        metadata = content[1]
        faiss = self._embeddings_provider.generate_from_documents(text, metadata)
        return faiss

    def _load_knowledge_pack(self, path: str, name: str) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"The specified path does not exist, no embeddings will be loaded: {path}"
            )

        knowledge_files = sorted(
            [f for f in os.listdir(path) if f.endswith(".md") and f != "README.md"]
        )

        if knowledge_files is not None:
            self._embeddings_stores[name] = InMemoryEmbeddingsDB()

        for knowledge_file in knowledge_files:
            self._load_document(
                document_path=os.path.join(path, knowledge_file), context=name
            )

    def _load_document(self, document_path: str, context: str) -> None:
        document = frontmatter.load(document_path)
        if (
            document.metadata.get("provider")
            == self._embeddings_provider.embedding_model.provider.lower()
        ):
            folder_path = Path(document_path).parent
            kb_path = document.metadata["path"]
            kb_full_path = os.path.join(folder_path, kb_path)
            embedding = DocumentEmbedding(
                context=context,
                key=document.metadata["key"],
                title=document.metadata.get("title", ""),
                source=document.metadata.get("source", ""),
                sample_question=document.metadata.get("sample_question", ""),
                description=document.metadata.get("description", ""),
                provider=document.metadata.get("provider", ""),
                retriever=self._get_retriever_from_file(kb_full_path),
            )

            store_for_context = self._get_or_create_embeddings_db_for_context(context)

            store_for_context.add_embedding(embedding.key, embedding)

    def _generate_document_from_text(
        self,
        document_key: str,
        document_metadata: dict,
        content: Tuple[List[str], List[dict]],
        context: str,
    ) -> None:
        embedding = DocumentEmbedding(
            context=context,
            key=document_key,
            title=document_metadata.get("title", document_key),
            source=document_metadata.get("source", "source not provided"),
            sample_question=document_metadata.get("sample_question", ""),
            description=document_metadata.get("description", ""),
            provider=self._embeddings_provider.embedding_model.provider.lower(),
            retriever=self._get_retriever_from_text(content),
        )

        store_for_context = self._get_or_create_embeddings_db_for_context(context)
        store_for_context.add_embedding(embedding.key, embedding)

    def _similarity_search_with_scores(
        self, query: str, context: str, k: int = 5, score_threshold: float = None
    ) -> List[Tuple[Document, float]]:
        similar_documents = []

        stores_to_search_in = {}
        stores_to_search_in["base"] = self._embeddings_stores["base"]

        if context is not None and context != "":
            stores_to_search_in[context] = self._embeddings_stores[context]

        for context, store in stores_to_search_in.items():
            for embedding_key in store.get_keys():
                partial_results = (
                    self._similarity_search_on_single_document_with_scores(
                        query, embedding_key, context, k, score_threshold
                    )
                )
                similar_documents.extend(partial_results)

        similar_documents.sort(key=lambda x: x[1], reverse=False)

        similar_documents = similar_documents[:k]

        return similar_documents

    def _similarity_search_on_single_document_with_scores(
        self,
        query: str,
        document_key: str,
        context: str,
        k: int = 5,
        score_threshold: float = None,
    ) -> List[Tuple[Document, float]]:
        store = self._embeddings_stores.get(context, None)
        if store is None:
            return []

        embedding = store.get_embedding(document_key)

        if embedding is None:
            return []

        similar_documents = embedding.retriever.similarity_search_with_score(
            query=query, k=k, score_threshold=score_threshold
        )
        return similar_documents

    def _similarity_search_on_single_document(
        self,
        query: str,
        document_key: str,
        context: str,
        k: int = 5,
        score_threshold: float = None,
    ) -> List[Document]:
        documents_with_scores = self._similarity_search_on_single_document_with_scores(
            query, document_key, context, k, score_threshold
        )
        documents = [doc for doc, _ in documents_with_scores]
        return documents

    def _similarity_search(
        self, query: str, context: str, k: int = 5, score_threshold: float = None
    ) -> List[Document]:
        documents_with_scores = self._similarity_search_with_scores(
            query, context, k, score_threshold
        )
        documents = [doc for doc, _ in documents_with_scores]
        return documents
