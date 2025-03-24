# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from unittest.mock import MagicMock

import pytest
from langchain.docstore.document import Document
from embeddings.model import EmbeddingModel
from knowledge.documents import KnowledgeBaseDocuments


class TestsKnowledgeBaseDocuments:
    @pytest.fixture(autouse=True)
    def setup(self):
        embedding_model = EmbeddingModel(
            id="ollama-embeddings",
            name="Ollama Embeddings",
            provider="ollama",
            config={"model": "ollama-embeddings", "api_key": "api_key"},
        )

        fake_similarity_results = [
            (Document(page_content="document content A"), 0.2),
            (Document(page_content="document content B"), 0.23),
            (Document(page_content="document content C"), 0.27),
            (Document(page_content="document content D"), 0.31),
            (Document(page_content="document content E"), 0.35),
        ]

        retriever_mock = MagicMock()
        retriever_mock.similarity_search_with_score.return_value = (
            fake_similarity_results
        )
        embeddings_provider_mock = MagicMock()
        embeddings_provider_mock.generate_from_filesystem.return_value = retriever_mock
        embeddings_provider_mock.generate_from_documents.return_value = retriever_mock
        embeddings_provider_mock.embedding_model = embedding_model
        config_service_mock = MagicMock()
        config_service_mock.load_embedding_model.return_value = embedding_model

        self.service = KnowledgeBaseDocuments(
            config_service_mock, embeddings_provider_mock
        )
        self.service._embeddings_provider.embedding_model = embedding_model
        self.knowledge_pack_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tests/test_data/test_knowledge_pack",
        )

    def test_load_base_knowledge_creates_entry_in_stores(
        self,
    ):
        # assert len(self.service._document_stores.get_keys()) == 2

        self.service.load_documents_for_base(self.knowledge_pack_path + "/embeddings")

        assert len(self.service._document_stores.get_keys()) == 2
        assert len(self.service._document_stores.get_documents()) == 2
        assert (
            self.service._document_stores.get_document("ingenuity-wikipedia").title
            == "Wikipedia entry about Ingenuity"
        )
        assert (
            self.service._document_stores.get_document("tw-guide-agile-sd").title
            == "The Thoughtworks guide to agile software delivery"
        )

    def test_re_load_base_knowledge_should_not_create_extra_entries(
        self,
    ):
        self.service.load_documents_for_base(self.knowledge_pack_path + "/embeddings")

        assert len(self.service._document_stores.get_keys()) == 2

        self.service.load_documents_for_base(self.knowledge_pack_path + "/embeddings")

        assert len(self.service._document_stores.get_keys()) == 2

    def test_similarity_search_on_single_document_with_scores_for_base_return_documents_and_scores(
        self,
    ):
        self.service.load_documents_for_base(self.knowledge_pack_path + "/embeddings")

        similarity_results = (
            self.service._similarity_search_on_single_document_with_scores(
                query="When Ingenuity was launched?",
                document_key="ingenuity-wikipedia",
            )
        )

        assert len(similarity_results) == 5
        assert len(similarity_results[0][0].page_content) > 1
        assert similarity_results[0][1] < 1

    def test_similarity_search_with_scores_should_return_documents_from_base_stores_sorted_by_scores(
        self,
    ):
        self.service.load_documents_for_base(self.knowledge_pack_path + "/embeddings")

        similarity_results = self.service.similarity_search_with_scores(
            query="When Ingenuity was launched?"
        )

        assert len(similarity_results) == 5

        # Since both stores retrievers will return the same results, results will be duplicated as there are 2 documents in total
        assert similarity_results[0][0].page_content == "document content A"
        assert similarity_results[1][0].page_content == "document content A"
        assert similarity_results[2][0].page_content == "document content B"
        assert similarity_results[3][0].page_content == "document content B"
        assert similarity_results[4][0].page_content == "document content C"

        assert similarity_results[0][1] == 0.2
        assert similarity_results[1][1] == 0.2
        assert similarity_results[2][1] == 0.23
        assert similarity_results[3][1] == 0.23
        assert similarity_results[4][1] == 0.27
