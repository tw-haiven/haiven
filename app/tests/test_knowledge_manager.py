# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import patch

from knowledge.documents import KnowledgeBaseDocuments
from tests.utils import get_test_data_path
from knowledge_manager import KnowledgeManager
from embeddings.model import EmbeddingModel


class TestKnowledgeManager:
    knowledge_pack_path = get_test_data_path() + "/test_knowledge_pack"
    config_file_path = get_test_data_path() + "/test_config.yaml"

    @patch("knowledge_manager.EmbeddingsClient")
    @patch("knowledge_manager.KnowledgeBaseDocuments")
    @patch("knowledge_manager.ConfigService")
    @patch("knowledge_manager.KnowledgeBaseMarkdown")
    def test_init(
        self,
        mock_knowledge_base_markdown,
        mock_config_service,
        mock_knowledge_base_documents,
        mock_embeddings,
    ):
        mock_config_service.load_embedding_model.return_value = {}
        mock_config_service.load_knowledge_pack_path.return_value = (
            self.knowledge_pack_path
        )

        knowledge_manager = KnowledgeManager(
            config_service=mock_config_service,
        )

        mock_config_service.load_embedding_model.assert_called_once()

        assert knowledge_manager.knowledge_base_documents is not None
        mock_knowledge_base_documents_instance: KnowledgeBaseDocuments = (
            mock_knowledge_base_documents.return_value
        )
        mock_knowledge_base_documents_instance.load_documents_for_base.assert_called_once_with(
            self.knowledge_pack_path + "/embeddings"
        )

        mock_knowledge_base_markdown.assert_called_once()
        knowledge_manager.knowledge_base_markdown.load_for_base.assert_called_once_with(
            self.knowledge_pack_path
        )

    @patch("knowledge_manager.ConfigService")
    @patch("knowledge_manager.KnowledgeBaseMarkdown")
    def test_load_context_knowledge_with_empty_embeddings_should_not_fail(
        self,
        mock_knowledge_base,
        mock_config_service,
    ):
        embedding_model = EmbeddingModel(
            id="ollama-embeddings",
            name="Ollama Embeddings",
            provider="ollama",
            config={"model": "ollama-embeddings", "api_key": "api_key"},
        )

        mock_config_service.load_embedding_model.return_value = embedding_model
        mock_config_service.load_knowledge_pack_path.return_value = (
            self.knowledge_pack_path
        )

        exception_raised = False
        try:
            _ = KnowledgeManager(
                config_service=mock_config_service,
            )
        except FileNotFoundError:
            exception_raised = True

        assert not exception_raised
