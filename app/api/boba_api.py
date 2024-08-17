# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from api.api_threat_modelling import ApiThreatModelling
from api.api_scenarios import ApiScenarios
from api.api_requirements import ApiRequirementsBreakdown
from api.api_story_validation import ApiStoryValidation
from api.api_creative_matrix import ApiCreativeMatrix
from llms.chats import (
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


class BobaApi:
    def __init__(
        self,
        prompts_factory: PromptsFactory,
        content_manager: ContentManager,
        chat_session_memory: ServerChatSessionMemory,
        config_service: ConfigService,
    ):
        self.content_manager = content_manager
        self.chat_session_memory = chat_session_memory
        self.config_service = config_service

        self.prompts_chat = prompts_factory.create_chat_prompt_list(
            self.content_manager.knowledge_base_markdown
        )
        prompts_factory_guided = PromptsFactory("./resources/prompts_guided")
        self.prompts_guided = prompts_factory_guided.create_guided_prompt_list(
            self.content_manager.knowledge_base_markdown
        )

        print(
            f"Model used for guided mode: {self.config_service.get_default_guided_mode_model()}"
        )

    def prompt(self, prompt_id, user_input, chat_session, context=None):
        rendered_prompt = self.prompts_chat.render_prompt(
            active_knowledge_context=context,
            prompt_choice=prompt_id,
            user_input=user_input,
            additional_vars={},
            warnings=[],
        )

        return self.chat(rendered_prompt, chat_session)

    def chat(self, rendered_prompt, chat_session):
        for chunk in chat_session.start_with_prompt(rendered_prompt):
            yield chunk

    def add_endpoints(self, app: FastAPI):
        @app.get("/api/models")
        def get_models(request: Request):
            models: List[Model] = self.config_service.load_models("config.yaml")
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

        ApiThreatModelling(
            app,
            self.chat_session_memory,
            self.config_service.get_default_guided_mode_model(),
            self.prompts_guided,
        )
        ApiRequirementsBreakdown(
            app,
            self.chat_session_memory,
            self.config_service.get_default_guided_mode_model(),
            self.prompts_guided,
        )
        ApiStoryValidation(
            app,
            self.chat_session_memory,
            self.config_service.get_default_guided_mode_model(),
            self.prompts_guided,
        )
        ApiScenarios(
            app,
            self.chat_session_memory,
            self.config_service.get_default_guided_mode_model(),
            self.prompts_guided,
        )
        ApiCreativeMatrix(
            app,
            self.chat_session_memory,
            self.config_service.get_default_guided_mode_model(),
            self.prompts_guided,
        )
