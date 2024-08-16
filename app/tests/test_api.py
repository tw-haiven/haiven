# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from unittest.mock import patch, ANY
from fastapi.testclient import TestClient
from fastapi import FastAPI

from api.api_story_validation import enable_story_validation
from api.api_scenarios import ApiScenarios
from api.api_threat_modelling import ApiThreatModelling
from api.api_requirements import ApiRequirementsBreakdown


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
        self,
        mock_prompt_list,
        mock_chat_session_memory,
        mock_json_chat,
    ):
        mock_json_chat.run.return_value = "some response from the model"
        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        ApiScenarios(
            self.app, mock_chat_session_memory, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        input = "someinput"
        num_scenarios = "3"
        time_horizon = "5"
        optimism = "optimistic"
        realism = "futuristic sci-fi"
        response = self.client.get(
            f"/api/make-scenario?input={input}&num_scenarios={num_scenarios}&time_horizon={time_horizon}&optimism={optimism}&realism={realism}&detail=true"
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"
        mock_prompt_list.render_prompt.assert_called_with(
            active_knowledge_context=ANY,
            prompt_choice="guided-scenarios-detailed",
            user_input=ANY,
            additional_vars={
                "input": input,
                "num_scenarios": num_scenarios,
                "time_horizon": time_horizon,
                "optimism": optimism,
                "realism": realism,
            },
            warnings=ANY,
        )

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_scenarios_explore(
        self,
        mock_prompt_list,
        mock_chat_session_memory,
        mock_streaming_chat,
    ):
        mock_streaming_chat.start_with_prompt.return_value = (
            "some response from the model"
        )

        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        ApiScenarios(
            self.app, mock_chat_session_memory, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        response = self.client.post(
            "/api/scenario/explore",
            json={
                "userMessage": "some user question",
                "item": "some scenario item",
                "originalInput": "some original prompt",
                "chatSessionId": None,
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"

        args, kwargs = mock_chat_session_memory.get_or_create_chat.call_args
        assert kwargs["chat_category"] == "scenarios-explore"
        assert kwargs["chat_session_key_value"] is None

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_threat_modelling(
        self, mock_prompt_list, mock_chat_session_memory, mock_json_chat
    ):
        mock_json_chat.run.return_value = "some response from the model"
        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        ApiThreatModelling(
            self.app, mock_chat_session_memory, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        dataFlow = "some data flow"
        assets = "some assets"
        userBase = "some user description"
        response = self.client.get(
            f"/api/threat-modelling?dataFlow={dataFlow}&assets={assets}&userBase={userBase}"
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"
        mock_prompt_list.render_prompt.assert_called_with(
            active_knowledge_context=ANY,
            prompt_choice="guided-threat-modelling",
            user_input=ANY,
            additional_vars={
                "dataFlow": dataFlow,
                "assets": assets,
                "userBase": userBase,
            },
            warnings=ANY,
        )

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_threat_modelling_explore(
        self, mock_prompt_list, mock_chat_session_memory, mock_streaming_chat
    ):
        mock_streaming_chat.start_with_prompt.return_value = (
            "some response from the model"
        )

        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        ApiThreatModelling(
            self.app, mock_chat_session_memory, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        response = self.client.post(
            "/api/threat-modelling/explore",
            json={
                "userMessage": "some user question",
                "item": "some scenario item",
                "originalInput": "some original prompt",
                "chatSessionId": None,
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"

        args, kwargs = mock_chat_session_memory.get_or_create_chat.call_args
        assert kwargs["chat_category"] == "threat-modelling-explore"
        assert kwargs["chat_session_key_value"] is None

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_requirements(
        self,
        mock_prompt_list,
        mock_chat_session_memory,
        mock_json_chat,
    ):
        mock_json_chat.run.return_value = "some response from the model"
        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        ApiRequirementsBreakdown(
            self.app, mock_chat_session_memory, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        user_input = "some user input"
        response = self.client.get(f"/api/requirements?input={user_input}")

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"
        mock_prompt_list.render_prompt.assert_called_with(
            active_knowledge_context=ANY,
            prompt_choice="guided-requirements",
            user_input=user_input,
            additional_vars={},
            warnings=ANY,
        )

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_requirements_explore(
        self,
        mock_prompt_list,
        mock_chat_session_memory,
        mock_streaming_chat,
    ):
        mock_streaming_chat.start_with_prompt.return_value = (
            "some response from the model"
        )

        mock_chat_session_memory.get_or_create_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt"
        ApiRequirementsBreakdown(
            self.app, mock_chat_session_memory, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        response = self.client.post(
            "/api/requirements/explore",
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

        args, kwargs = mock_chat_session_memory.get_or_create_chat.call_args
        assert kwargs["chat_category"] == "requirements-breakdown-explore"
        assert kwargs["chat_session_key_value"] == "some session id"

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ServerChatSessionMemory")
    @patch("prompts.prompts.PromptList")
    def test_story_validation(
        self,
        mock_prompt_list,
        mock_chat_session_memory,
        mock_json_chat,
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
