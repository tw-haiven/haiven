# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import FastAPI
from api.api_basics import ApiBasics
from api.api_multi_step import ApiMultiStep
from api.api_scenarios import ApiScenarios
from api.api_requirements import ApiRequirementsBreakdown
from api.api_creative_matrix import ApiCreativeMatrix
from llms.chats import (
    ChatManager,
)
from knowledge_manager import KnowledgeManager
from llms.image_description_service import ImageDescriptionService
from prompts.prompts_factory import PromptsFactory
from config_service import ConfigService
from disclaimer_and_guidelines import DisclaimerAndGuidelinesService


class BobaApi:
    def __init__(
        self,
        prompts_factory: PromptsFactory,
        knowledge_manager: KnowledgeManager,
        chat_manager: ChatManager,
        config_service: ConfigService,
        image_service: ImageDescriptionService,
        disclaimer_and_guidelines: DisclaimerAndGuidelinesService,
    ):
        self.knowledge_manager = knowledge_manager
        self.chat_manager = chat_manager
        self.config_service = config_service

        self.prompts_chat = prompts_factory.create_chat_prompt_list(
            self.knowledge_manager.knowledge_base_markdown
        )
        prompts_factory_guided = PromptsFactory("./resources/prompts_guided")
        self.prompts_guided = prompts_factory_guided.create_guided_prompt_list(
            self.knowledge_manager.knowledge_base_markdown
        )

        self.model_config = self.config_service.get_chat_model()

        self.image_service = image_service
        self.disclaimer_and_guidelines = disclaimer_and_guidelines

        print(f"Model used for guided mode: {self.model_config.id}")

    def add_endpoints(self, app: FastAPI):
        ApiBasics(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_guided,
            self.knowledge_manager,
            self.prompts_chat,
            self.image_service,
            self.config_service,
            self.disclaimer_and_guidelines,
        )
        ApiMultiStep(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_chat,
        )

        ApiRequirementsBreakdown(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_guided,
        )
        ApiScenarios(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_guided,
        )
        ApiCreativeMatrix(
            app,
            self.chat_manager,
            self.model_config,
            self.prompts_guided,
        )
