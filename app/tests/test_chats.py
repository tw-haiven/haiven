# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

from langchain.docstore.document import Document
from llms.chats import DocumentsChat, ServerChatSessionMemory
from llms.llm_config import LLMConfig
from unittest.mock import MagicMock


def test_documents_chat(mocker):
    os.environ["USE_AZURE"] = "true"

    mocker.patch("logger.HaivenLogger.get", return_value=mocker.Mock())

    knowledge_base_mock = mocker.Mock()
    knowledge_base_mock.retriever = mocker.Mock()
    chat_model_mock = mocker.Mock()
    mocker.patch(
        "llms.llm_config.LLMChatFactory.new_llm_chat",
        return_value=chat_model_mock,
    )

    documents = [
        Document(
            page_content="Some doc content",
            metadata={"source": "http://somewebsite.com", "title": "Some Website"},
        )
    ]
    mocker.patch(
        "embeddings.embeddings_service.EmbeddingsService.similarity_search_on_single_document",
        return_value=[document for document in documents],
    )

    chain_mock = mocker.Mock()
    chain_mock.return_value = {"output_text": "Paris", "source_documents": documents}
    mocker.patch("llms.chats.DocumentsChat.create_chain", return_value=chain_mock)

    service = "azure-gpt35"
    default_tone = "more precise (0.2)"
    documents_chat = DocumentsChat(
        llm_config=LLMConfig(
            service,
            default_tone,
        ),
        knowledge=knowledge_base_mock,
        context="test_context",
    )

    question = "What is the capital of France?"
    expected_prompt = documents_chat.build_prompt(question)
    answer, sources = documents_chat.next(question)

    chain_mock.assert_called_once_with(
        {"input_documents": documents, "question": expected_prompt}
    )
    assert answer == "Paris"
    assert "These sources were searched" in sources
    assert "Some Website" in sources


def test_dump_as_text():
    # Arrange
    category = "category"
    user_owner = "user_owner"

    expected_result = "Chat session memory as text"
    chat_session = MagicMock()
    chat_session.memory_as_text.return_value = expected_result

    # Act
    session_memory = ServerChatSessionMemory()
    session_key = session_memory.add_new_entry(category, user_owner)
    session_memory.store_chat(session_key, chat_session)

    result = session_memory.dump_as_text(session_key, user_owner)

    # Assert
    assert result == expected_result


def test_dump_as_text_should_not_return_data_if_not_owned_by_user():
    # Arrange
    category = "category"
    user_owner = "user_owner"

    expected_result = "Chat session memory as text"
    chat_session = MagicMock()
    chat_session.memory_as_text.return_value = expected_result

    session_memory = ServerChatSessionMemory()
    session_key = session_memory.add_new_entry(category, user_owner)
    session_memory.store_chat(session_key, chat_session)

    # Act
    result = session_memory.dump_as_text(session_key, "another_user")

    # Assert
    assert "not found for this user" in result
