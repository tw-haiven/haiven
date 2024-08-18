# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import unittest

from langchain.docstore.document import Document
from llms.chats import DocumentsChat, ServerChatSessionMemory
from unittest.mock import MagicMock, patch


class TestChats(unittest.TestCase):
    @patch("llms.chats.DocumentsChat.create_chain")
    @patch("content_manager.ContentManager")
    @patch("logger.HaivenLogger.get")
    def test_documents_chat(self, mock_logger, mock_content_manager, mock_create_chain):
        os.environ["USE_AZURE"] = "true"

        document_embedding_mock = MagicMock()
        document_embedding_mock.retriever = MagicMock()

        expected_documents = [
            Document(
                page_content="Some doc content",
                metadata={"source": "http://somewebsite.com", "title": "Some Website"},
            )
        ]

        embeddings_service = MagicMock()
        mock_content_manager.embeddings_service = embeddings_service
        embeddings_service.similarity_search_on_single_document.return_value = [
            document for document in expected_documents
        ]

        chain_fn_mock = MagicMock()
        chain_fn_mock.return_value = {
            "output_text": "Paris",
            "source_documents": expected_documents,
        }
        mock_create_chain.return_value = chain_fn_mock

        documents_chat = DocumentsChat(
            chat_client=MagicMock(),
            content_manager=mock_content_manager,
            knowledge="a-document-key",
            context="test_context",
        )

        question = "What is the capital of France?"
        answer, sources_markdown = documents_chat.next(question)

        args, _ = chain_fn_mock.call_args
        assert args[0]["input_documents"] == expected_documents
        assert question in args[0]["question"]

        assert answer == "Paris"
        assert "These sources were searched" in sources_markdown
        assert "Some Website" in sources_markdown

    def test_dump_as_text(self):
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

    def test_dump_as_text_should_not_return_data_if_not_owned_by_user(self):
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
