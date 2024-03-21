# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from pathlib import Path
from typing import Dict, List, Tuple

from langchain.docstore.document import Document

from shared.services.config_service import ConfigService
from shared.embeddings import Embeddings


class DocumentRetrieval:
    @staticmethod
    def get_vector_store(path=".", config_file_path="config.yaml"):
        embeddings_provider = Embeddings(
            ConfigService.load_embedding_model(config_file_path)
        )
        return embeddings_provider.generate_from_filesystem(path)

    @staticmethod
    def get_document_retriever(path, config_file_path):
        TOP_K_EMBEDDINGS = 5
        EMBEDDING_SCORE_CUTOFF = 0.3

        path = Path(path)
        search_kwargs = {
            "k": TOP_K_EMBEDDINGS,
            "score_threshold": EMBEDDING_SCORE_CUTOFF,
        }
        faiss = DocumentRetrieval.get_vector_store(path, config_file_path)

        return faiss.as_retriever(
            search_type="similarity_score_threshold", search_kwargs=search_kwargs
        )

    @staticmethod
    def get_docs_and_sources_from_document_store(
        document_retriever, query, chat_history: List[Dict[str, str]] = None
    ):
        docs = document_retriever.get_relevant_documents(query)
        print(
            f"Found {len(docs)} relevant documents for query with "
            f"the following doc lengths: {[len(doc.page_content) for doc in docs]}"
        )
        return docs

    @staticmethod
    def get_unique_sources(
        documents: List[Document],
    ) -> Tuple[List[str], List[dict[str, str]]]:
        unique_sources = []
        metadata = []
        for doc in documents:
            source = doc.metadata["source"]
            if source not in unique_sources:
                unique_sources.append(source)
                metadata.append(
                    {
                        "source": source,
                        "title": doc.metadata["title"],
                    }
                )

        return metadata
