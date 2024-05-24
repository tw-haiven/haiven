# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import gradio as gr
from shared.logger import HaivenLogger
from shared.user_context import user_context


class EventHandler:
    def __init__(self, logger_factory: HaivenLogger):
        self.logger_factory = logger_factory

    def get_user(self, request: gr.Request):
        return request.request.session.get("user", {}).get("sub", "guest")

    def on_ui_load(self, request: gr.Request):
        self.logger_factory.get().analytics(
            f"User {self.get_user(request)} loaded UI at {request.url}"
        )
        return self.get_user(request)

    def on_ui_load_with_tab_deeplink(self, request: gr.Request):
        self.logger_factory.get().analytics(
            f"User {self.get_user(request)} loaded UI at {request.url}"
        )

        if "tab" in request.query_params:
            return gr.Tabs(selected=request.query_params["tab"])

        return gr.Tabs(), self.get_user(request)

    def on_load_ui(
        self,
        model_selected,
        tone_selected,
        knowledge_context_select,
        request: gr.Request,
    ):
        if user_context.get_value(request, "llm_model", app_level=True) is not None:
            model_selected = user_context.get_value(
                request, "llm_model", app_level=True
            )

        if user_context.get_value(request, "llm_tone", app_level=True) is not None:
            tone_selected = user_context.get_value(request, "llm_tone", app_level=True)

        if (
            user_context.get_value(request, "active_knowledge_context", app_level=True)
            is not None
        ):
            knowledge_context_select = user_context.get_value(
                request, "active_knowledge_context", app_level=True
            )

        if user_context.get_active_path(request) != "unknown":
            self.logger_factory.get().analytics(
                f"User {self.get_user(request)} loaded UI at {request.url}"
            )
            selected_tab = user_context.get_value(request, "selected_tab")

            if "tab" in request.query_params:
                return (
                    gr.Tabs(selected=request.query_params["tab"]),
                    model_selected,
                    tone_selected,
                    knowledge_context_select,
                    self.get_user(request),
                )
            return (
                gr.Tabs(selected=selected_tab),
                model_selected,
                tone_selected,
                knowledge_context_select,
                self.get_user(request),
            )
        else:
            return (
                gr.Tabs(),
                model_selected,
                tone_selected,
                knowledge_context_select,
                self.get_user(request),
            )
