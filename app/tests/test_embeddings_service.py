# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
import pytest
from shared.models.embedding_model import EmbeddingModel
from shared.embeddings import Embeddings
from shared.services.embeddings_service import EmbeddingsService


class TestsEmbeddingsService:
    @pytest.fixture(autouse=True)
    def setup(self):
        EmbeddingsService.reset_instance()

        api_key = os.environ.get("OPENAI_API_KEY")
        embedding_config = EmbeddingModel(
            id="open-ai-text-embedding-ada-002",
            name="Text Embedding Ada v2 on OpenAI",
            provider="openai",
            config={"model": "text-embedding-ada-002", "api_key": api_key},
        )

        embeddings_provider = Embeddings(embedding_config)
        EmbeddingsService.initialize(embeddings_provider)

        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        EmbeddingsService.load_knowledge_pack(
            os.path.join(root_dir, "tests/test_data/test_knowledge_pack")
        )

        self.service = EmbeddingsService.get_instance()

    @pytest.mark.integration
    def test_generate_load_knowledge_pack_should_load_two_embedding(self):
        assert len(self.service._embeddings_store._embeddings) == 2
        assert len(self.service._embeddings_store.get_keys()) == 2

        assert "ingenuity-wikipedia" in self.service._embeddings_store.get_keys()
        assert "automotive-spice" in self.service._embeddings_store.get_keys()

    @pytest.mark.integration
    def test_similarity_search_on_single_document_with_scores_return_documents_and_scores(
        self,
    ):
        score_threshold = 0.3
        similarity_results = (
            self.service.similarity_search_on_single_document_with_scores(
                query="When Ingenuity was launched?",
                document_key="ingenuity-wikipedia",
                k=3,
                score_threshold=score_threshold,
            )
        )

        assert len(similarity_results) > 0
        assert len(similarity_results) <= 3
        assert len(similarity_results[0][0].page_content) > 1
        assert similarity_results[0][1] < score_threshold

    @pytest.mark.integration
    def test_similarity_search_on_single_document_with_scores_without_score_threshold_return_documents_and_scores(
        self,
    ):
        similarity_results = (
            self.service.similarity_search_on_single_document_with_scores(
                query="When Team AIDE was released?",
                document_key="ingenuity-wikipedia",
                k=3,
            )
        )

        assert len(similarity_results) > 0
        assert len(similarity_results) <= 3
        assert len(similarity_results[0][0].page_content) > 1

    @pytest.mark.integration
    def test_similarity_search_on_single_document_with_scores_default_score_threshold(
        self,
    ):
        similarity_results = (
            self.service.similarity_search_on_single_document_with_scores(
                query="what is Ingenuity?", document_key="ingenuity-wikipedia", k=5
            )
        )

        assert len(similarity_results) <= 5
        assert len(similarity_results[0][0].page_content) > 1
        for _, score in similarity_results:
            assert score <= 0.4

    @pytest.mark.integration
    def test_similarity_search_with_scores_return_results_from_different_documents(
        self,
    ):
        similarity_results = self.service.similarity_search_with_scores(
            query="what does Ingenuity and Automotive Spice have in common?", k=5
        )

        extracted_files = [result[0].metadata["file"] for result in similarity_results]

        assert len(similarity_results) <= 5
        assert len(set(extracted_files)) == 2
