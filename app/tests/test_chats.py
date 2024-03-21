# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os

from langchain.docstore.document import Document
from shared.models.embedding_model import EmbeddingModel
from shared.chats import DocumentsChat, PDFChat, ServerChatSessionMemory
from shared.llm_config import LLMConfig
from unittest import mock
from unittest.mock import MagicMock


def test_pdf_chat(mocker):
    # TODO: Investigate why not mocking the logger breaks the tests
    os.environ["USE_AZURE"] = "true"

    mocker.patch("shared.logger.TeamAILogger.get", return_value=mocker.Mock())

    knowledge_base_mock = mocker.Mock()
    knowledge_base_mock.retriever = mocker.Mock()
    chat_model_mock = mocker.Mock()
    mocker.patch(
        "shared.llm_config.LLMChatFactory.new_llm_chat",
        return_value=chat_model_mock,
    )

    chain_mock = mocker.Mock()
    chain_mock.return_value = {"result": "Paris", "source_documents": []}
    mocker.patch("shared.chats.PDFChat.create_chain", return_value=chain_mock)

    service = "azure-gpt35"
    default_tone = "more precise (0.2)"
    pdf_chat = PDFChat.create_from_knowledge(
        llm_config=LLMConfig(
            service,
            default_tone,
        ),
        knowledge_metadata=knowledge_base_mock,
    )

    question = "What is the capital of France?"
    answer, sources = pdf_chat.next(question)

    chain_mock.assert_called_once_with("What is the capital of France?")
    assert answer == "Paris"
    assert "**Sources of this answer (ranked)**" in sources


def test_documents_chat(mocker):
    os.environ["USE_AZURE"] = "true"

    mocker.patch("shared.logger.TeamAILogger.get", return_value=mocker.Mock())

    knowledge_base_mock = mocker.Mock()
    knowledge_base_mock.retriever = mocker.Mock()
    chat_model_mock = mocker.Mock()
    mocker.patch(
        "shared.llm_config.LLMChatFactory.new_llm_chat",
        return_value=chat_model_mock,
    )

    documents = [
        Document(
            page_content="Some doc content",
            metadata={"source": "http://somewebsite.com", "title": "Some Website"},
        )
    ]
    mocker.patch(
        "shared.document_retriever.DocumentRetrieval.get_docs_and_sources_from_document_store",
        return_value=documents,
    )

    chain_mock = mocker.Mock()
    chain_mock.return_value = {"output_text": "Paris", "source_documents": documents}
    mocker.patch("shared.chats.DocumentsChat.create_chain", return_value=chain_mock)

    service = "azure-gpt35"
    default_tone = "more precise (0.2)"
    documents_chat = DocumentsChat(
        llm_config=LLMConfig(
            service,
            default_tone,
        ),
        knowledge=knowledge_base_mock,
    )

    question = "What is the capital of France?"
    answer, sources = documents_chat.next(question)

    chain_mock.assert_called_once_with(
        {"input_documents": documents, "question": "What is the capital of France?"}
    )
    assert answer == "Paris"
    assert "These articles were searched" in sources
    assert "Some Website" in sources


@mock.patch("shared.services.config_service.ConfigService.load_embedding_model")
@mock.patch("shared.chats.get_text_and_metadata_from_pdf")
@mock.patch("shared.chats.Embeddings.generate_from_documents")
@mock.patch("shared.chats.PDFChat")
def test_create_from_uploaded_pdf(
    pdf_chat_mock,
    generate_from_documents_mock,
    get_text_and_metadata_mock,
    load_embedding_model_mock,
):
    text = "text"
    metadata = "metadata"
    get_text_and_metadata_mock.return_value = (text, metadata)

    knowledge = "knowledge"
    generate_from_documents_mock.return_value = knowledge

    pdf_chat = "pdf_chat"
    pdf_chat_mock.return_value = pdf_chat

    embedding_model = EmbeddingModel(
        id="text-embedding-ada-002",
        name="Ada",
        provider="Azure",
        config={
            "api_key": "test",
            "azure_endpoint": "test",
            "azure_deployment": "test",
            "api_version": "test",
        },
    )
    load_embedding_model_mock.return_value = embedding_model

    llm_config = LLMConfig("service_value", "tone")
    upload_file_name = "file.pdf"
    with open(upload_file_name, "wb") as file:
        file.write(b"This is a sample PDF content")

    PDFChat.create_from_uploaded_pdf(llm_config, upload_file_name)

    generate_from_documents_mock.assert_called_once_with(text, metadata)
    pdf_chat_mock.assert_called_once_with(
        llm_config, knowledge, "You are a helpful assistant"
    )

    os.remove(upload_file_name)


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
