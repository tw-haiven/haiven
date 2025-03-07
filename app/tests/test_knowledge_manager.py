# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import patch

from knowledge.documents import KnowledgeBaseDocuments
from tests.utils import get_test_data_path
from knowledge_manager import KnowledgeManager
from embeddings.model import EmbeddingModel
from config.constants import SYSTEM_MESSAGE


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

        # Verify that the system message was loaded
        # Expected custom system message from the real file
        expected_system_message = "You are an AI assistant and this is your system message loaded in the test knowledge pack."
        assert knowledge_manager.system_message == expected_system_message
        assert knowledge_manager.get_system_message() == expected_system_message

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

    @patch("knowledge_manager.EmbeddingsClient")
    @patch("knowledge_manager.KnowledgeBaseDocuments")
    @patch("knowledge_manager.KnowledgeBaseMarkdown")
    @patch("knowledge_manager.ConfigService")
    @patch("knowledge_manager.os.path.exists")
    def test_load_system_message_error_handling(
        self,
        mock_exists,
        mock_config_service,
        mock_knowledge_base_markdown,
        mock_knowledge_base_documents,
        mock_embeddings_client,
    ):
        # Setup mocks
        mock_config_service.load_knowledge_pack_path.return_value = (
            self.knowledge_pack_path
        )
        mock_config_service.load_embedding_model.return_value = {}
        mock_exists.return_value = True

        # Create a mock KnowledgePack with no contexts to avoid loading context files
        with patch("knowledge_manager.KnowledgePack") as mock_knowledge_pack:
            mock_knowledge_pack_instance = mock_knowledge_pack.return_value
            mock_knowledge_pack_instance.path = self.knowledge_pack_path
            mock_knowledge_pack_instance.contexts = []

            # Mock open to raise an exception
            with patch("builtins.open", side_effect=Exception("Error reading file")):
                knowledge_manager = KnowledgeManager(config_service=mock_config_service)

                # Verify the default system message is used when there's an error
                assert knowledge_manager.system_message == SYSTEM_MESSAGE
                assert knowledge_manager.get_system_message() == SYSTEM_MESSAGE
