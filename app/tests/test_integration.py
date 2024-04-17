# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os

import pytest
from dotenv import load_dotenv
from shared.chats import DocumentsChat, StreamingChat
from shared.knowledge import KnowledgeBaseMarkdown
from shared.llm_config import LLMConfig
from shared.models.document_embedding import DocumentEmbedding
from shared.prompts import PromptList
from shared.services.embeddings_service import EmbeddingsService


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
@pytest.fixture(scope="session", autouse=True)
def setup_before_tests():
    os.chdir("./app")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")
    EmbeddingsService.reset_instance()
    EmbeddingsService.initialize()
    EmbeddingsService.load_knowledge_pack(teams_dir + "/team_demo/knowledge/documents")


@pytest.mark.integration
def test_REAL_CALLS_streaming_chat():
    load_dotenv()

    service = "azure-gpt35"
    default_tone = 0.2
    chat_session = StreamingChat(
        llm_config=LLMConfig(
            service,
            default_tone,
        )
    )

    final_response_history = []
    for chat_history_chunk in chat_session.next("Who is Elvis?", []):
        final_response_history = chat_history_chunk

    assert len(final_response_history) == 1
    assert final_response_history[0][0] == "Who is Elvis?"
    assert "Presley" in final_response_history[0][1]


@pytest.mark.integration
def test_REAL_CALLS_streaming_chat_request_knowledge_advice():
    load_dotenv()

    service = "azure-gpt35"
    default_tone = 0.2
    chat_session = StreamingChat(
        llm_config=LLMConfig(
            service,
            default_tone,
        )
    )

    epic_breakdown_prompt = render_prompt(
        "0d76c75b-c064-464a-9295-2a3ccec2c799",
        "I want sales managers to be able to plan activities to contact their customers. They should be able to plan dates and times for contacts, and document the activities.",
    )
    mf_knowledge: str = "mf-bliki"

    history = []
    for chat_history_chunk in chat_session.start_with_prompt(epic_breakdown_prompt):
        history = chat_history_chunk

    assert len(history) == 1
    assert history[0][0] == epic_breakdown_prompt

    for chat_history_chunk in chat_session.next_advice_from_knowledge(
        history, mf_knowledge
    ):
        history = chat_history_chunk

    assert len(history) == 2


@pytest.mark.integration
def test_REAL_CALLS_chat_with_document():
    load_dotenv()
    knowledge: DocumentEmbedding = EmbeddingsService.get_embedded_document("mf-bliki")
    chat_session = DocumentsChat(
        llm_config=LLMConfig("azure-gpt35", 0.8),
        knowledge=knowledge,
    )

    answer, sources_markdown = chat_session.next(
        "How do I implement Continuous Delivery?"
    )

    print(answer)
    assert "Continuous Delivery" in answer
    assert "These articles were searched as input" in sources_markdown


def smoke_test_model(service_name):
    chat_session = StreamingChat(llm_config=LLMConfig(service_name, 0.8))

    final_response_history = []
    for chat_history_chunk in chat_session.next("Who is Elvis?", []):
        final_response_history = chat_history_chunk

    assert len(final_response_history) == 1
    assert final_response_history[0][0] == "Who is Elvis?"
    assert "Presley" in final_response_history[0][1]


@pytest.mark.integration
def test_REAL_CALL_bedrock_claude():
    load_dotenv()

    smoke_test_model("aws-claude-v2")


@pytest.mark.integration
def test_REAL_CALL_bedrock_claudev3():
    load_dotenv()

    smoke_test_model("aws-claude-v3")


@pytest.mark.integration
def test_REAL_CALL_gemini():
    load_dotenv()

    smoke_test_model("google-gemini")
