# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from unittest.mock import patch

from llms.llm_config import LLMChatFactory, LLMConfig
from llms.model import Model


class TestLLMChatFactory(unittest.TestCase):
    @patch("llms.llm_config.ConfigService")
    def test_azure_client(self, mock_config_service):
        config_service_instance = mock_config_service.return_value
        config_service_instance.get_model.return_value = Model(
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

        base_chat = LLMChatFactory.new_llm_chat(LLMConfig("azure", 0.5))
        assert base_chat is not None
        assert base_chat.__class__.__name__ == "AzureChatOpenAI"
