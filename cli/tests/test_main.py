# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import patch, MagicMock, PropertyMock
from haiven_cli.main import (
    index_file,
    index_all_files,
    init,
    set_config_path,
    set_env_path,
)


class TestMain:
    @patch("haiven_cli.main.MetadataService")
    @patch("haiven_cli.main.EmbeddingService")
    @patch("haiven_cli.main.CliConfigService")
    @patch("haiven_cli.main.TokenService")
    @patch("haiven_cli.main.KnowledgeService")
    @patch("haiven_cli.main.ConfigService")
    @patch("haiven_cli.main.FileService")
    @patch("haiven_cli.main.App")
    def test_index_file(
        self,
        mock_app,
        mock_file_service,
        mock_config_service,
        mock_knowledge_service,
        mock_token_service,
        mock_cli_config_service,
        mock_embedding_service,
        mock_metadata_service,
    ):
        source_path = "source_path.pdf"
        embedding_model = "embedding_model"
        config_path = "config_path"
        description = "description"
        output_dir = "output_dir"
        provider = "provider"

        token_service = MagicMock()
        mock_token_service.return_value = token_service

        knowledge_service = MagicMock()
        mock_knowledge_service.return_value = knowledge_service

        env_file_path = ".test_env"
        cli_config_service = MagicMock()
        cli_config_service.get_env_path.return_value = env_file_path
        mock_cli_config_service.return_value = cli_config_service

        config_service = MagicMock()
        model = MagicMock()
        type(model).id = PropertyMock(return_value=embedding_model)
        type(model).provider = PropertyMock(return_value=provider)
        config_service.load_embeddings.return_value = [model]
        mock_config_service.return_value = config_service

        file_service = MagicMock()
        mock_file_service.return_value = file_service

        app = MagicMock()
        mock_app.return_value = app

        index_file(source_path, embedding_model, config_path, description, output_dir)

        mock_token_service.assert_called_once_with("cl100k_base")
        mock_knowledge_service.assert_called_once_with(
            token_service, mock_embedding_service
        )
        mock_config_service.assert_called_once_with(env_file_path=env_file_path)
        mock_app.assert_called_once_with(
            config_service,
            file_service,
            knowledge_service,
            mock_metadata_service,
        )
        app.index_individual_file.assert_called_once_with(
            source_path, embedding_model, config_path, output_dir, description, None
        )

    @patch("haiven_cli.main.MetadataService")
    @patch("haiven_cli.main.EmbeddingService")
    @patch("haiven_cli.main.CliConfigService")
    @patch("haiven_cli.main.TokenService")
    @patch("haiven_cli.main.KnowledgeService")
    @patch("haiven_cli.main.ConfigService")
    @patch("haiven_cli.main.FileService")
    @patch("haiven_cli.main.App")
    def test_index_all_files(
        self,
        mock_app,
        mock_file_service,
        mock_config_service,
        mock_knowledge_service,
        mock_token_service,
        mock_cli_config_service,
        mock_embedding_service,
        mock_metadata_service,
    ):
        source_dir = "source_dir"
        output_dir = "destination_dir"
        embedding_model = "embedding_model"
        description = "description"
        config_path = "config_path"

        token_service = MagicMock()
        mock_token_service.return_value = token_service

        knowledge_service = MagicMock()
        mock_knowledge_service.return_value = knowledge_service

        env_file_path = ".test_env"
        cli_config_service = MagicMock()
        cli_config_service.get_env_path.return_value = env_file_path
        mock_cli_config_service.return_value = cli_config_service

        config_service = MagicMock()
        mock_config_service.return_value = config_service

        file_service = MagicMock()
        mock_file_service.return_value = file_service

        app = MagicMock()
        mock_app.return_value = app

        index_all_files(
            source_dir, output_dir, embedding_model, description, config_path
        )

        mock_token_service.assert_called_once_with("cl100k_base")
        mock_knowledge_service.assert_called_once_with(
            token_service, mock_embedding_service
        )
        mock_config_service.assert_called_once_with(env_file_path=env_file_path)
        mock_app.assert_called_once_with(
            config_service,
            file_service,
            knowledge_service,
            mock_metadata_service,
        )
        app.index_all_files.assert_called_once_with(
            source_dir, embedding_model, config_path, output_dir, description
        )

    @patch("haiven_cli.main.CliConfigService")
    def test_init(self, mock_cli_config_service):
        cli_config_service = MagicMock()
        mock_cli_config_service.return_value = cli_config_service
        config_path = "config_path"
        env_path = "env_path"

        init(config_path, env_path)

        cli_config_service.initialize_config.assert_called_once_with(
            config_path=config_path, env_path=env_path
        )

    @patch("haiven_cli.main.CliConfigService")
    def test_set_config_path(self, mock_cli_config_service):
        cli_config_service = MagicMock()
        mock_cli_config_service.return_value = cli_config_service
        config_path = "config_path"

        set_config_path(config_path)

        cli_config_service.set_config_path.assert_called_once_with(config_path)

    @patch("haiven_cli.main.CliConfigService")
    def test_set_env_path(self, mock_cli_config_service):
        cli_config_service = MagicMock()
        mock_cli_config_service.return_value = cli_config_service
        env_path = ".env_path"

        set_env_path(env_path)

        cli_config_service.set_env_path.assert_called_once_with(env_path)
