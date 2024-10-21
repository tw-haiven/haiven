# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from config_service import ConfigService
from knowledge_manager import KnowledgeManager
from llms.chats import ChatManager, ChatOptions, ServerChatSessionMemory
from llms.clients import ChatClientFactory
from llms.model_config import ModelConfig
from main import backwards_compat_env_vars
from tests.utils import get_app_path


@pytest.fixture(scope="session", autouse=True)
def setup_before_tests():
    load_dotenv()
    backwards_compat_env_vars()
    os.environ.update({"ENABLED_PROVIDERS": "azure,aws,google,ollama"})


def create_chat_manager(config_service):
    knowledge_manager = KnowledgeManager(config_service=config_service)

    chat_session_memory = ServerChatSessionMemory()
    llm_chat_factory = ChatClientFactory(config_service)
    chat_manager = ChatManager(
        config_service, chat_session_memory, llm_chat_factory, knowledge_manager
    )
    return chat_manager


def run_for_model_config(model_config: ModelConfig):
    config_service = ConfigService(get_app_path() + "/config.yaml")
    chat_manager = create_chat_manager(config_service)

    _, chat_session = chat_manager.streaming_chat(
        model_config=model_config,
        options=ChatOptions(in_chunks=True, category="integration_test"),
    )

    final_response = ""
    for chunk in chat_session.run("Who is Elvis?"):
        final_response += chunk

    assert "Presley" in final_response


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat_azure(mock_get_config):
    run_for_model_config(
        ModelConfig(
            "azure-gpt4",
            "azure",
            "GPT4 on Azure",
            config={
                "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME_GPT4"),
                "api_version": os.environ.get("AZURE_OPENAI_API_VERSION"),
            },
        )
    )


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat_bedrock(mock_get_config):
    run_for_model_config(
        ModelConfig(
            "sonnet",
            "aws",
            "Sonnet on AWS",
            config={"model_id": "anthropic.claude-3-sonnet-20240229-v1:0"},
        )
    )


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat_gemini(mock_get_config):
    run_for_model_config(
        ModelConfig(
            "gemini",
            "google",
            "Gemini",
            config={"model": "gemini-1.5-flash"},
        )
    )


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat_ollama(mock_get_config):
    run_for_model_config(
        ModelConfig(
            "ollama-llama2",
            "ollama",
            "Llama 2 on ollama",
            config={"model": "llama3:latest"},
        )
    )
