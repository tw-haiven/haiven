# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
import pytest
from shared.prompts import PromptList
from shared.knowledge import (
    KnowledgeBaseDocuments,
    KnowledgeBaseMarkdown,
    KnowledgeBasePDFs,
    KnowledgeEntryVectorStore,
)
from shared.chats import DocumentsChat, PDFChat, StreamingChat
from shared.llm_config import LLMConfig

from dotenv import load_dotenv


def get_knowledge_entry_pdfs(key) -> KnowledgeEntryVectorStore:
    # Fix root path for the tests
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")
    knowledge_base_pdfs = KnowledgeBasePDFs(
        "team_demo", root_dir=teams_dir, config_file_path="config.yaml"
    )

    return knowledge_base_pdfs.get(key)


def get_knowledge_entry_documents(key) -> KnowledgeEntryVectorStore:
    # Fix root path for the tests
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")
    knowledge_base_documents = KnowledgeBaseDocuments(
        "team_demo", root_dir=teams_dir, config_file_path="config.yaml"
    )

    return knowledge_base_documents.get(key)


def render_prompt(key, user_input):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    prompt_list = PromptList(
        "chat",
        KnowledgeBaseMarkdown("team_demo", root_dir=teams_dir),
        root_dir=teams_dir,
    )
    return prompt_list.render_prompt(key, user_input)


# Fixture to run before all tests
@pytest.fixture(scope="session", autouse=True)
def setup_before_tests():
    os.chdir("./app")


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
    mf_knowledge: KnowledgeEntryVectorStore = get_knowledge_entry_documents("mf-bliki")

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
def test_REAL_CALLS_chat_with_pdf():
    load_dotenv()

    knowledge: KnowledgeEntryVectorStore = get_knowledge_entry_pdfs("test-wikipedia")
    chat_session = PDFChat.create_from_knowledge(
        llm_config=LLMConfig("azure-gpt35", 0.8),
        knowledge_metadata=knowledge,
    )

    answer, sources_markdown = chat_session.next("How long was the first flight?")

    print(answer)
    assert "39.1 seconds" in answer
    assert "Sources of this answer" in sources_markdown


@pytest.mark.integration
def test_REAL_CALLS_chat_with_document():
    load_dotenv()

    knowledge: KnowledgeEntryVectorStore = get_knowledge_entry_documents("mf-bliki")
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


@pytest.mark.integration
def test_REAL_CALL_lm_studio():
    load_dotenv()

    smoke_test_model("lmstudio-local-model")
