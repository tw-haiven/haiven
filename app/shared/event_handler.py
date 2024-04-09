# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from shared.logger import TeamAILogger


class EventHandler:
    def __init__(self, logger_factory: TeamAILogger):
        self.logger_factory = logger_factory

    def get_user(self, request: gr.Request):
        return request.request.session.get("user", {}).get("sub", "guest")

    def on_ui_load(self, request: gr.Request):
        self.logger_factory.get().analytics(
            f"User {self.get_user(request)} loaded UI at {request.url}"
        )
        return request.session.get("user", {}).get("sub")

    def on_ui_load_with_tab_deeplink(self, request: gr.Request):
        self.logger_factory.get().analytics(
            f"User {self.get_user(request)} loaded UI at {request.url}"
        )

        if "tab" in request.query_params:
            return gr.Tabs(selected=request.query_params["tab"])

        return gr.Tabs(), self.get_user(request)
