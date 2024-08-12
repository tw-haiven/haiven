# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from api.models.explore_request import ExploreRequest
from tab_story_validation.api import enable_story_validation
from tab_requirements.api import enable_requirements
from tab_threat_modelling.api import enable_threat_modelling
from shared.llms.chats import (
    JSONChat,
    ServerChatSessionMemory,
    StreamingChat,
)
from shared.content_manager import ContentManager
from shared.llms.model import Model
from shared.prompts.prompts_factory import PromptsFactory
from shared.config_service import ConfigService
from shared.llms.llm_config import LLMConfig

from pydantic import BaseModel


def explore_scenario_prompt(original_input, item, user_message):
    return f"""
    You are a prospector, I am exploring the following context:
    {original_input}

    ...and the following scenario:
    {item}

    You are able to give me a concise elaboration of the scenario described in the
    context, here is my request for exploration:

    {user_message}

    Please respond in 3-5 sentences.
    """


class PromptRequestBody(BaseModel):
    promptid: str
    userinput: str
    chatSessionId: str = None
    context: str = None


class ExploreScenarioRequestBody(BaseModel):
    context: str
    input: str


class ScenarioQuestionRequestBody(BaseModel):
    context: str


class ScenarioQuestionResponse(BaseModel):
    questions: List[str]


class BobaApi:
    def __init__(
        self,
        prompts_factory: PromptsFactory,
        content_manager: ContentManager,
        chat_session_memory: ServerChatSessionMemory,
        model: str,
    ):
        self.content_manager = content_manager
        self.chat_session_memory = chat_session_memory
        self.model = model

        self.prompts_chat = prompts_factory.create_chat_prompt_list(
            self.content_manager.knowledge_base_markdown
        )
        prompts_factory_guided = PromptsFactory("./resources/prompts_guided")
        self.prompts_guided = prompts_factory_guided.create_guided_prompt_list(
            self.content_manager.knowledge_base_markdown
        )

        print(f"Model used for guided mode: {self.model}")

    def prompt(self, prompt_id, user_input, chat_session, context=None):
        rendered_prompt = self.prompts_chat.render_prompt(
            active_knowledge_context=context,
            prompt_choice=prompt_id,
            user_input=user_input,
            additional_vars={},
            warnings=[],
        )

        return self.chat(rendered_prompt, chat_session)

    def prompt_guided_json(self, prompt_id, variables):
        rendered_prompt = self.prompts_guided.render_prompt(
            active_knowledge_context=None,
            prompt_choice=prompt_id,
            user_input="",
            additional_vars=variables,
            warnings=[],
        )
        chat = JSONChat(llm_config=LLMConfig(self.model, 0.2))
        return chat.run(rendered_prompt)

    def chat(self, rendered_prompt, chat_session):
        for chunk in chat_session.start_with_prompt(rendered_prompt):
            yield chunk

    def add_endpoints(self, app: FastAPI):
        @app.get("/api/models")
        def get_models(request: Request):
            models: List[Model] = ConfigService.load_models("config.yaml")
            return JSONResponse(
                [{"id": model.id, "name": model.name} for model in models]
            )

        @app.get("/api/prompts")
        def get_prompts(request: Request):
            response_data = [entry.metadata for entry in self.prompts_chat.prompts]
            return JSONResponse(response_data)

        @app.get("/api/knowledge/snippets")
        def get_knowledge_snippets(request: Request):
            all_contexts = (
                self.content_manager.knowledge_base_markdown.get_all_contexts_keys()
            )

            response_data = []
            for context in all_contexts:
                snippets = self.content_manager.knowledge_base_markdown.get_knowledge_content_dict(
                    context
                )
                response_data.append({"context": context, "snippets": snippets})

            return JSONResponse(response_data)

        @app.get("/api/make-scenario")
        def make_scenario(request: Request):
            variables = {
                "input": request.query_params.get(
                    "input", "productization of consulting"
                ),
                "num_scenarios": request.query_params.get("num_scenarios", 5),
                "time_horizon": request.query_params.get("time_horizon", "5-year"),
                "optimism": request.query_params.get("optimism", "optimistic"),
                "realism": request.query_params.get("realism", "futuristic sci-fi"),
            }
            detailed = request.query_params.get("detail") == "true"

            return StreamingResponse(
                self.prompt_guided_json(
                    "guided-scenarios-detailed" if detailed else "guided-scenarios",
                    variables,
                ),
                media_type="text/event-stream",
                headers={"Connection": "keep-alive", "Content-Encoding": "none"},
            )

        enable_threat_modelling(app, self.chat_session_memory, self.chat)
        enable_requirements(app, self.chat_session_memory, self.chat)
        enable_story_validation(app, self.chat_session_memory)

        @app.post("/api/prompt")
        def chat(prompt_data: PromptRequestBody):
            chat_session_key_value, chat_session = (
                self.chat_session_memory.get_or_create_chat(
                    lambda: StreamingChat(
                        llm_config=LLMConfig(self.model, 0.5), stream_in_chunks=True
                    ),
                    prompt_data.chatSessionId,
                    "chat",
                    # TODO: Pass user identifier from session
                )
            )

            return StreamingResponse(
                self.prompt(
                    prompt_data.promptid,
                    prompt_data.userinput,
                    chat_session,
                    prompt_data.context,
                ),
                media_type="text/event-stream",
                headers={
                    "Connection": "keep-alive",
                    "Content-Encoding": "none",
                    "Access-Control-Expose-Headers": "X-Chat-ID",
                    "X-Chat-ID": chat_session_key_value,
                },
            )

        @app.post("/api/scenario/explore")
        def explore_scenario(explore_request: ExploreRequest):
            chat_session_key_value, chat_session = (
                self.chat_session_memory.get_or_create_chat(
                    lambda: StreamingChat(
                        llm_config=LLMConfig(self.model, 0.5), stream_in_chunks=True
                    ),
                    explore_request.chatSessionId,
                    "chat",
                    # TODO: Pass user identifier from session
                )
            )

            prompt = explore_request.userMessage
            if explore_request.chatSessionId is None:
                prompt = explore_scenario_prompt(
                    explore_request.originalInput,
                    explore_request.item,
                    explore_request.userMessage,
                )

            return StreamingResponse(
                self.chat(prompt, chat_session),
                media_type="text/event-stream",
                headers={
                    "Connection": "keep-alive",
                    "Content-Encoding": "none",
                    "Access-Control-Expose-Headers": "X-Chat-ID",
                    "X-Chat-ID": chat_session_key_value,
                },
            )

        @app.get("/api/creative-matrix")
        async def creative_matrix(request: Request):
            variables = {
                "rows": request.query_params.getlist("rows"),
                "columns": request.query_params.getlist("columns"),
                "prompt": request.query_params.get("prompt"),
                "idea_qualifiers": request.query_params.get("idea_qualifiers", None),
                "num_ideas": int(request.query_params.get("num_ideas", 3)),
            }

            return StreamingResponse(
                self.prompt_guided_json("guided-creative-matrix", variables),
                media_type="text/event-stream",
                headers={"Connection": "keep-alive", "Content-Encoding": "none"},
            )
