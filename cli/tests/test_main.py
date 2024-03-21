# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest.mock import patch, MagicMock
from main import index_file, index_all_files


class TestMain:
    @patch("main.TokenService")
    @patch("main.KnowledgeService")
    @patch("main.ConfigService")
    @patch("main.FileService")
    @patch("main.App")
    def test_index_file(
        self,
        mock_app,
        mock_file_service,
        mock_config_service,
        mock_knowledge_service,
        mock_token_service,
    ):
        source_path = "source_path"
        destination_dir = "destination_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"

        token_service = MagicMock()
        mock_token_service.return_value = token_service

        knowledge_service = MagicMock()
        mock_knowledge_service.return_value = knowledge_service

        config_service = MagicMock()
        mock_config_service.return_value = config_service

        file_service = MagicMock()
        mock_file_service.return_value = file_service

        app = MagicMock()
        mock_app.return_value = app

        index_file(source_path, destination_dir, embedding_model, config_path)

        mock_token_service.assert_called_once_with("cl100k_base")
        mock_knowledge_service.assert_called_once_with(destination_dir, token_service)
        mock_app.assert_called_once_with(
            config_service, file_service, knowledge_service
        )
        app.index_individual_file.assert_called_once_with(
            source_path, embedding_model, config_path
        )

    @patch("main.TokenService")
    @patch("main.KnowledgeService")
    @patch("main.ConfigService")
    @patch("main.FileService")
    @patch("main.App")
    def test_index_all_files(
        self,
        mock_app,
        mock_file_service,
        mock_config_service,
        mock_knowledge_service,
        mock_token_service,
    ):
        source_dir = "source_dir"
        destination_dir = "destination_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"

        token_service = MagicMock()
        mock_token_service.return_value = token_service

        knowledge_service = MagicMock()
        mock_knowledge_service.return_value = knowledge_service

        config_service = MagicMock()
        mock_config_service.return_value = config_service

        file_service = MagicMock()
        mock_file_service.return_value = file_service

        app = MagicMock()
        mock_app.return_value = app

        index_all_files(source_dir, destination_dir, embedding_model, config_path)

        mock_token_service.assert_called_once_with("cl100k_base")
        mock_knowledge_service.assert_called_once_with(destination_dir, token_service)
        mock_app.assert_called_once_with(
            config_service, file_service, knowledge_service
        )
        app.index_all_files.assert_called_once_with(
            source_dir, embedding_model, config_path
        )
