# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
import json
import asyncio
from unittest.mock import MagicMock, patch
from api.api_basics import HaivenBaseApi
from llms.model_config import ModelConfig
from llms.chats import ChatManager, StreamingChat, JSONChat


class TestTokenUsageIntegration(unittest.TestCase):
    """
    Integration tests for token usage functionality across different streaming endpoints.
    These tests verify the SSE format for token usage data.
    """

    def setUp(self):
        self.mock_chat_manager = MagicMock(spec=ChatManager)
        self.mock_model_config = MagicMock(spec=ModelConfig)
        self.mock_model_config.lite_id = "gpt-4"
        self.mock_prompt_list = MagicMock()
        self.mock_app = MagicMock()

        self.api = HaivenBaseApi(
            self.mock_app,
            self.mock_chat_manager,
            self.mock_model_config,
            self.mock_prompt_list,
        )

    async def collect_chunks(self, body_iterator):
        """Helper method to collect chunks from async iterator"""
        chunks = []
        async for chunk in body_iterator:
            if isinstance(chunk, bytes):
                chunks.append(chunk.decode("utf-8"))
            else:
                chunks.append(chunk)
        return chunks

    def test_stream_text_chat_token_usage_format(self):
        """Test that stream_text_chat sends token usage in SSE format"""
        # Create mock streaming chat with usage data
        mock_chat_session = MagicMock(spec=StreamingChat)
        mock_chat_session.run.return_value = iter(
            [
                "Hello",
                " world",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )

        self.mock_chat_manager.streaming_chat.return_value = (
            "session-123",
            mock_chat_session,
        )

        with patch.object(self.api, "log_run"):
            result = self.api.stream_text_chat(
                prompt="Test prompt",
                chat_category="chat",
                chat_session_key_value="session-123",
                model_config=self.mock_model_config,
            )

            # Collect all chunks from the stream generator
            chunks = asyncio.run(self.collect_chunks(result.body_iterator))

            # Find the token usage chunk (should be SSE format)
            token_usage_found = False
            for chunk in chunks:
                if "event: token_usage" in chunk and "data:" in chunk:
                    token_usage_found = True
                    # Extract the JSON data from the SSE format
                    lines = chunk.strip().split("\n")
                    data_line = [line for line in lines if line.startswith("data:")][0]
                    json_data = data_line[5:].strip()  # Remove 'data:' prefix

                    # Parse the token usage data
                    usage_data = json.loads(json_data)
                    self.assertEqual(usage_data["total_tokens"], 300)
                    self.assertEqual(usage_data["prompt_tokens"], 100)
                    self.assertEqual(usage_data["completion_tokens"], 200)
                    self.assertEqual(usage_data["model"], "gpt-4")
                    break

            self.assertTrue(
                token_usage_found, "Token usage SSE event should be present"
            )

    def test_stream_json_chat_token_usage_format(self):
        """Test that stream_json_chat sends token usage in SSE format"""
        # Create mock JSON chat with usage data
        mock_chat_session = MagicMock(spec=JSONChat)
        mock_chat_session.run.return_value = iter(
            [
                '{"ideas": [{"title": "Test"}]}',
                {
                    "usage": {
                        "prompt_tokens": 150,
                        "completion_tokens": 250,
                        "total_tokens": 400,
                    }
                },
            ]
        )

        self.mock_chat_manager.json_chat.return_value = (
            "session-456",
            mock_chat_session,
        )

        with patch.object(self.api, "log_run"):
            result = self.api.stream_json_chat(
                prompt="Test creative matrix prompt",
                chat_category="creative-matrix",
                chat_session_key_value="session-456",
                model_config=self.mock_model_config,
            )

            # Collect all chunks from the stream
            chunks = asyncio.run(self.collect_chunks(result.body_iterator))

            # Find the token usage chunk (should be SSE format)
            token_usage_found = False
            content_found = False

            for chunk in chunks:
                if "event: token_usage" in chunk and "data:" in chunk:
                    token_usage_found = True
                    # Extract the JSON data from the SSE format
                    lines = chunk.strip().split("\n")
                    data_line = [line for line in lines if line.startswith("data:")][0]
                    json_data = data_line[5:].strip()  # Remove 'data:' prefix

                    # Parse the token usage data
                    usage_data = json.loads(json_data)
                    self.assertEqual(usage_data["total_tokens"], 400)
                    self.assertEqual(usage_data["prompt_tokens"], 150)
                    self.assertEqual(usage_data["completion_tokens"], 250)
                    self.assertEqual(usage_data["model"], "gpt-4")
                elif '{"ideas"' in chunk:
                    content_found = True

            self.assertTrue(
                token_usage_found, "Token usage SSE event should be present"
            )
            self.assertTrue(content_found, "Content should be streamed")

    def test_token_usage_format_compatibility_with_fetchsse(self):
        """Test that JSON chat token usage format is compatible with fetchSSE expectations"""
        # This test simulates how fetchSSE processes chunks
        mock_chat_session = MagicMock(spec=JSONChat)
        mock_chat_session.run.return_value = iter(
            [
                '{"ideas": [{"title": "Test"}]}',
                {
                    "usage": {
                        "prompt_tokens": 150,
                        "completion_tokens": 250,
                        "total_tokens": 400,
                    }
                },
            ]
        )

        self.mock_chat_manager.json_chat.return_value = (
            "session-456",
            mock_chat_session,
        )

        with patch.object(self.api, "log_run"):
            result = self.api.stream_json_chat(
                prompt="Test creative matrix prompt",
                chat_category="creative-matrix",
                chat_session_key_value="session-456",
                model_config=self.mock_model_config,
            )

            # Simulate fetchSSE processing
            chunks = asyncio.run(self.collect_chunks(result.body_iterator))

            # All chunks should be properly formatted - no JSON parsing errors
            for chunk in chunks:
                # SSE events should be properly formatted
                if "event: token_usage" in chunk:
                    self.assertIn("data:", chunk)
                    # Verify we can extract and parse the data
                    lines = chunk.strip().split("\n")
                    data_line = [line for line in lines if line.startswith("data:")][0]
                    json_data = data_line[5:].strip()
                    # This should not raise a JSONDecodeError
                    parsed_data = json.loads(json_data)
                    self.assertIn("total_tokens", parsed_data)

    def test_error_message_format_compatibility(self):
        """Test that error messages are formatted correctly for different endpoints"""
        # Test that JSON chat errors are wrapped in {"data": "..."} format
        mock_chat_session = MagicMock(spec=JSONChat)
        mock_chat_session.run.side_effect = Exception("Test error")

        self.mock_chat_manager.json_chat.return_value = (
            "session-456",
            mock_chat_session,
        )

        with patch.object(self.api, "log_run"):
            result = self.api.stream_json_chat(
                prompt="Test prompt that will fail",
                chat_category="creative-matrix",
                chat_session_key_value="session-456",
                model_config=self.mock_model_config,
            )

            # Collect error chunks
            chunks = asyncio.run(self.collect_chunks(result.body_iterator))
            error_chunks = [chunk for chunk in chunks if "[ERROR]" in chunk]

            # Verify error messages are properly formatted as JSON
            self.assertTrue(len(error_chunks) > 0, "Should have error chunks")

            for error_chunk in error_chunks:
                # Should be valid JSON
                try:
                    parsed = json.loads(error_chunk)
                    self.assertIn("data", parsed)
                    self.assertIn("[ERROR]", parsed["data"])
                except json.JSONDecodeError:
                    self.fail(f"Error chunk should be valid JSON: {error_chunk}")

    def test_token_usage_data_structure_consistency(self):
        """Test that token usage data structure is consistent across endpoints"""
        # Test both endpoints return the same token usage structure
        mock_streaming_chat = MagicMock(spec=StreamingChat)
        mock_streaming_chat.run.return_value = iter(
            [
                "Content",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )

        mock_json_chat = MagicMock(spec=JSONChat)
        mock_json_chat.run.return_value = iter(
            [
                '{"ideas": []}',
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )

        self.mock_chat_manager.streaming_chat.return_value = (
            "session-1",
            mock_streaming_chat,
        )
        self.mock_chat_manager.json_chat.return_value = ("session-2", mock_json_chat)

        with patch.object(self.api, "log_run"):
            # Get token usage from both endpoints
            text_result = self.api.stream_text_chat(
                prompt="Test",
                chat_category="chat",
                chat_session_key_value="session-1",
                model_config=self.mock_model_config,
            )
            json_result = self.api.stream_json_chat(
                prompt="Test",
                chat_category="creative-matrix",
                chat_session_key_value="session-2",
                model_config=self.mock_model_config,
            )

            # Extract token usage from both
            text_chunks = asyncio.run(self.collect_chunks(text_result.body_iterator))
            json_chunks = asyncio.run(self.collect_chunks(json_result.body_iterator))

            text_token_usage = None
            json_token_usage = None

            # Extract token usage from text stream
            for chunk in text_chunks:
                if "event: token_usage" in chunk and "data:" in chunk:
                    lines = chunk.strip().split("\n")
                    data_line = [line for line in lines if line.startswith("data:")][0]
                    json_data = data_line[5:].strip()
                    text_token_usage = json.loads(json_data)
                    break

            # Extract token usage from JSON stream
            for chunk in json_chunks:
                if "event: token_usage" in chunk and "data:" in chunk:
                    lines = chunk.strip().split("\n")
                    data_line = [line for line in lines if line.startswith("data:")][0]
                    json_data = data_line[5:].strip()
                    json_token_usage = json.loads(json_data)
                    break

            # Both should have the same data structure
            self.assertIsNotNone(text_token_usage, "Text token usage should be found")
            self.assertIsNotNone(json_token_usage, "JSON token usage should be found")

            # Verify structure consistency (both will be non-None after assertions above)
            if text_token_usage and json_token_usage:
                self.assertEqual(
                    text_token_usage["total_tokens"], json_token_usage["total_tokens"]
                )
                self.assertEqual(text_token_usage["model"], json_token_usage["model"])


if __name__ == "__main__":
    unittest.main()
