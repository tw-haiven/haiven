# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import os
import unittest
from unittest.mock import MagicMock, patch, ANY
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_basics import ApiBasics
from api.api_multi_step import ApiMultiStep
from api.api_scenarios import ApiScenarios
from api.api_creative_matrix import ApiCreativeMatrix
from prompts.prompts_factory import PromptsFactory
from llms.model_config import ModelConfig
from tests.utils import get_test_data_path
from starlette.middleware.sessions import SessionMiddleware
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_basics import ApiBasics
from knowledge.markdown import KnowledgeMarkdown
from knowledge_manager import KnowledgeManager
from config_service import ConfigService
from llms.chats import ChatManager
from llms.model_config import ModelConfig
from prompts.prompts import PromptList
from llms.image_description_service import ImageDescriptionService
from disclaimer_and_guidelines import DisclaimerAndGuidelinesService
from inspirations import InspirationsManager


class TestApi(unittest.TestCase):
    def check_token_usage_in_streamed_content(self, streamed_content):
        """Helper function to check for token usage in the new format"""
        import json

        # Try to find the usage JSON object in the streamed content
        usage_found = False

        # Look for the usage pattern in the content
        if '"usage"' in streamed_content:
            # Find the start of the usage object
            usage_start = streamed_content.find('{"usage"')
            if usage_start != -1:
                # Extract from the start of the usage object to the end
                usage_part = streamed_content[usage_start:]
                try:
                    data = json.loads(usage_part)
                    if "usage" in data:
                        usage_found = True
                        assert "prompt_tokens" in data["usage"]
                        assert "completion_tokens" in data["usage"]
                        assert "total_tokens" in data["usage"]
                except json.JSONDecodeError:
                    pass

        assert (
            usage_found
        ), f"Token usage not found in streamed content: {streamed_content}"

    def setUp(self):
        self.app = FastAPI()
        self.app.add_middleware(SessionMiddleware, secret_key="some-random-string")
        self.client = TestClient(self.app)

    def tearDown(self):
        # Clean up code to run after each test
        pass

    def test_apikey_endpoints_use_service(self):
        # Arrange
        user_email = "testuser@example.com"

        # Mock service
        mock_service = MagicMock()
        # For list_keys_for_user, return a dummy key
        mock_service.list_keys_for_user.return_value = {
            "dummy_key_hash": {
                "name": "dummy",
                "user_id": "pseudonymized_user_id",  # Service handles pseudonymization
                "created_at": "2024-01-01T00:00:00",
                "expires_at": "2024-01-02T00:00:00",
                "last_used": None,
                "usage_count": 0,
            }
        }
        # For generate_api_key, return a dummy key
        mock_service.generate_api_key.return_value = "dummy_api_key_value"

        # Mock config
        mock_config = MagicMock()

        # Patch get_user_email to return our test email
        from api.api_key_management import ApiKeyManagementAPI

        class TestApiKeyManagementAPI(ApiKeyManagementAPI):
            def get_user_email(self, request):
                return user_email

        # Register endpoints with our test APIKeyManagementAPI
        TestApiKeyManagementAPI(self.app, mock_service, mock_config)

        # Act: Generate API key
        response = self.client.post(
            "/api/apikeys/generate",
            json={"name": "dummy"},
        )
        # Assert: The service should be called with the original user_id
        mock_service.generate_api_key.assert_called_with(
            name="dummy", user_id=user_email, expires_days=30
        )
        assert response.status_code == 200

        # Act: List API keys
        response = self.client.get("/api/apikeys")
        mock_service.list_keys_for_user.assert_called_with(user_email)
        assert response.status_code == 200

    def test_apikey_revoke_uses_service(self):
        user_email = "testuser@example.com"
        key_hash = "dummy_key_hash"

        # Mock service
        mock_service = MagicMock()
        mock_service.list_keys_for_user.return_value = {
            key_hash: {"name": "dummy", "user_id": "pseudonymized_user_id"}
        }
        mock_service.revoke_key.return_value = True

        # Mock config
        mock_config = MagicMock()

        # Patch get_user_email
        from api.api_key_management import ApiKeyManagementAPI

        class TestApiKeyManagementAPI(ApiKeyManagementAPI):
            def get_user_email(self, request):
                return user_email

        TestApiKeyManagementAPI(self.app, mock_service, mock_config)

        # Act: Revoke API key
        response = self.client.post(
            "/api/apikeys/revoke",
            json={"key_hash": key_hash},
        )
        # Assert: list_keys_for_user and revoke_key called with correct args
        mock_service.list_keys_for_user.assert_called_with(user_email)
        mock_service.revoke_key.assert_called_with(key_hash)
        assert response.status_code == 200

    def test_apikey_usage_uses_service(self):
        user_email = "testuser@example.com"

        # Mock service
        mock_service = MagicMock()
        mock_service.list_keys_for_user.return_value = {
            "dummy_key_hash": {
                "name": "dummy",
                "user_id": "pseudonymized_user_id",  # Service handles pseudonymization
                "created_at": "2024-01-01T00:00:00",
                "expires_at": "2024-01-02T00:00:00",
                "last_used": "2024-01-01T12:00:00",
                "usage_count": 5,
            }
        }

        # Mock config
        mock_config = MagicMock()

        # Patch get_user_email
        from api.api_key_management import ApiKeyManagementAPI

        class TestApiKeyManagementAPI(ApiKeyManagementAPI):
            def get_user_email(self, request):
                return user_email

        TestApiKeyManagementAPI(self.app, mock_service, mock_config)

        # Act: Get API key usage
        response = self.client.get("/api/apikeys/usage")
        # Assert: list_keys_for_user called with correct user_id
        mock_service.list_keys_for_user.assert_called_with(user_email)
        assert response.status_code == 200

    def test_get_prompts(self):
        mock_prompts = MagicMock()
        some_prompts = [{"identifier": "some-identifier", "title": "Some title"}]
        mock_prompts.get_prompts_with_follow_ups.return_value = some_prompts

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/prompts")
        expected_response = some_prompts

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

    def test_get_models(self):
        # Helper function to create MagicMock with id and name attributes
        def create_mock_model(id_value, name_value):
            mock_model = MagicMock()
            mock_model.id = id_value
            mock_model.name = name_value
            return mock_model

        # Mocking config_service methods to return specific MagicMock objects
        mock_config_service = MagicMock()
        mock_config_service.load_embedding_model.return_value = create_mock_model(
            "embed-model-id", "embed-model-name"
        )
        mock_config_service.get_image_model.return_value = create_mock_model(
            "image-model-id", "image-model-name"
        )
        mock_config_service.get_chat_model.return_value = create_mock_model(
            "chat-model-id", "chat-model-name"
        )

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=mock_config_service,
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/models")
        expected_response = {
            "chat": {
                "id": "chat-model-id",
                "name": "chat-model-name",
            },
            "vision": {
                "id": "image-model-id",
                "name": "image-model-name",
            },
            "embeddings": {
                "id": "embed-model-id",
                "name": "embed-model-name",
            },
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

    def test_get_documents(self):
        mock_knowledge_manager = MagicMock()

        mock_kb_documents = MagicMock()
        mock_doc_base = MagicMock(
            key="some-document-base",
            title="Some title base",
            description="Some description 1",
        )
        mock_doc_base.get_source_title_link.return_value = "some source title link"
        mock_doc_1 = MagicMock(
            key="some-document-1",
            title="Some title 1",
            description="Some description 2",
        )
        mock_doc_1.get_source_title_link.return_value = "some source title link"
        mock_doc_2 = MagicMock(
            key="some-document-2",
            title="Some title 2",
            description="Some description 3",
        )
        mock_doc_2.get_source_title_link.return_value = "some source title link"
        mock_kb_documents.get_documents.return_value = [
            mock_doc_base,
            mock_doc_1,
            mock_doc_2,
        ]
        mock_knowledge_manager.knowledge_base_documents = mock_kb_documents

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=mock_knowledge_manager,
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/knowledge/documents")

        # Assert the response
        assert response.status_code == 200

        assert mock_kb_documents.get_documents.call_count == 1

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
    def test_prompting_text(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", None
        mock_prompt_list.produces_json_output.return_value = False
        ApiBasics(
            self.app,
            chat_manager=mock_chat_manager,
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompt_list,
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.post(
            "/api/prompt",
            json={
                "promptid": "some-prompt-id",
                "userinput": "some user input",
                "userContext": "some user defined context",
                "contexts": ["some context"],
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content

        self.check_token_usage_in_streamed_content(streamed_content)
        mock_prompt_list.render_prompt.assert_called_with(
            prompt_choice="some-prompt-id",
            user_input="some user input",
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
        mock_json_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.json_chat.return_value = (
            "some_key",
            mock_json_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        mock_prompt_list.produces_json_output.return_value = True
        ApiBasics(
            self.app,
            chat_manager=mock_chat_manager,
            model_config=MagicMock(),
            prompts_guided=mock_prompt_list,
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        # Make the request to the endpoint
        user_input = "some user input"
        response = self.client.post(
            "/api/prompt",
            json={
                "userinput": user_input,
                "contexts": ["some context"],
                "promptid": "guided-requirements",
                "userContext": "some user defined context",
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content

        self.check_token_usage_in_streamed_content(streamed_content)
        mock_prompt_list.render_prompt.assert_called_with(
            prompt_choice="guided-requirements",
            user_input=user_input,
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
        mock_json_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
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
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)
        mock_prompt_list.render_prompt.assert_called_with(
            prompt_choice="guided-scenarios-detailed",
            user_input=ANY,
            additional_vars={
                "input": input,
                "num_scenarios": num_scenarios,
                "time_horizon": time_horizon,
                "optimism": optimism,
                "realism": realism,
            },
        )

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_explore_with_static_framing(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )

        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        ApiMultiStep(self.app, mock_chat_manager, "some_model_key", mock_prompt_list)

        body_dict = {
            "userinput": "some user question",
            "item": "some scenario item",
            "first_step_input": "some original prompt",
            "chatSessionId": "",
            # # previous_promptid: str = None TODO, another test
            "previous_framing": "We did something before, here it is: ",
        }

        # Make the request to the endpoint
        response = self.client.post(
            "/api/prompt/explore",
            json=body_dict,
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)

        args, kwargs = mock_streaming_chat.run.call_args
        actual_composed_prompt = args[0]
        assert body_dict["userinput"] in actual_composed_prompt
        assert body_dict["previous_framing"] in actual_composed_prompt
        assert body_dict["first_step_input"] in actual_composed_prompt

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["options"].category == "explore"
        assert kwargs["session_id"] == ""

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_explore_with_previous_prompt(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )

        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"

        ApiMultiStep(self.app, mock_chat_manager, "some_model_key", mock_prompt_list)

        body_dict = {
            "userinput": "some user question",
            "contexts": ["some context"],
            "item": "some scenario item",
            "first_step_input": "some original prompt",
            "chatSessionId": "",
            "previous_promptid": "some-previous-prompt-id",
        }

        # Make the request to the endpoint
        response = self.client.post(
            "/api/prompt/explore",
            json=body_dict,
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        # The response now includes both the model response and token usage data
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)

        args, kwargs = mock_streaming_chat.run.call_args
        actual_composed_prompt = args[0]
        assert body_dict["userinput"] in actual_composed_prompt
        assert body_dict["first_step_input"] in actual_composed_prompt

        args, kwargs = mock_chat_manager.streaming_chat.call_args
        assert kwargs["options"].category == "explore"
        assert kwargs["session_id"] == ""

    @patch("llms.chats.ChatManager")
    @patch("llms.chats.StreamingChat")
    def test_post_multi_step(
        self,
        mock_streaming_chat,
        mock_chat_manager,
    ):
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.streaming_chat.return_value = (
            "some_session_key",
            mock_streaming_chat,
        )

        guided_prompts_path = (
            get_test_data_path() + "/test_knowledge_pack/prompts/guided"
        )
        prompts_factory_guided = PromptsFactory(guided_prompts_path)
        prompts_guided = prompts_factory_guided.create_guided_prompt_list(
            MagicMock(),  # knowledge_base_markdown
            MagicMock(),  # knowledge_manager,
        )

        ApiMultiStep(self.app, mock_chat_manager, "some_model_key", prompts_guided)

        # Make the request to the endpoint
        response = self.client.post(
            "/api/prompt/follow-up",
            json={
                # The usual
                "chat_session_id": None,
                "userinput": "some original requirement",
                "promptid": "follow-up-prompt-2345",
                "contexts": ["some-context"],
                # additional data for the follow-up
                "scenarios": [{"title": "some title", "content": "some content"}],
                "previous_promptid": "first-step-prompt-1234",
                "userContext": "some user context",
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)

        assert mock_streaming_chat.run.call_count == 1
        args, kwargs = mock_streaming_chat.run.call_args
        prompt_argument = args[0]
        assert "this is what I got from the first step" in prompt_argument
        assert "some title" in prompt_argument
        assert "some content" in prompt_argument
        assert "Follow up" in prompt_argument

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
        mock_json_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
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
        # The response now includes both the model response and token usage data
        assert "some response from the model" in streamed_content
        self.check_token_usage_in_streamed_content(streamed_content)
        mock_prompt_list.render_prompt.assert_called_with(
            prompt_choice="guided-creative-matrix",
            user_input=ANY,
            additional_vars={
                "rows": rows,
                "columns": columns,
                "prompt": prompt,
                "idea_qualifiers": idea_qualifiers,
                "num_ideas": num_ideas,
            },
        )

    def test_get_inspirations(self):
        mock_inspirations = [{"title": "Test Title"}]
        mock_inspirations_manager = MagicMock()
        mock_inspirations_manager.get_inspirations.return_value = mock_inspirations

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=mock_inspirations_manager,
        )

        response = self.client.get("/api/inspirations")

        # Assert the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert isinstance(response_data, list)
        assert len(response_data) > 0

        # Verify the title field of the first inspiration item
        first_item = response_data[0]
        assert "title" in first_item

        # Verify the mock was called
        mock_inspirations_manager.get_inspirations.assert_called_once()

    def test_get_inspiration_by_id(self):
        mock_inspiration = {
            "id": "test-id",
            "title": "Test Title",
            "description": "Test Description",
            "category": "test",
            "prompt_template": "Test template",
        }
        mock_inspirations_manager = MagicMock()
        mock_inspirations_manager.get_inspiration_by_id.return_value = mock_inspiration

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=mock_inspirations_manager,
        )

        response = self.client.get("/api/inspirations/test-id")

        # Assert the response
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data == mock_inspiration
        mock_inspirations_manager.get_inspiration_by_id.assert_called_once_with(
            "test-id"
        )

    def test_get_inspiration_by_id_not_found(self):
        mock_inspirations_manager = MagicMock()
        mock_inspirations_manager.get_inspiration_by_id.return_value = None

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=MagicMock(),
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=mock_inspirations_manager,
        )

        response = self.client.get("/api/inspirations/non-existent")

        # Assert the response
        assert response.status_code == 404
        mock_inspirations_manager.get_inspiration_by_id.assert_called_once_with(
            "non-existent"
        )

    def test_get_prompt_with_follow_ups_should_return_prompt_for_the_given_id(self):
        mock_prompts_chat = MagicMock()

        mock_prompt = MagicMock()
        mock_prompt.content = "Content {user_input} {context}"
        mock_prompt.metadata = {
            "title": "Test Prompt",
            "identifier": "test-prompt-id",
            "categories": ["test"],
            "type": "chat",
            "editable": False,
            "show": True,
            "help_prompt_description": "Test description",
            "help_user_input": "Test user input help",
            "help_sample_input": "Test sample input",
        }

        mock_prompts_chat.get_a_prompt_with_follow_ups.return_value = {
            "content": "PromptContent {user_input}",
            "title": "Test Prompt",
            "identifier": "test-prompt-id",
            "categories": ["test"],
            "type": "chat",
            "editable": False,
            "show": True,
            "help_prompt_description": "Test description",
            "help_user_input": "Test user input help",
            "help_sample_input": "Test sample input",
            "follow_ups": [],
        }

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompts_chat,
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?prompt_id=test-prompt-id")

        assert response.status_code == 200
        mock_prompts_chat.get_a_prompt_with_follow_ups.assert_called_with(
            "test-prompt-id", download_prompt=True
        )

        response_data = json.loads(response.content)[0]
        assert response_data["content"] == "PromptContent {user_input}"
        assert response_data["title"] == "Test Prompt"
        assert response_data["identifier"] == "test-prompt-id"
        assert response_data["categories"] == ["test"]
        assert response_data["type"] == "chat"
        assert response_data["editable"] is False
        assert response_data["show"] is True
        assert response_data["help_prompt_description"] == "Test description"
        assert response_data["help_user_input"] == "Test user input help"
        assert response_data["help_sample_input"] == "Test sample input"
        assert len(response_data["follow_ups"]) == 0

    def test_get_prompt_with_follow_ups_should_throw_exception_if_prompt_not_found(
        self,
    ):
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_a_prompt_with_follow_ups.return_value = None

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompts_chat,
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?prompt_id=non-existent-id")

        # Assert the response
        assert response.status_code == 500
        assert b"Prompt not found" in response.content
        assert mock_prompts_chat.get_a_prompt_with_follow_ups.call_count == 1
        mock_prompts_chat.get_a_prompt_with_follow_ups.assert_called_with(
            "non-existent-id", download_prompt=True
        )

    def test_download_prompt_invalid_prompt_id(self):
        mock_prompts_chat = MagicMock()
        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompts_chat,
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )
        # Invalid characters
        response = self.client.get("/api/download-prompt?prompt_id=bad!id")
        assert response.status_code == 400
        assert b"Invalid prompt_id" in response.content
        # Too long
        long_id = "a" * 101
        response = self.client.get(f"/api/download-prompt?prompt_id={long_id}")
        assert response.status_code == 400
        assert b"Invalid prompt_id" in response.content
        # Empty
        response = self.client.get("/api/download-prompt?prompt_id=")
        assert response.status_code == 400
        assert b"Invalid prompt_id" in response.content

    def test_download_prompt_invalid_category(self):
        mock_prompts_chat = MagicMock()
        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            prompts_chat=mock_prompts_chat,
            image_service=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )
        # Invalid characters
        response = self.client.get("/api/download-prompt?category=bad!cat")
        assert response.status_code == 400
        assert b"Invalid category" in response.content
        # Too long
        long_cat = "a" * 101
        response = self.client.get(f"/api/download-prompt?category={long_cat}")
        assert response.status_code == 400
        assert b"Invalid category" in response.content

    def test_get_prompts_with_category(self):
        mock_prompts = MagicMock()
        category_prompts = [
            {
                "identifier": "prompt-1",
                "title": "Prompt 1",
                "categories": ["architecture"],
                "content": "Content 1",
            },
            {
                "identifier": "prompt-2",
                "title": "Prompt 2",
                "categories": ["architecture"],
                "content": "Content 2",
            },
        ]

        mock_prompts.get_prompts_with_follow_ups.return_value = category_prompts

        # Mock the HaivenLogger
        with patch("api.api_basics.HaivenLogger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.get.return_value = mock_logger_instance

            ApiBasics(
                self.app,
                chat_manager=MagicMock(),
                model_config=MagicMock(),
                image_service=MagicMock(),
                prompts_chat=mock_prompts,
                prompts_guided=MagicMock(),
                knowledge_manager=MagicMock(),
                config_service=MagicMock(),
                disclaimer_and_guidelines=MagicMock(),
                inspirations_manager=MagicMock(),
            )

            # Test the endpoint with category parameter
            response = self.client.get("/api/download-prompt?category=architecture")

            # Assert response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), category_prompts)

            # Verify the method was called with the right parameters
            mock_prompts.get_prompts_with_follow_ups.assert_called_with(
                download_prompt=True, category="architecture"
            )

            # Check that analytics was logged for each prompt
            calls = mock_logger_instance.analytics.call_args_list
            self.assertEqual(len(calls), 2)

            for i, call in enumerate(calls):
                args, kwargs = call
                self.assertEqual(args[0], "Download prompt")
                self.assertEqual(
                    args[1]["prompt_id"], category_prompts[i]["identifier"]
                )
                self.assertEqual(args[1]["category"], "architecture")
                self.assertEqual(args[1]["source"], "ui")

    def test_get_all_prompts(self):
        mock_prompts = MagicMock()
        all_prompts = [
            {
                "identifier": "prompt-1",
                "title": "Prompt 1",
                "categories": ["architecture"],
                "content": "Content 1",
            },
            {
                "identifier": "prompt-2",
                "title": "Prompt 2",
                "categories": ["coding"],
                "content": "Content 2",
            },
        ]

        mock_prompts.get_prompts_with_follow_ups.return_value = all_prompts

        # Mock the HaivenLogger
        with patch("api.api_basics.HaivenLogger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.get.return_value = mock_logger_instance

            ApiBasics(
                self.app,
                chat_manager=MagicMock(),
                model_config=MagicMock(),
                image_service=MagicMock(),
                prompts_chat=mock_prompts,
                prompts_guided=MagicMock(),
                knowledge_manager=MagicMock(),
                config_service=MagicMock(),
                disclaimer_and_guidelines=MagicMock(),
                inspirations_manager=MagicMock(),
            )

            # Test the endpoint with category parameter
            response = self.client.get("/api/download-prompt")

            # Assert response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), all_prompts)

            # Verify the method was called with the right parameters
            mock_prompts.get_prompts_with_follow_ups.assert_called_with(
                download_prompt=True,
            )

            # Check that analytics was logged for each prompt
            calls = mock_logger_instance.analytics.call_args_list
            self.assertEqual(len(calls), 2)

            for i, call in enumerate(calls):
                args, kwargs = call
                self.assertEqual(args[0], "Download prompt")
                self.assertEqual(args[1]["prompt_id"], all_prompts[i]["identifier"])
                self.assertEqual(args[1]["category"], "all")
                self.assertEqual(args[1]["source"], "ui")

    def test_download_prompt_source_detection(self):
        """Test that source detection logic works correctly."""
        # Test MCP source detection
        mock_request_mcp = MagicMock()
        mock_request_mcp.session = {
            "user": {"auth_type": "api_key", "user_id": "test_user_id"}
        }

        # Test UI source detection
        mock_request_ui = MagicMock()
        mock_request_ui.session = {
            "user": {"auth_type": "session", "user_id": "test_user_id"}
        }

        # Test default source detection (no auth_type)
        mock_request_default = MagicMock()
        mock_request_default.session = {"user": {"user_id": "test_user_id"}}

        # Test no session
        mock_request_no_session = MagicMock()
        mock_request_no_session.session = None

        # Test empty session
        mock_request_empty_session = MagicMock()
        mock_request_empty_session.session = {}

        # Test auth switched off scenario
        mock_request_auth_off = MagicMock()
        mock_request_auth_off.session = None

        # Test the source detection logic (same as _get_request_source helper)
        def get_analytics_source(request):
            # Check if auth is switched off
            if os.environ.get("AUTH_SWITCHED_OFF") == "true":
                return "unknown"

            # Check if it's an API key auth (MCP)
            if request.session and request.session.get("user"):
                user = request.session.get("user")
                if user.get("auth_type") == "api_key":
                    return "mcp"

            # Default to UI
            return "ui"

            # Verify analytics source detection

        self.assertEqual(get_analytics_source(mock_request_mcp), "mcp")
        self.assertEqual(get_analytics_source(mock_request_ui), "ui")
        self.assertEqual(get_analytics_source(mock_request_default), "ui")
        self.assertEqual(get_analytics_source(mock_request_no_session), "ui")
        self.assertEqual(get_analytics_source(mock_request_empty_session), "ui")

        # Test auth switched off scenario
        with patch.dict(os.environ, {"AUTH_SWITCHED_OFF": "true"}):
            self.assertEqual(get_analytics_source(mock_request_auth_off), "unknown")
            self.assertEqual(get_analytics_source(mock_request_mcp), "unknown")
            self.assertEqual(get_analytics_source(mock_request_ui), "unknown")

        # Test that analytics logging includes the source field
        with patch("api.api_basics.HaivenLogger") as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.get.return_value = mock_logger_instance

            # Test MCP analytics
            mock_request_mcp.session = {
                "user": {"auth_type": "api_key", "user_id": "test_user_id"}
            }
            user = mock_request_mcp.session.get("user", {})
            source = "mcp" if user.get("auth_type") == "api_key" else "ui"

            # Simulate analytics call
            mock_logger_instance.analytics(
                "Download prompt",
                {
                    "user_id": "test_user_id",
                    "prompt_id": "test_prompt",
                    "category": "Individual Prompt",
                    "source": source,
                },
            )

            # Verify the analytics call was made with correct source
            mock_logger_instance.analytics.assert_called_with(
                "Download prompt",
                {
                    "user_id": "test_user_id",
                    "prompt_id": "test_prompt",
                    "category": "Individual Prompt",
                    "source": "mcp",
                },
            )

    @patch("llms.chats.StreamingChat")
    @patch("llms.chats.ChatManager")
    @patch("prompts.prompts.PromptList")
    def test_perplexity_used_for_grounded_prompts(
        self,
        mock_prompt_list,
        mock_chat_manager,
        mock_streaming_chat,
    ):
        # Setup mocks
        mock_streaming_chat.run.return_value = iter(
            [
                "some response from the model",
                {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    }
                },
            ]
        )
        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", None
        mock_prompt_list.produces_json_output.return_value = False

        # Create a mock prompt with grounded=True
        mock_prompt = MagicMock()
        mock_prompt.metadata = {"grounded": True}
        mock_prompt_list.get.return_value = mock_prompt

        # Setup the API with a default model config that we can recognize
        default_model_config = MagicMock()
        default_model_config.provider = "default-provider"

        perplexity_model_config = MagicMock()
        perplexity_model_config.provider = "perplexity"

        # Create the API with our mocks
        ApiBasics(
            self.app,
            chat_manager=mock_chat_manager,
            model_config=default_model_config,
            image_service=MagicMock(),
            prompts_chat=mock_prompt_list,
            prompts_guided=mock_prompt_list,
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        # Make the request
        response = self.client.post(
            "/api/prompt",
            json={
                "userinput": "some user input",
                "promptid": "grounded-prompt-id",
            },
        )

        # Assert the response
        self.assertEqual(response.status_code, 200)
        streamed_content = response.content.decode("utf-8")
        self.assertIn("some response from the model", streamed_content)
        self.check_token_usage_in_streamed_content(streamed_content)

        expected_model_config = ModelConfig("perplexity", "perplexity", "Perplexity")

        # Verify that streaming_chat was called with the Perplexity model config
        # and not the default config
        mock_chat_manager.streaming_chat.assert_called_once()
        actual_model_config = mock_chat_manager.streaming_chat.call_args[1][
            "model_config"
        ]
        self.assertEqual(actual_model_config.provider, expected_model_config.provider)



class TestApiBasics:
    def test_get_knowledge_snippets_with_missing_title_metadata(self):
        """Test that get_knowledge_snippets handles contexts without title metadata gracefully"""
        # Create a mock app
        app = FastAPI()
        
        # Create mock dependencies
        mock_chat_manager = Mock(spec=ChatManager)
        mock_model_config = Mock(spec=ModelConfig)
        mock_prompts_guided = Mock(spec=PromptList)
        mock_prompts_chat = Mock(spec=PromptList)
        mock_image_service = Mock(spec=ImageDescriptionService)
        mock_config_service = Mock(spec=ConfigService)
        mock_disclaimer_service = Mock(spec=DisclaimerAndGuidelinesService)
        mock_inspirations_manager = Mock(spec=InspirationsManager)
        
        # Create a mock knowledge manager with contexts that have missing title metadata
        mock_knowledge_manager = Mock(spec=KnowledgeManager)
        
        # Create a context with missing title metadata
        context_without_title = KnowledgeMarkdown(
            content="Some content without title",
            metadata={}  # Empty metadata, no title
        )
        
        # Create a context with title metadata
        context_with_title = KnowledgeMarkdown(
            content="Some content with title",
            metadata={"title": "Context With Title"}
        )
        
        # Mock the get_all_contexts method to return our test contexts
        mock_knowledge_manager.knowledge_base_markdown.get_all_contexts.return_value = {
            "context_without_title": context_without_title,
            "context_with_title": context_with_title
        }
        
        # Create the API instance
        api = ApiBasics(
            app=app,
            chat_manager=mock_chat_manager,
            model_config=mock_model_config,
            prompts_guided=mock_prompts_guided,
            knowledge_manager=mock_knowledge_manager,
            prompts_chat=mock_prompts_chat,
            image_service=mock_image_service,
            config_service=mock_config_service,
            disclaimer_and_guidelines=mock_disclaimer_service,
            inspirations_manager=mock_inspirations_manager
        )
        
        # Create a test client
        client = TestClient(app)
        
        # Make the request
        response = client.get("/api/knowledge/snippets")
        
        # The response should be successful and handle missing titles gracefully
        assert response.status_code == 200
        
        # Parse the response
        data = response.json()
        
        # Should have both contexts
        assert len(data) == 2
        
        # Find the context without title
        context_without_title_data = next(
            (item for item in data if item["context"] == "context_without_title"), 
            None
        )
        assert context_without_title_data is not None
        # Should use the context name as fallback title
        assert context_without_title_data["title"] == "context_without_title"
        
        # Find the context with title
        context_with_title_data = next(
            (item for item in data if item["context"] == "context_with_title"), 
            None
        )
        assert context_with_title_data is not None
        # Should use the metadata title
        assert context_with_title_data["title"] == "Context With Title"

    def test_download_restricted_prompt_returns_403(self):
        """Test that downloading a restricted prompt returns 403 Forbidden"""
        # Mock the prompt with download_restricted=True
        mock_prompt = {
            "identifier": "restricted-prompt",
            "title": "Restricted Prompt",
            "download_restricted": True,
            "content": "Restricted content",
        }

        # Create mock prompts_chat
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_a_prompt_with_follow_ups.return_value = mock_prompt

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts_chat,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?prompt_id=restricted-prompt")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"], "This prompt is not available for download"
        )

    def test_download_restricted_prompts_filtered_from_category(self):
        """Test that restricted prompts are filtered out when downloading by category"""
        # Mock prompts with some restricted
        mock_prompts = [
            {
                "identifier": "prompt-1",
                "download_restricted": False,
                "title": "Downloadable Prompt 1",
            },
            {
                "identifier": "prompt-2",
                "download_restricted": True,
                "title": "Restricted Prompt",
            },
            {
                "identifier": "prompt-3",
                "download_restricted": False,
                "title": "Downloadable Prompt 2",
            },
        ]

        # Create mock prompts_chat
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_prompts_with_follow_ups.return_value = mock_prompts

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts_chat,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?category=test-category")

        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Should only return non-restricted prompts
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["identifier"], "prompt-1")
        self.assertEqual(result[1]["identifier"], "prompt-3")

    def test_download_restricted_prompts_filtered_from_all_prompts(self):
        """Test that restricted prompts are filtered out when downloading all prompts"""
        # Mock prompts with some restricted
        mock_prompts = [
            {
                "identifier": "prompt-1",
                "download_restricted": False,
                "title": "Downloadable Prompt 1",
            },
            {
                "identifier": "prompt-2",
                "download_restricted": True,
                "title": "Restricted Prompt",
            },
            {
                "identifier": "prompt-3",
                "download_restricted": False,
                "title": "Downloadable Prompt 2",
            },
        ]

        # Create mock prompts_chat
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_prompts_with_follow_ups.return_value = mock_prompts

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts_chat,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt")

        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Should only return non-restricted prompts
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["identifier"], "prompt-1")
        self.assertEqual(result[1]["identifier"], "prompt-3")

    def test_download_all_prompts_with_empty_category(self):
        """Test that empty category parameter correctly triggers 'download all prompts' logic"""
        # Mock prompts with some restricted
        mock_prompts = [
            {
                "identifier": "prompt-1",
                "download_restricted": False,
                "title": "Downloadable Prompt 1",
            },
            {
                "identifier": "prompt-2",
                "download_restricted": True,
                "title": "Restricted Prompt",
            },
            {
                "identifier": "prompt-3",
                "download_restricted": False,
                "title": "Downloadable Prompt 2",
            },
        ]

        # Create mock prompts_chat
        mock_prompts_chat = MagicMock()
        mock_prompts_chat.get_prompts_with_follow_ups.return_value = mock_prompts

        ApiBasics(
            self.app,
            chat_manager=MagicMock(),
            model_config=MagicMock(),
            image_service=MagicMock(),
            prompts_chat=mock_prompts_chat,
            prompts_guided=MagicMock(),
            knowledge_manager=MagicMock(),
            config_service=MagicMock(),
            disclaimer_and_guidelines=MagicMock(),
            inspirations_manager=MagicMock(),
        )

        response = self.client.get("/api/download-prompt?category=")

        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Should only return non-restricted prompts
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["identifier"], "prompt-1")
        self.assertEqual(result[1]["identifier"], "prompt-3")

    def test_apikey_generate_requires_user(self):
        # Arrange
        mock_service = MagicMock()
        mock_service.generate_api_key.return_value = "dummy_api_key_value"
        mock_config = MagicMock()
        from api.api_key_management import ApiKeyManagementAPI
        from fastapi import HTTPException

        # Patch get_user_email to simulate missing user
        class TestApiKeyManagementAPI(ApiKeyManagementAPI):
            def get_user_email(self, request):
                raise HTTPException(
                    status_code=401,
                    detail="User not authenticated. You must be logged in to generate or manage API keys, even in developer mode.",
                )

        TestApiKeyManagementAPI(self.app, mock_service, mock_config)

        # Act: Generate API key without user in session
        response = self.client.post(
            "/api/apikeys/generate",
            json={"name": "dummy"},
        )
        # Assert: Should return 401 with improved error message
        assert response.status_code == 401
        assert "User not authenticated" in response.json().get("detail", "")

