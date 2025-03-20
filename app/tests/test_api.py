# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import unittest
from unittest.mock import MagicMock, patch, ANY
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_basics import ApiBasics
from api.api_multi_step import ApiMultiStep
from api.api_scenarios import ApiScenarios
from api.api_creative_matrix import ApiCreativeMatrix
from prompts.prompts_factory import PromptsFactory
from tests.utils import get_test_data_path
from starlette.middleware.sessions import SessionMiddleware


class TestApi(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.add_middleware(SessionMiddleware, secret_key="some-random-string")
        self.client = TestClient(self.app)

    def tearDown(self):
        # Clean up code to run after each test
        pass

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
    def test_prompting_text(
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
            },
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
            user_context="some user defined context",
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
                "context": "some context",
                "promptid": "guided-requirements",
                "userContext": "some user defined context",
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
            user_context="some user defined context",
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
    def test_explore_with_static_framing(
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
        assert streamed_content == "some response from the model"

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
        mock_streaming_chat.run.return_value = "some response from the model"

        mock_chat_manager.streaming_chat.return_value = (
            "some_key",
            mock_streaming_chat,
        )
        mock_prompt_list.render_prompt.return_value = "some prompt", "template"
        some_context = "some context for example a domain description"
        mock_prompt_list.get_rendered_context.return_value = some_context

        ApiMultiStep(self.app, mock_chat_manager, "some_model_key", mock_prompt_list)

        body_dict = {
            "userinput": "some user question",
            "context": "some context",
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
        assert streamed_content == "some response from the model"

        args, kwargs = mock_streaming_chat.run.call_args
        actual_composed_prompt = args[0]
        assert body_dict["userinput"] in actual_composed_prompt
        assert some_context in actual_composed_prompt
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
        mock_streaming_chat.run.return_value = "some response from the model"
        mock_chat_manager.streaming_chat.return_value = (
            "some_session_key",
            mock_streaming_chat,
        )

        guided_prompts_path = (
            get_test_data_path() + "/test_knowledge_pack/prompts/guided"
        )
        prompts_factory_guided = PromptsFactory(guided_prompts_path)
        prompts_guided = prompts_factory_guided.create_guided_prompt_list(
            MagicMock()  # knowledge_base_markdown
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
                "context": "some-context",
                # additional data for the follow-up
                "scenarios": [{"title": "some title", "content": "some content"}],
                "previous_promptid": "first-step-prompt-1234",
            },
        )

        # Assert the response
        assert response.status_code == 200
        streamed_content = response.content.decode("utf-8")
        assert streamed_content == "some response from the model"

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
