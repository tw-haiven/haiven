# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from api.boba_api import BobaApi
from knowledge_manager import KnowledgeManager
from llms.chats import ChatManager, ServerChatSessionMemory
from llms.image_description_service import ImageDescriptionService
from llms.clients import ChatClientFactory
from llms.model_config import ModelConfig
from prompts.prompts_factory import PromptsFactory
from server import Server
from config_service import ConfigService
from disclaimer_and_guidelines import DisclaimerAndGuidelinesService
from auth.api_key_repository_factory import ApiKeyRepositoryFactory
from auth.api_key_auth_service import ApiKeyAuthService


class App:
    def create_image_service(self, config_service):
        model: ModelConfig = config_service.get_image_model()

        return ImageDescriptionService(model)

    def _create_api_key_repository(self, config_service):
        return ApiKeyRepositoryFactory.get_repository(config_service)

    def __init__(self, config_path: str):
        config_service = ConfigService(config_path)

        knowledge_pack_path = config_service.load_knowledge_pack_path()
        knowledge_manager = KnowledgeManager(config_service=config_service)

        prompts_factory = PromptsFactory(knowledge_pack_path)
        disclaimer_and_guidelines = DisclaimerAndGuidelinesService(knowledge_pack_path)
        chat_session_memory = ServerChatSessionMemory()
        llm_chat_factory = ChatClientFactory(config_service)
        chat_manager = ChatManager(
            config_service, chat_session_memory, llm_chat_factory, knowledge_manager
        )

        image_service = self.create_image_service(config_service)

        # Conditionally initialize API key authentication based on feature toggle
        api_key_auth_service = None
        if config_service.is_api_key_auth_enabled():
            api_key_repository = self._create_api_key_repository(config_service)
            api_key_auth_service = ApiKeyAuthService(config_service, api_key_repository)

        self.server = Server(
            chat_manager,
            config_service,
            api_key_auth_service,
            BobaApi(
                prompts_factory,
                knowledge_manager,
                chat_manager,
                config_service,
                image_service,
                disclaimer_and_guidelines,
                api_key_auth_service,
            ),
        ).create()

    def launch_via_fastapi_wrapper(self):
        return self.server
