# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import call, patch, MagicMock
from app import App


class TestApp:
    @patch("app.Server")
    def test_init(self, mock_server):
        # Mock the dependencies
        server = MagicMock()
        mock_server().create.return_value = server
        content_manager = MagicMock()
        ui_factory = MagicMock()

        # Initialize App
        app = App(
            content_manager=content_manager,
            prompts_factory=MagicMock(),
            chat_session_memory=MagicMock(),
            ui_factory=ui_factory,
        )

        # Assertions to ensure everything was called as expected
        mock_server().create.assert_called_once_with()

        assert app.server == server
        assert app.content_manager == content_manager

    @patch("app.gr.mount_gradio_app")
    @patch("app.Server")
    def test_launch_via_fastapi_wrapper(self, mock_server, mock_mount_gradio_app):
        # Mock the dependencies
        server = MagicMock()
        mock_server().create.return_value = server
        content_manager = MagicMock()
        ui_factory = MagicMock()

        navigation_manager = MagicMock()
        analysis_path = MagicMock()
        testing_path = MagicMock()
        coding_path = MagicMock()
        knowledge_path = MagicMock()
        about_path = MagicMock()
        chat_path = MagicMock()
        navigation_manager.get_analysis_path.return_value = analysis_path
        navigation_manager.get_testing_path.return_value = testing_path
        navigation_manager.get_coding_path.return_value = coding_path
        navigation_manager.get_knowledge_path.return_value = knowledge_path
        navigation_manager.get_about_path.return_value = about_path
        navigation_manager.get_chat_path.return_value = chat_path

        ui_factory = MagicMock()
        ui_analysts = MagicMock()
        ui_testing = MagicMock()
        ui_coding = MagicMock()
        ui_knowledge = MagicMock()
        ui_about = MagicMock()
        plain_chat = MagicMock()
        ui_factory.navigation_manager = navigation_manager
        ui_factory.create_ui_analysts.return_value = ui_analysts
        ui_factory.create_ui_testing.return_value = ui_testing
        ui_factory.create_ui_coding.return_value = ui_coding
        ui_factory.create_ui_knowledge.return_value = ui_knowledge
        ui_factory.create_ui_about.return_value = ui_about
        ui_factory.create_plain_chat.return_value = plain_chat

        app = App(
            content_manager=content_manager,
            prompts_factory=MagicMock(),
            chat_session_memory=MagicMock(),
            ui_factory=ui_factory,
        )

        # Action
        returned_server = app.launch_via_fastapi_wrapper()

        # Assert
        expected_calls = [
            call(server, ui_analysts, path=analysis_path, root_path=analysis_path),
            call(server, ui_testing, path=testing_path, root_path=testing_path),
            call(server, ui_coding, path=coding_path, root_path=coding_path),
            call(server, ui_knowledge, path=knowledge_path, root_path=knowledge_path),
            call(server, ui_about, path=about_path, root_path=about_path),
            call(server, plain_chat, path=chat_path, root_path=chat_path),
        ]

        mock_mount_gradio_app.assert_has_calls(expected_calls, any_order=True)
        assert returned_server == app.server
