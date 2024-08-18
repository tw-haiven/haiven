# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from unittest.mock import MagicMock

import pytest
from langchain.docstore.document import Document
from embeddings.model import EmbeddingModel
from embeddings.service import EmbeddingsService


class TestsEmbeddingsService:
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

        self.service = EmbeddingsService(config_service_mock, embeddings_provider_mock)
        self.service._embeddings_provider.embedding_model = embedding_model
        self.knowledge_pack_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tests/test_data/test_knowledge_pack",
        )

    def test_load_base_knowledge_pack_creates_one_entry_in_stores(
        self,
    ):
        assert len(self.service._embeddings_stores) == 1
        assert self.service._embeddings_stores["base"]._embeddings == {}

        self.service.load_knowledge_base(self.knowledge_pack_path + "/embeddings")

        assert len(self.service._embeddings_stores) == 1
        assert (
            "ingenuity-wikipedia"
            in self.service._embeddings_stores["base"]._embeddings.keys()
        )

    def test_load_context_knowledge_with_empty_embeddings_raise_error(
        self,
    ):
        try:
            self.service.load_knowledge_context(
                context_name="Context B",
                context_path=self.knowledge_pack_path
                + "/contexts/context_b/embeddings",
            )
            exception_raised = False
        except FileNotFoundError:
            exception_raised = True

        assert exception_raised
        assert len(self.service._embeddings_stores) == 1  # only base embeddings
        assert "base" in self.service._embeddings_stores.keys()
        assert "Context B" not in self.service._embeddings_stores.keys()

    def test_load_base_and_context_knowledge_creates_two_entry_in_stores(
        self,
    ):
        assert len(self.service._embeddings_stores) == 1

        self.service.load_knowledge_base(self.knowledge_pack_path + "/embeddings")

        assert len(self.service._embeddings_stores) == 1
        assert "base" in self.service._embeddings_stores.keys()

        self.service.load_knowledge_context(
            context_name="Context A",
            context_path=self.knowledge_pack_path + "/contexts/context_a/embeddings",
        )

        assert len(self.service._embeddings_stores) == 2
        assert "base" in self.service._embeddings_stores.keys()
        assert "Context A" in self.service._embeddings_stores.keys()

    def test_re_load_base_or_context_knowledge_should_not_create_extra_entries(
        self,
    ):
        assert len(self.service._embeddings_stores) == 1

        self.service.load_knowledge_base(self.knowledge_pack_path + "/embeddings")

        assert len(self.service._embeddings_stores) == 1
        assert "base" in self.service._embeddings_stores.keys()

        self.service.load_knowledge_base(self.knowledge_pack_path + "/embeddings")

        assert len(self.service._embeddings_stores) == 1
        assert "base" in self.service._embeddings_stores.keys()

        self.service.load_knowledge_context(
            context_name="Context A",
            context_path=self.knowledge_pack_path + "/contexts/context_a/embeddings",
        )

        assert len(self.service._embeddings_stores) == 2
        assert "base" in self.service._embeddings_stores.keys()
        assert "Context A" in self.service._embeddings_stores.keys()

        self.service.load_knowledge_context(
            context_name="Context A",
            context_path=self.knowledge_pack_path + "/contexts/context_a/embeddings",
        )

        assert len(self.service._embeddings_stores) == 2
        assert "base" in self.service._embeddings_stores.keys()
        assert "Context A" in self.service._embeddings_stores.keys()

    def test_generate_load_knowledge_base_should_load_two_embedding(self):
        self.service.load_knowledge_base(self.knowledge_pack_path + "/embeddings")

        assert len(self.service._embeddings_stores) == 1
        assert len(self.service._embeddings_stores.keys()) == 1
        assert "base" in self.service._embeddings_stores.keys()

        assert (
            "ingenuity-wikipedia" in self.service._embeddings_stores["base"].get_keys()
        )
        assert "tw-guide-agile-sd" in self.service._embeddings_stores["base"].get_keys()

    def test_similarity_search_on_single_document_with_scores_for_base_return_documents_and_scores(
        self,
    ):
        self.service.load_knowledge_base(self.knowledge_pack_path + "/embeddings")

        similarity_results = (
            self.service._similarity_search_on_single_document_with_scores(
                query="When Ingenuity was launched?",
                document_key="ingenuity-wikipedia",
                context="base",
            )
        )

        assert len(similarity_results) == 5
        assert len(similarity_results[0][0].page_content) > 1
        assert similarity_results[0][1] < 1

    def test_similarity_search_on_single_document_with_scores_for_context_does_not_return_documents_and_scores_if_context_is_not_loaded(
        self,
    ):
        self.service.load_knowledge_base(self.knowledge_pack_path + "/embeddings")

        similarity_results = (
            self.service._similarity_search_on_single_document_with_scores(
                query="When Ingenuity was launched?",
                document_key="ingenuity-wikipedia",
                context="Context A",
            )
        )

        assert len(similarity_results) == 0

    def test_similarity_search_for_context_should_return_documents_from_base_and_context_stores_sorted_by_scores(
        self,
    ):
        assert len(self.service._embeddings_stores) == 1

        self.service.load_knowledge_base(self.knowledge_pack_path + "/embeddings")

        self.service.load_knowledge_context(
            context_name="Context A",
            context_path=self.knowledge_pack_path + "/contexts/context_a/embeddings",
        )

        similarity_results = self.service.similarity_search_with_scores(
            query="When Ingenuity was launched?", context="Context A"
        )

        assert len(similarity_results) == 5
        # Since both stores retrievers will return the same results, the first 4 results will be the same as there are 4 documents in total
        assert (
            similarity_results[0][0].page_content
            == similarity_results[1][0].page_content
        )
        assert (
            similarity_results[0][0].page_content
            == similarity_results[2][0].page_content
        )
        assert (
            similarity_results[0][0].page_content
            == similarity_results[3][0].page_content
        )

        assert similarity_results[0][1] == 0.2
        assert similarity_results[1][1] == 0.2
        assert similarity_results[2][1] == 0.2
        assert similarity_results[3][1] == 0.2
