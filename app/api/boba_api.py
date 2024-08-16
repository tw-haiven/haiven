# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from api.api_threat_modelling import ApiThreatModelling
from api.api_scenarios import ApiScenarios
from api.api_requirements import ApiRequirementsBreakdown
from api.api_story_validation import ApiStoryValidation
from llms.chats import (
    JSONChat,
    ServerChatSessionMemory,
    StreamingChat,
)
from content_manager import ContentManager
from llms.model import Model
from prompts.prompts_factory import PromptsFactory
from config_service import ConfigService
from llms.llm_config import LLMConfig

from pydantic import BaseModel


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

        ApiThreatModelling(
            app,
            self.chat_session_memory,
            ConfigService.get_default_guided_mode_model(),
            self.prompts_guided,
        )
        ApiRequirementsBreakdown(
            app,
            self.chat_session_memory,
            ConfigService.get_default_guided_mode_model(),
            self.prompts_guided,
        )
        ApiStoryValidation(
            app,
            self.chat_session_memory,
            ConfigService.get_default_guided_mode_model(),
            self.prompts_guided,
        )
        ApiScenarios(
            app,
            self.chat_session_memory,
            ConfigService.get_default_guided_mode_model(),
            self.prompts_guided,
        )

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
