# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from api.boba_api import BobaApi
from knowledge_manager import KnowledgeManager
from llms.chats import ChatManager, ServerChatSessionMemory
from llms.image_description_service import ImageDescriptionService
from llms.clients import ChatClientFactory
from llms.model import Model
from prompts.prompts_factory import PromptsFactory
from prompts.prompts_testing_ui import PromptsTestingUI
from server import Server
from config_service import ConfigService

import gradio as gr


class App:
    def create_image_service(self, config_service):
        model: Model = config_service.get_image_model()

        return ImageDescriptionService(model)

    def __init__(self, config_path: str):
        config_service = ConfigService(config_path)

        knowledge_pack_path = config_service.load_knowledge_pack_path()
        knowledge_manager = KnowledgeManager(config_service=config_service)

        prompts_factory = PromptsFactory(knowledge_pack_path)
        chat_session_memory = ServerChatSessionMemory()
        llm_chat_factory = ChatClientFactory(config_service)
        chat_manager = ChatManager(
            config_service, chat_session_memory, llm_chat_factory, knowledge_manager
        )

        image_service = self.create_image_service(config_service)

        self.prompts_testing_ui = PromptsTestingUI(chat_manager)

        self.server = Server(
            chat_manager,
            config_service,
            BobaApi(
                prompts_factory,
                knowledge_manager,
                chat_manager,
                config_service,
                image_service,
            ),
        ).create()

    def launch_via_fastapi_wrapper(self):
        gr.mount_gradio_app(
            self.server,
            self.prompts_testing_ui.create_gradio_ui(),
            path="/prompting",
            root_path="/prompting",
        )

        return self.server
