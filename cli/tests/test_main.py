# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest.mock import patch, MagicMock
from teamai_cli.main import index_file, index_all_files, pickle_web_page, init


class TestMain:
    @patch("teamai_cli.main.WebPageService")
    @patch("teamai_cli.main.TokenService")
    @patch("teamai_cli.main.KnowledgeService")
    @patch("teamai_cli.main.ConfigService")
    @patch("teamai_cli.main.FileService")
    @patch("teamai_cli.main.App")
    def test_index_file(
        self,
        mock_app,
        mock_file_service,
        mock_config_service,
        mock_knowledge_service,
        mock_token_service,
        mock_web_page_service,
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

        web_page_service = MagicMock()
        mock_web_page_service.return_value = web_page_service

        app = MagicMock()
        mock_app.return_value = app

        index_file(source_path, destination_dir, embedding_model, config_path)

        mock_token_service.assert_called_once_with("cl100k_base")
        mock_knowledge_service.assert_called_once_with(destination_dir, token_service)
        mock_app.assert_called_once_with(
            config_service, file_service, knowledge_service, web_page_service
        )
        app.index_individual_file.assert_called_once_with(
            source_path, embedding_model, config_path
        )

    @patch("teamai_cli.main.WebPageService")
    @patch("teamai_cli.main.TokenService")
    @patch("teamai_cli.main.KnowledgeService")
    @patch("teamai_cli.main.ConfigService")
    @patch("teamai_cli.main.FileService")
    @patch("teamai_cli.main.App")
    def test_index_all_files(
        self,
        mock_app,
        mock_file_service,
        mock_config_service,
        mock_knowledge_service,
        mock_token_service,
        mock_web_page_service,
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

        web_page_service = MagicMock()
        mock_web_page_service.return_value = web_page_service

        app = MagicMock()
        mock_app.return_value = app

        index_all_files(source_dir, destination_dir, embedding_model, config_path)

        mock_token_service.assert_called_once_with("cl100k_base")
        mock_knowledge_service.assert_called_once_with(destination_dir, token_service)
        mock_app.assert_called_once_with(
            config_service, file_service, knowledge_service, web_page_service
        )
        app.index_all_files.assert_called_once_with(
            source_dir, embedding_model, config_path
        )

    @patch("teamai_cli.main.Client")
    @patch("teamai_cli.main.PageHelper")
    @patch("teamai_cli.main.WebPageService")
    @patch("teamai_cli.main.TokenService")
    @patch("teamai_cli.main.KnowledgeService")
    @patch("teamai_cli.main.ConfigService")
    @patch("teamai_cli.main.FileService")
    @patch("teamai_cli.main.App")
    def test_index_web_page(
        self,
        mock_app,
        mock_file_service,
        mock_config_service,
        mock_knowledge_service,
        mock_token_service,
        mock_web_page_service,
        mock_page_helper,
        mock_client,
    ):
        source_url = "source_url"
        destination_path = "destination_path"
        html_filter = "p"

        token_service = MagicMock()
        mock_token_service.return_value = token_service

        knowledge_service = MagicMock()
        mock_knowledge_service.return_value = knowledge_service

        config_service = MagicMock()
        mock_config_service.return_value = config_service

        file_service = MagicMock()
        mock_file_service.return_value = file_service

        client = MagicMock()
        mock_client.return_value = client

        page_helper = MagicMock()
        mock_page_helper.return_value = page_helper

        web_page_service = MagicMock()
        mock_web_page_service.return_value = web_page_service

        app = MagicMock()
        mock_app.return_value = app

        pickle_web_page(source_url, destination_path, html_filter)

        mock_knowledge_service.assert_called_once_with(destination_path, token_service)
        mock_web_page_service.assert_called_once_with(client, page_helper)
        app.index_web_page.assert_called_once_with(
            url=source_url, html_filter=html_filter, destination_path=destination_path
        )

    @patch("teamai_cli.main.CliConfigService")
    def test_init(self, mock_cli_config_service):
        cli_config_service = MagicMock()
        mock_cli_config_service.return_value = cli_config_service

        config_path = "config_path"
        env_path = "env_path"

        init(config_path, env_path)

        cli_config_service.initialize_config.assert_called_once_with(
            config_path=config_path, env_path=env_path
        )
