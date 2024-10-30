# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import unittest

from langchain.docstore.document import Document
from llms.chats import DocumentsChat, ServerChatSessionMemory, StreamingChat
from unittest.mock import MagicMock, patch

from llms.clients import HaivenAIMessage, HaivenHumanMessage, HaivenSystemMessage


class TestChats(unittest.TestCase):
    @patch("llms.chats.DocumentsChat._create_chain")
    @patch("knowledge_manager.KnowledgeManager")
    @patch("logger.HaivenLogger.get")
    def test_documents_chat(
        self, mock_logger, mock_knowledge_manager, mock_create_chain
    ):
        os.environ["USE_AZURE"] = "true"

        document_embedding_mock = MagicMock()
        document_embedding_mock.retriever = MagicMock()

        expected_documents = [
            Document(
                page_content="Some doc content",
                metadata={"source": "http://somewebsite.com", "title": "Some Website"},
            )
        ]

        mock_knowledge_base_documents = MagicMock()
        mock_knowledge_manager.knowledge_base_documents = mock_knowledge_base_documents
        mock_knowledge_base_documents.similarity_search_on_single_document.return_value = [
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
            knowledge_manager=mock_knowledge_manager,
            knowledge="a-document-key",
            context="test_context",
        )

        question = "What is the capital of France?"
        answer, sources_markdown = documents_chat.run(question)

        args, _ = chain_fn_mock.call_args
        assert args[0]["input_documents"] == expected_documents
        assert question in args[0]["question"]

        assert answer == "Paris"
        assert "These sources were searched" in sources_markdown
        assert "Some Website" in sources_markdown

    @patch("knowledge_manager.KnowledgeManager")
    @patch("logger.HaivenLogger.get")
    def test_streaming_chat(self, mock_logger, mock_knowledge_manager):
        os.environ["USE_AZURE"] = "true"

        mock_chat_client = MagicMock()
        mock_chat_client.stream.return_value = iter(
            [
                MagicMock(content="Pa"),
                MagicMock(content="ris"),
            ]
        )

        streaming_chat = StreamingChat(
            chat_client=mock_chat_client, knowledge_manager=mock_knowledge_manager
        )

        assert len(streaming_chat.memory) == 1
        assert isinstance(streaming_chat.memory[0], HaivenSystemMessage)

        question = "What is the capital of France?"
        answer = streaming_chat.run(question)

        assert next(answer) == "Pa"
        assert next(answer) == "ris"
        assert len(streaming_chat.memory) == 3
        assert isinstance(streaming_chat.memory[1], HaivenHumanMessage)
        assert isinstance(streaming_chat.memory[2], HaivenAIMessage)

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
