# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import FastAPI
from unittest.mock import patch, MagicMock


@patch("app.DisclaimerAndGuidelinesService", new_callable=MagicMock)
@patch("frontmatter.load", return_value=MagicMock())
@patch("tiktoken.get_encoding", return_value=MagicMock())
@patch("os.listdir", return_value=["prompt1.md", "prompt2.md"])
@patch("os.path.exists", return_value=True)
def test_create_server_returns_fastapi(
    mock_exists, mock_listdir, mock_get_encoding, mock_frontmatter, mock_disclaimer
):
    with patch("config_service.ConfigService") as MockConfig:
        mock_config = MockConfig.return_value
        # Patch methods/attributes used in app creation
        mock_embedding_model = MagicMock()
        mock_embedding_model.provider = "openai"
        # Patch .config to be a dict with real string values
        mock_embedding_model.config = {
            "model": "text-embedding-ada-002",
            "api_key": "sk-test",
        }
        mock_config.load_embedding_model.return_value = mock_embedding_model
        mock_config.load_knowledge_pack_path.return_value = "./"
        mock_config.get_image_model.return_value = MagicMock()
        mock_config.get_chat_model.return_value = MagicMock()
        mock_config.load_api_key_repository_type.return_value = "file"
        mock_config.load_api_key_pseudonymization_salt.return_value = "dummy"
        mock_config.is_api_key_auth_enabled.return_value = False
        from main import create_server

        app = create_server()
        assert isinstance(app, FastAPI)


@patch("uvicorn.run")
def test_main_calls_uvicorn_run(mock_run):
    import main

    with patch("main.create_server") as mock_create_server:
        mock_app = MagicMock(spec=FastAPI)
        mock_create_server.return_value = mock_app
        main.main()
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] is mock_app
        assert kwargs["host"] == "0.0.0.0"
        assert kwargs["port"] == 8080
        assert kwargs["forwarded_allow_ips"] == "*"
