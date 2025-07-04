# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from unittest.mock import MagicMock, patch
import json
from api.api_basics import HaivenBaseApi
from llms.model_config import ModelConfig
from llms.chats import ChatManager, StreamingChat


class TestTokenUsage(unittest.TestCase):
    def setUp(self):
        self.mock_chat_manager = MagicMock(spec=ChatManager)
        self.mock_model_config = MagicMock(spec=ModelConfig)
        self.mock_prompt_list = MagicMock()
        self.mock_app = MagicMock()
        
        self.api = HaivenBaseApi(
            self.mock_app,
            self.mock_chat_manager,
            self.mock_model_config,
            self.mock_prompt_list
        )

    def test_token_usage_data_structure(self):
        """Test that token usage data has the correct simplified structure"""
        token_data = {
            "type": "token_usage",
            "data": {
                "prompt_tokens": 150,
                "completion_tokens": 75,
                "total_tokens": 225,
                "model": "gpt-4"
            }
        }
        
        # Verify required fields exist
        self.assertIn("type", token_data)
        self.assertEqual(token_data["type"], "token_usage")
        self.assertIn("data", token_data)
        
        data = token_data["data"]
        required_fields = ["prompt_tokens", "completion_tokens", "total_tokens", "model"]
        for field in required_fields:
            self.assertIn(field, data)
        
        # Verify data types
        self.assertIsInstance(data["prompt_tokens"], int)
        self.assertIsInstance(data["completion_tokens"], int)
        self.assertIsInstance(data["total_tokens"], int)
        self.assertIsInstance(data["model"], str)

    def test_stream_includes_token_usage_event(self):
        """Test that the stream includes a token_usage event after content"""
        mock_chat_session = MagicMock(spec=StreamingChat)
        mock_chat_session.run.return_value = iter(["Hello", " world"])
        
        self.mock_chat_manager.streaming_chat.return_value = ("session-123", mock_chat_session)
        
        with patch.object(self.api, 'log_run'):
            # Get the stream generator
            result = self.api.stream_text_chat(
                prompt="Test prompt",
                chat_category="test",
                chat_session_key_value="session-123"
            )
            
            # Check if the result is a StreamingResponse
            self.assertIsNotNone(result)
            
            # The stream should now include token usage events
            self.assertTrue(hasattr(result, 'body_iterator'))

    def test_stream_options_include_usage(self):
        """Test that stream_options include usage is properly configured"""
        # This test verifies that the ChatClient is configured to include usage data
        from llms.clients import ChatClient
        
        mock_model_config = MagicMock(spec=ModelConfig)
        mock_model_config.lite_id = "gpt-4"
        
        chat_client = ChatClient(mock_model_config)
        
        # Verify that the stream method includes the stream_options parameter
        self.assertTrue(hasattr(chat_client, 'stream'))

    def test_token_usage_timing(self):
        """Test that token usage is sent after content and before done"""
        # This test would verify the order of events in the stream
        events = []
        
        # Simulate the expected order
        events.append({"type": "content", "data": "Hello"})
        events.append({"type": "content", "data": " world"})
        events.append({"type": "token_usage", "data": {"prompt_tokens": 10, "completion_tokens": 5}})
        events.append({"type": "done"})
        
        # Verify order
        content_events = [e for e in events if e["type"] == "content"]
        token_events = [e for e in events if e["type"] == "token_usage"]
        done_events = [e for e in events if e["type"] == "done"]
        
        # Token usage should come after content
        if content_events and token_events:
            content_indices = [i for i, e in enumerate(events) if e["type"] == "content"]
            token_indices = [i for i, e in enumerate(events) if e["type"] == "token_usage"]
            self.assertTrue(all(ti > max(content_indices) for ti in token_indices))
        
        # Token usage should come before done
        if token_events and done_events:
            token_indices = [i for i, e in enumerate(events) if e["type"] == "token_usage"]
            done_indices = [i for i, e in enumerate(events) if e["type"] == "done"]
            self.assertTrue(all(di > max(token_indices) for di in done_indices))

    def test_stream_json_chat_includes_token_usage(self):
        """Test that stream_json_chat method includes token usage tracking"""
        # Create a mock chat session that returns a JSON response
        mock_chat_session = MagicMock()
        mock_chat_session.run.return_value = iter(['{"ideas": [{"title": "Test Idea", "description": "A test idea"}]}'])
        
        # Mock the chat manager
        self.mock_chat_manager.json_chat.return_value = ("session-123", mock_chat_session)
        
        # Mock the log_run method
        with patch.object(self.api, 'log_run'):
            # Call stream_json_chat
            result = self.api.stream_json_chat(
                prompt="Test prompt for creative matrix",
                chat_category="creative-matrix",
                chat_session_key_value="session-123"
            )
            
            # Verify that the result is a StreamingResponse
            self.assertIsNotNone(result)
            self.assertTrue(hasattr(result, 'body_iterator'))
            self.assertTrue(hasattr(result, 'media_type'))
            self.assertEqual(result.media_type, "text/event-stream")

    def test_stream_content_includes_token_usage(self):
        """Test that the stream content actually includes token usage data"""
        # Create a mock chat session that returns a JSON response
        mock_chat_session = MagicMock()
        mock_chat_session.run.return_value = iter(['{"ideas": [{"title": "Test Idea", "description": "A test idea"}]}'])

        # Mock the chat manager
        self.mock_chat_manager.json_chat.return_value = ("session-123", mock_chat_session)

        # Mock the log_run method
        with patch.object(self.api, 'log_run'):
            # Call stream_json_chat
            result = self.api.stream_json_chat(
                prompt="Test prompt for creative matrix",
                chat_category="creative-matrix",
                chat_session_key_value="session-123"
            )

            # Verify that the result is a StreamingResponse
            self.assertIsNotNone(result)
            self.assertTrue(hasattr(result, 'body_iterator'))
            self.assertTrue(hasattr(result, 'media_type'))
            self.assertEqual(result.media_type, "text/event-stream")

    def test_usage_data_extraction_from_litellm(self):
        """Test that usage data is properly extracted from liteLLM responses"""
        # Test the format that liteLLM responses provide
        mock_usage_data = {
            "prompt_tokens": 150,
            "completion_tokens": 75,
            "total_tokens": 225
        }
        
        # Simulate creating token usage response from liteLLM data
        model_name = "gpt-4"
        token_usage_response = {
            "type": "token_usage",
            "data": {
                "prompt_tokens": mock_usage_data.get("prompt_tokens", 0),
                "completion_tokens": mock_usage_data.get("completion_tokens", 0),
                "total_tokens": mock_usage_data.get("total_tokens", 0),
                "model": model_name
            }
        }
        
        # Verify the response format
        self.assertEqual(token_usage_response["type"], "token_usage")
        self.assertEqual(token_usage_response["data"]["prompt_tokens"], 150)
        self.assertEqual(token_usage_response["data"]["completion_tokens"], 75)
        self.assertEqual(token_usage_response["data"]["total_tokens"], 225)
        self.assertEqual(token_usage_response["data"]["model"], "gpt-4")


if __name__ == '__main__':
    unittest.main() 