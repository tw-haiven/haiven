# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest.mock import MagicMock, patch
from shared.content_manager import ContentManager


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
        mock_knowledge_pack = MagicMock()
        mock_knowledge_pack.path = knowledge_pack_path

        _ = ContentManager(knowledge_pack=mock_knowledge_pack)

        mock_config_service.load_embedding_model.assert_called_once_with("config.yaml")
        mock_embeddings_service.initialize.assert_called_once()
        mock_embeddings_service.load_knowledge_base.assert_called_once_with(
            knowledge_pack_path + "/embeddings"
        )

        mock_knowledge_base_markdown.assert_called_with(path=knowledge_pack_path)
