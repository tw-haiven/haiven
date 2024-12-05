# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import unittest

from llms.chats import ServerChatSessionMemory, StreamingChat
from unittest.mock import MagicMock, patch

from llms.clients import HaivenAIMessage, HaivenHumanMessage, HaivenSystemMessage


class TestChats(unittest.TestCase):
    @patch("knowledge_manager.KnowledgeManager")
    @patch("logger.HaivenLogger.get")
    def test_streaming_chat(self, mock_logger, mock_knowledge_manager):
        os.environ["USE_AZURE"] = "true"

        mock_chat_client = MagicMock()
        mock_chat_client.stream.return_value = (
            {"content": part} for part in ["Pa", "ris"]
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
