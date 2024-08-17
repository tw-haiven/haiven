# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import gradio as gr
from api.boba_api import BobaApi
from content_manager import ContentManager
from llms.chats import ChatManager, ServerChatSessionMemory
from llms.image_description_service import ImageDescriptionService
from llms.clients import ChatClientFactory
from llms.model import Model
from logger import HaivenLogger
from prompts.prompts_factory import PromptsFactory
from server import Server
from ui.event_handler import EventHandler
from ui.navigation import NavigationManager
from ui.ui import UIBaseComponents
from ui.ui_factory import UIFactory
from config_service import ConfigService


class App:
    def create_image_service(self, config_service):
        available_vision_models = [
            (available_model.name, available_model.id)
            for available_model in config_service.load_enabled_models(
                features=["image-to-text"],
            )
        ]

        model_id = (
            config_service.load_default_models().vision or available_vision_models[0][1]
            if len(available_vision_models) > 0
            else None
        )

        model: Model = config_service.get_model(model_id)

        return ImageDescriptionService(model)

    def __init__(self, config_path: str):
        config_service = ConfigService(config_path)

        knowledge_pack_path = config_service.load_knowledge_pack_path()
        content_manager = ContentManager(config_service=config_service)

        prompts_factory = PromptsFactory(knowledge_pack_path)
        chat_session_memory = ServerChatSessionMemory()
        llm_chat_factory = ChatClientFactory(config_service)
        chat_manager = ChatManager(
            config_service, chat_session_memory, llm_chat_factory
        )

        self.ui_factory = UIFactory(
            ui_base_components=UIBaseComponents(config_service),
            prompts_factory=prompts_factory,
            navigation_manager=NavigationManager(),
            event_handler=EventHandler(HaivenLogger),
            prompts_parent_dir=knowledge_pack_path,
            content_manager=content_manager,
            chat_manager=chat_manager,
            image_service=self.create_image_service(config_service),
        )

        self.server = Server(
            chat_manager,
            config_service,
            BobaApi(
                prompts_factory,
                content_manager,
                chat_manager,
                config_service,
            ),
        ).create()

    def launch_via_fastapi_wrapper(self):
        if self.ui_factory is not None:
            ui_components = [
                ("create_ui_analysts", "get_analysis_path"),
                ("create_ui_testing", "get_testing_path"),
                ("create_ui_coding", "get_coding_path"),
                ("create_ui_knowledge", "get_knowledge_path"),
                ("create_ui_about", "get_about_path"),
                ("create_plain_chat", "get_chat_path"),
            ]

            for create_ui, get_path in ui_components:
                ui_component = getattr(self.ui_factory, create_ui)()
                path = getattr(self.ui_factory.navigation_manager, get_path)()

                gr.mount_gradio_app(
                    self.server, ui_component, path=path, root_path=path
                )

        return self.server
