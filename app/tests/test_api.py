# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from api.api_scenarios import enable_scenarios
from api.api_story_validation import enable_story_validation


class TestApi(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.client = TestClient(self.app)

    def tearDown(self):
        # Clean up code to run after each test
        pass

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_scenarios(
        self, mock_json_chat, mock_chat_session_memory, mock_prompt_list
    ):
        mock_json_chat.run.return_value = "some response from the model"
        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        enable_scenarios(
            self.app, mock_chat_session_memory, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        response = self.client.get("/api/make-scenario")

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_scenarios_explore(
        self, mock_streaming_chat, mock_chat_session_memory, mock_prompt_list
    ):
        mock_streaming_chat.start_with_prompt.return_value = (
            "some response from the model"
        )

        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        enable_scenarios(
            self.app, mock_chat_session_memory, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        response = self.client.post(
            "/api/scenario/explore",
            json={
                "userMessage": "some user question",
                "item": "some scenario item",
                "originalInput": "some original prompt",
                "chatSessionId": "some session id",
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_post_story_validation(
        self, mock_json_chat, mock_chat_session_memory, mock_prompt_list
    ):
        mock_json_chat.run.return_value = "some response from the model"
        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        enable_story_validation(self.app, mock_chat_session_memory, mock_prompt_list)

        # Make the request to the endpoint
        response = self.client.post(
            "/api/story-validation/questions", json={"input": "some user input"}
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"
