# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from shared.logger import TeamAILogger


class EventHandler:
    def __init__(self, logger_factory: TeamAILogger):
        self.logger_factory = logger_factory

    def on_ui_load(self, request: gr.Request):
        self.logger_factory.get().analytics(
            f"User {request.request.session['user']['sub']} loaded UI at {request.url}"
        )
        return request.session["user"]["sub"]

    def on_ui_load_with_tab_deeplink(self, request: gr.Request):
        self.logger_factory.get().analytics(
            f"User {request.request.session['user']['sub']} loaded UI at {request.url}"
        )

        if "tab" in request.query_params:
            return gr.Tabs(selected=request.query_params["tab"])

        return gr.Tabs(), request.request.session["user"]["sub"]
