# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from unittest.mock import patch

from langchain_openai import AzureChatOpenAI
import pytest
from dotenv import load_dotenv

from config_service import ConfigService
from knowledge.markdown import KnowledgeBaseMarkdown
from knowledge_manager import KnowledgeManager
from llms.chats import StreamingChat
from llms.clients import ChatClient
from prompts.prompts import PromptList
from tests.utils import get_app_path


def render_prompt(key, user_input):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    prompt_list = PromptList(
        "chat",
        KnowledgeBaseMarkdown(path=teams_dir + "/team_demo/knowledge"),
        root_dir=teams_dir,
    )
    return prompt_list.render_prompt(key, user_input)


# Fixture to run before all tests
# @pytest.fixture(scope="session", autouse=True)
# def setup_before_tests():
#     os.chdir("./app")
#     root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     teams_dir = os.path.join(root_dir, "teams")
#     EmbeddingsService.reset_instance()
#     EmbeddingsService.initialize()
#     EmbeddingsService.load_knowledge_base(teams_dir + "/team_demo/knowledge/documents")


@pytest.mark.integration
@patch.object(ConfigService, "load_knowledge_pack_path", return_value="")
def test_REAL_CALLS_streaming_chat(mock_get_config):
    load_dotenv()

    config_service = ConfigService(get_app_path() + "/config.yaml")
    # knowledge_pack_path = "../" + config_service.load_knowledge_pack_path()
    knowledge_manager = KnowledgeManager(config_service=config_service)

    chat_client = ChatClient(
        AzureChatOpenAI(
            openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            azure_deployment="gpt-4",
            azure_endpoint=os.environ.get("AZURE_OPENAI_API_BASE"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            temperature=0.5,
        )
    )
    chat_session = StreamingChat(
        chat_client=chat_client, knowledge_manager=knowledge_manager
    )

    final_response = ""
    for chat_history_chunk in enumerate(chat_session.run("Who is Elvis?")):
        final_response += chat_history_chunk[1]

    assert "Presley" in final_response
