# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import FastAPI
from api.api_basics import ApiBasics
from api.api_threat_modelling import ApiThreatModelling
from api.api_scenarios import ApiScenarios
from api.api_requirements import ApiRequirementsBreakdown
from api.api_story_validation import ApiStoryValidation
from api.api_creative_matrix import ApiCreativeMatrix
from llms.chats import (
    ChatManager,
)
from content_manager import ContentManager
from prompts.prompts_factory import PromptsFactory
from config_service import ConfigService


class BobaApi:
    def __init__(
        self,
        prompts_factory: PromptsFactory,
        content_manager: ContentManager,
        chat_manager: ChatManager,
        config_service: ConfigService,
    ):
        self.content_manager = content_manager
        self.chat_manager = chat_manager
        self.config_service = config_service

        self.prompts_chat = prompts_factory.create_chat_prompt_list(
            self.content_manager.knowledge_base_markdown
        )
        prompts_factory_guided = PromptsFactory("./resources/prompts_guided")
        self.prompts_guided = prompts_factory_guided.create_guided_prompt_list(
            self.content_manager.knowledge_base_markdown
        )

        self.model = self.config_service.get_default_guided_mode_model()

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

    def chat(self, rendered_prompt, chat_session):
        for chunk in chat_session.start_with_prompt(rendered_prompt):
            yield chunk

    def add_endpoints(self, app: FastAPI):
        ApiBasics(
            app,
            self.chat_manager,
            self.model,
            self.prompts_guided,
            self.content_manager,
            self.prompts_chat,
        )

        ApiThreatModelling(
            app,
            self.chat_manager,
            self.model,
            self.prompts_guided,
        )
        ApiRequirementsBreakdown(
            app,
            self.chat_manager,
            self.model,
            self.prompts_guided,
        )
        ApiStoryValidation(
            app,
            self.chat_manager,
            self.model,
            self.prompts_guided,
        )
        ApiScenarios(
            app,
            self.chat_manager,
            self.model,
            self.prompts_guided,
        )
        ApiCreativeMatrix(
            app,
            self.chat_manager,
            self.model,
            self.prompts_guided,
        )
