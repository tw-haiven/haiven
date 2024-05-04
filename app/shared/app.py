# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from shared.boba_api import BobaApi
from shared.content_manager import ContentManager
from shared.server import Server
from shared.ui_factory import UIFactory


class App:
    def __init__(self, content_manager: ContentManager, ui_factory: UIFactory):
        self.server = Server(ui_factory.chat_session_memory, BobaApi()).create()
        self.content_manager = content_manager
        self.ui_factory = ui_factory

    def launch_via_fastapi_wrapper(self):
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
            gr.mount_gradio_app(self.server, ui_component, path=path)

        return self.server
