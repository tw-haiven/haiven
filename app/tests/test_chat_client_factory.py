# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from unittest.mock import patch

from llms.clients import ChatClientFactory, ModelConfig


class TestChatClientFactory(unittest.TestCase):
    @patch("llms.clients.ConfigService")
    def test_azure_client(self, mock_config_service):
        base_chat = ChatClientFactory(mock_config_service).new_chat_client(
            ModelConfig(
                "some-id",
                "azure",
                "Some name",
                config={
                    "api_key": "some value",
                    "azure_deployment": "some value",
                    "azure_endpoint": "some value",
                    "api_version": "some value",
                },
            )
        )
        assert base_chat is not None
        assert base_chat.__class__.__name__ == "ChatClient"
