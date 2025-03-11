# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import unittest

from llms.chats import ServerChatSessionMemory, StreamingChat, JSONChat, HaivenBaseChat
from unittest.mock import MagicMock, patch

from llms.clients import HaivenAIMessage, HaivenHumanMessage, HaivenSystemMessage
from config.constants import SYSTEM_MESSAGE


class TestChats(unittest.TestCase):
    @patch("knowledge_manager.KnowledgeManager")
    @patch("logger.HaivenLogger.get")
    def test_streaming_chat(self, mock_logger, mock_knowledge_manager):
        os.environ["USE_AZURE"] = "true"

        # Setup knowledge manager to return a specific system message
        custom_system_message = "You are a test assistant"
        mock_knowledge_manager.get_system_message.return_value = custom_system_message

        mock_chat_client = MagicMock()
        mock_chat_client.stream.return_value = (
            {"content": part} for part in ["Pa", "ris"]
        )

        streaming_chat = StreamingChat(
            chat_client=mock_chat_client, knowledge_manager=mock_knowledge_manager
        )

        # Verify system message is correctly set from knowledge manager
        assert streaming_chat.system == custom_system_message
        assert len(streaming_chat.memory) == 1
        assert isinstance(streaming_chat.memory[0], HaivenSystemMessage)
        assert streaming_chat.memory[0].content == custom_system_message

        # Verify knowledge manager was called to get the system message
        mock_knowledge_manager.get_system_message.assert_called_once()

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

    @patch("knowledge_manager.KnowledgeManager")
    def test_json_chat(self, mock_knowledge_manager):
        # Setup knowledge manager to return a specific system message
        custom_system_message = "You are a test assistant"
        mock_knowledge_manager.get_system_message.return_value = custom_system_message

        mock_chat_client = MagicMock()
        actual_chunks = (
            {"content": '{"key":"v'},
            {"content": 'alue"}'},
            {"metadata": {"citations": ["test.url"]}},
        )
        mock_chat_client.stream.return_value = actual_chunks

        json_chat = JSONChat(
            chat_client=mock_chat_client, knowledge_manager=mock_knowledge_manager
        )

        # Verify system message is correctly set from knowledge manager
        assert json_chat.system == custom_system_message
        assert len(json_chat.memory) == 1
        assert isinstance(json_chat.memory[0], HaivenSystemMessage)
        assert json_chat.memory[0].content == custom_system_message

        # Verify knowledge manager was called to get the system message
        mock_knowledge_manager.get_system_message.assert_called_once()

        # Test run method - collect the generator output
        question = "What is the capital of France?"
        response_generator = json_chat.run(question)

        # Get the first response chunk
        actual_streamed_response = ""
        for chunk in actual_chunks:
            actual_streamed_response += next(response_generator)

        # Verify the response is encoding the JSON data as it is expected by the frontend
        assert (
            '{"data": "{\\"key\\":\\"v"}'
            + "\n\n"
            + '{"data": "alue\\"}"}'
            + "\n\n"
            + '{"metadata": {"citations": ["test.url"]}}'
            == actual_streamed_response
        )

        # Verify the memory was updated correctly
        assert len(json_chat.memory) == 3
        assert isinstance(json_chat.memory[1], HaivenHumanMessage)
        assert json_chat.memory[1].content == question
        assert isinstance(json_chat.memory[2], HaivenAIMessage)
        assert json_chat.memory[2].content == '{"key":"value"}'

    @patch("knowledge_manager.KnowledgeManager")
    def test_haiven_base_chat(self, mock_knowledge_manager):
        # Setup knowledge manager to return the default system message
        mock_knowledge_manager.get_system_message.return_value = SYSTEM_MESSAGE

        mock_chat_client = MagicMock()

        # Create base chat instance
        base_chat = HaivenBaseChat(
            chat_client=mock_chat_client, knowledge_manager=mock_knowledge_manager
        )

        # Verify system message is correctly set from knowledge manager
        assert base_chat.system == SYSTEM_MESSAGE
        assert len(base_chat.memory) == 1
        assert isinstance(base_chat.memory[0], HaivenSystemMessage)
        assert base_chat.memory[0].content == SYSTEM_MESSAGE

        # Test memory_as_text method
        memory_text = base_chat.memory_as_text()
        # Just check if the memory_as_text method returns a non-empty string
        # that contains some part of the system message
        assert isinstance(memory_text, str)
        assert len(memory_text) > 0
        # Check for a unique substring from the system message
        assert "You are Haiven" in memory_text
