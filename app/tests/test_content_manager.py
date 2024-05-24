# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import patch

from shared.content_manager import ContentManager
from shared.models.embedding_model import EmbeddingModel
from shared.services.embeddings_service import EmbeddingsService


class TestContentManager:
    @patch("shared.content_manager.Embeddings")
    @patch("shared.content_manager.EmbeddingsService")
    @patch("shared.content_manager.ConfigService")
    @patch("shared.content_manager.KnowledgeBaseMarkdown")
    def test_init(
        self,
        mock_knowledge_base_markdown,
        mock_config_service,
        mock_embeddings_service,
        mock_embeddings,
    ):
        knowledge_pack_path = "/path/to/root"

        mock_config_service.load_embedding_model.return_value = {}

        content_manager = ContentManager(knowledge_pack_path=knowledge_pack_path)

        mock_config_service.load_embedding_model.assert_called_once_with("config.yaml")
        mock_embeddings_service.initialize.assert_called_once()
        mock_embeddings_service.load_knowledge_base.assert_called_once_with(
            knowledge_pack_path + "/embeddings"
        )

        mock_knowledge_base_markdown.assert_called_once()
        content_manager.knowledge_base_markdown.load_base_knowledge.assert_called_once_with(
            knowledge_pack_path
        )

    @patch("shared.content_manager.ConfigService")
    @patch("shared.content_manager.KnowledgeBaseMarkdown")
    def test_load_context_knowledge_with_empty_embeddings_should_not_fail(
        self,
        mock_knowledge_base,
        mock_config_service,
    ):
        EmbeddingsService.reset_instance()

        embedding_model = EmbeddingModel(
            id="ollama-embeddings",
            name="Ollama Embeddings",
            provider="ollama",
            config={"model": "ollama-embeddings", "api_key": "api_key"},
        )

        knowledge_pack_path = "tests/test_data/test_knowledge_pack"

        mock_config_service.load_embedding_model.return_value = embedding_model

        exception_raised = False
        try:
            _ = ContentManager(knowledge_pack_path=knowledge_pack_path)
        except FileNotFoundError:
            exception_raised = True

        assert not exception_raised
