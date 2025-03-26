# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
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


def _get_azure_config():
    return ModelConfig(
        "azure-gpt-4o",
        "azure",
        "GPT-4o on Azure",
        config={
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME_GPT4"),
            "api_version": os.environ.get("AZURE_OPENAI_API_VERSION"),
        },
    )


def _get_aws_config():
    return ModelConfig(
        "claude",
        "aws",
        "Claude Sonnet on AWS",
        config={
            "model_id": "${AWS_BEDROCK_REGION}.anthropic.claude-3-5-sonnet-20241022-v2:0"
        },
    )


def _get_google_config():
    return ModelConfig(
        "gemini",
        "gcp",
        "Gemini",
        config={"model": "gemini-1.5-flash"},
    )


def _get_ollama_config():
    return ModelConfig(
        "ollama-llama2",
        "ollama",
        "Llama 2 on ollama",
        config={"model": "llama3:latest"},
    )


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


def run_text_stream_for_model_config(model_config: ModelConfig):
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


def run_json_stream_for_model_config(model_config: ModelConfig):
    config_service = ConfigService(get_app_path() + "/config.yaml")
    chat_manager = create_chat_manager(config_service)

    _, chat_session = chat_manager.json_chat(
        model_config=model_config,
        options=ChatOptions(in_chunks=True, category="integration_test"),
    )

    final_response = ""
    for chunk in chat_session.run("""
        Who are the members of the pop group Spice Girls? 
                                  
        Respond in JSON format giving a list of objects where the name as "title", 
        the style and type of spice they represent "category", and a one sentence 
        biography as "summary":
        
        scenarios: [
            title: str
            category: str
            summary: str
        ]
                                  """):
        chunk_data = json.loads(chunk.strip())
        final_response += chunk_data["data"]

    spice_girls = json.loads(final_response)
    assert len(spice_girls) == 5
    assert spice_girls[0]["title"] is not None
    assert spice_girls[0]["category"] is not None
    assert spice_girls[0]["summary"] is not None


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat_azure(mock_get_config):
    run_text_stream_for_model_config(_get_azure_config())


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_json_azure(mock_get_config):
    run_json_stream_for_model_config(_get_azure_config())


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat_bedrock(mock_get_config):
    run_text_stream_for_model_config(_get_aws_config())


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_json_bedrock(mock_get_config):
    run_json_stream_for_model_config(_get_aws_config())


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat_gemini(mock_get_config):
    run_text_stream_for_model_config(_get_google_config())


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_json_gemini(mock_get_config):
    run_json_stream_for_model_config(_get_google_config())


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat_ollama(mock_get_config):
    run_text_stream_for_model_config(_get_ollama_config())


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_json_ollama(mock_get_config):
    run_json_stream_for_model_config(_get_ollama_config())
