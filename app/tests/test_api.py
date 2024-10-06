# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import unittest
from unittest.mock import MagicMock, patch, ANY
from fastapi.testclient import TestClient
from fastapi import FastAPI

from api.api_basics import ApiBasics
from api.api_scenarios import ApiScenarios
from api.api_threat_modelling import ApiThreatModelling
from api.api_requirements import ApiRequirementsBreakdown
from api.api_story_validation import ApiStoryValidation
from api.api_creative_matrix import ApiCreativeMatrix


class TestApi(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.client = TestClient(self.app)

    def tearDown(self):
        # Clean up code to run after each test
        pass

    def test_get_documents(self):
        mock_knowledge_manager = MagicMock()
        mock_knowledge_manager.get_all_context_keys.return_value = [
            "context1",
            "context2",
        ]

        mock_kb_documents = MagicMock()
        mock_doc_base = MagicMock(
            key="some-document-base",
            title="Some title base",
            description="Some description",
        )
        mock_doc_base.get_source_title_link.return_value = "some source title link"
        mock_doc_1 = MagicMock(
            key="some-document-1", title="Some title 1", description="Some description"
        )
        mock_doc_1.get_source_title_link.return_value = "some source title link"
        mock_doc_2 = MagicMock(
            key="some-document-2", title="Some title 2", description="Some description"
        )
        mock_doc_2.get_source_title_link.return_value = "some source title link"
        mock_kb_documents.get_documents.side_effect = [
            [mock_doc_base],
            [mock_doc_1],
            [mock_doc_2],
        ]
        mock_knowledge_manager.knowledge_base_documents = mock_kb_documents

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_key="some_model_key",
            prompts_guided=MagicMock(),
            knowledge_manager=mock_knowledge_manager,
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
        )

        response = self.client.get("/api/knowledge/documents")

        # Assert the response
        assert response.status_code == 200

        assert mock_kb_documents.get_documents.call_count == 3
        args, context_1_kwargs = mock_kb_documents.get_documents.call_args_list[0]
        assert context_1_kwargs["context"] == "context1"
        args, context_2_kwargs = mock_kb_documents.get_documents.call_args_list[1]
        assert context_2_kwargs["context"] == "context2"
        args, base_kwargs = mock_kb_documents.get_documents.call_args_list[2]
        assert base_kwargs["context"] is None

        response_data = json.loads(response.content)
        assert isinstance(response_data, list)
        assert len(response_data) == 3
        assert response_data[0]["key"] == mock_doc_base.key
        assert response_data[0]["title"] == mock_doc_base.title
        assert response_data[1]["key"] == mock_doc_1.key
        assert response_data[1]["title"] == mock_doc_1.title
        assert response_data[2]["key"] == mock_doc_2.key
        assert response_data[2]["title"] == mock_doc_2.title

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_prompting(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = "some response from the model"
        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", None
        ApiBasics(
            self.app,
            chat_manager=mock_chat_manager,
            model_key="some_model_key",
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompt_list,
            image_service=MagicMock(),
            config_service=MagicMock(),
        )

        response = self.client.post(
            "/api/prompt",
            json={"promptid": "some-prompt-id", "userinput": "some user input"},
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"
        mock_prompt_list.render_prompt.assert_called_with(
            active_knowledge_context=ANY,
            prompt_choice="some-prompt-id",
            user_input="some user input",
            additional_vars={},
            warnings=ANY,
        )

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_prompting_guided(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_json_chat,
    ):
        mock_json_chat.run.return_value = "some response from the model"
        mock_chat_manager.json_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiBasics(
            self.app,
            chat_manager=mock_chat_manager,
            model_key="some_model_key",
            prompts_guided=mock_prompt_list,
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
        )

        # Make the request to the endpoint
        user_input = "some user input"
        response = self.client.post(
            "/api/prompt",
            json={
                "userinput": user_input,
                "context": "some context",
                "promptid": "guided-requirements",
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"
        mock_prompt_list.render_prompt.assert_called_with(
            active_knowledge_context="some context",
            prompt_choice="guided-requirements",
            user_input=user_input,
            additional_vars={},
            warnings=ANY,
        )

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_scenarios(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_json_chat,
    ):
        mock_json_chat.run.return_value = "some response from the model"
        mock_chat_manager.json_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiScenarios(self.app, mock_chat_manager, "some_model_key", mock_prompt_list)

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
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_scenarios_explore(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = "some response from the model"

        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiScenarios(self.app, mock_chat_manager, "some_model_key", mock_prompt_list)

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

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["options"].category == "scenarios-explore"
        assert kwargs["session_id"] is None

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_threat_modelling_explore(
        self, mock_prompt_list, mock_chat_manager, mock_streaming_chat
    ):
        mock_streaming_chat.run.return_value = "some response from the model"

        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiThreatModelling(
            self.app, mock_chat_manager, "some_model_key", mock_prompt_list
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

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["options"].category == "threat-modelling-explore"
        assert kwargs["session_id"] is None

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_requirements_explore(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = "some response from the model"

        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiRequirementsBreakdown(
            self.app, mock_chat_manager, "some_model_key", mock_prompt_list
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

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["options"].category == "requirements-breakdown-explore"
        assert kwargs["session_id"] == "some session id"

    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    @patch("llms.chats.StreamingChat")
    def test_post_story_validation_scenarios(
        self,
        mock_streaming_chat,
        mock_prompt_list,
        mock_chat_manager,
    ):
        mock_streaming_chat.run.return_value = "some response from the model"
        mock_chat_manager.streaming_chat.return_value = (
            "some_session_key",
            mock_streaming_chat,
        )

        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiStoryValidation(
            self.app, mock_chat_manager, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        response = self.client.post(
            "/api/story-validation/scenarios",
            json={
                "chat_session_id": None,
                "answers": [{"question": "some question 1", "answer": "answer1"}],
                "input": "some original requirement",
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"

        assert mock_streaming_chat.run.call_count == 1
        args, kwargs = mock_streaming_chat.run.call_args
        prompt_argument = args[0]
        assert "some question 1" in prompt_argument

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["session_id"] is None

    @patch("llms.chats.JSONChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_creative_matrix(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_json_chat,
    ):
        mock_json_chat.run.return_value = "some response from the model"
        mock_chat_manager.json_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiCreativeMatrix(
            self.app, mock_chat_manager, "some_model_key", mock_prompt_list
        )

        # Make the request to the endpoint
        rows = "For A, For B"
        columns = "For C, For D"
        prompt = "give me use cases for the future of gardening"
        idea_qualifiers = "utopian"
        num_ideas = "3"
        response = self.client.get(
            f"/api/creative-matrix?rows={rows}&columns={columns}&prompt={prompt}&idea_qualifiers={idea_qualifiers}&num_ideas={num_ideas}"
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"
        mock_prompt_list.render_prompt.assert_called_with(
            active_knowledge_context=ANY,
            prompt_choice="guided-creative-matrix",
            user_input=ANY,
            additional_vars={
                "rows": rows,
                "columns": columns,
                "prompt": prompt,
                "idea_qualifiers": idea_qualifiers,
                "num_ideas": num_ideas,
            },
            warnings=ANY,
        )
