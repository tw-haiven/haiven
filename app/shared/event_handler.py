# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from shared.logger import TeamAILogger
from shared.user_context import user_context


class EventHandler:
    def __init__(self, logger_factory: TeamAILogger):
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
        chat_prompt_choice,
        brainstorming_prompt_choice,
        diagram_chat_prompt_choice,
        knowledge_chat_prompt_choice,
        model_selected,
        tone_selected,
        request: gr.Request,
    ):
        if user_context.get_active_path(request) != "unknown":
            if user_context.get_value(request, "llm_model", app_level=True) is not None:
                model_selected = user_context.get_value(
                    request, "llm_model", app_level=True
                )

            if user_context.get_value(request, "llm_tone", app_level=True) is not None:
                tone_selected = user_context.get_value(
                    request, "llm_tone", app_level=True
                )

            if (
                user_context.get_value(request, "brainstorming_prompt_choice")
                is not None
            ):
                brainstorming_prompt_choice = user_context.get_value(
                    request, "brainstorming_prompt_choice"
                )
            if user_context.get_value(request, "chat_prompt_choice") is not None:
                chat_prompt_choice = user_context.get_value(
                    request, "chat_prompt_choice"
                )

            if (
                user_context.get_value(request, "knowledge_chat_prompt_choice")
                is not None
            ):
                knowledge_chat_prompt_choice = user_context.get_value(
                    request, "knowledge_chat_prompt_choice"
                )

            if (
                user_context.get_value(request, "diagram_chat_prompt_choice")
                is not None
            ):
                diagram_chat_prompt_choice = user_context.get_value(
                    request, "diagram_chat_prompt_choice"
                )

            self.logger_factory.get().analytics(
                f"User {self.get_user(request)} loaded UI at {request.url}"
            )
            selected_tab = user_context.get_value(request, "selected_tab")

            if "tab" in request.query_params:
                return (
                    gr.Tabs(selected=request.query_params["tab"]),
                    chat_prompt_choice,
                    brainstorming_prompt_choice,
                    diagram_chat_prompt_choice,
                    knowledge_chat_prompt_choice,
                    model_selected,
                    tone_selected,
                    self.get_user(request),
                )
            return (
                gr.Tabs(selected=selected_tab),
                chat_prompt_choice,
                brainstorming_prompt_choice,
                diagram_chat_prompt_choice,
                knowledge_chat_prompt_choice,
                model_selected,
                tone_selected,
                self.get_user(request),
            )
        else:
            return (
                gr.Tabs(),
                chat_prompt_choice,
                brainstorming_prompt_choice,
                diagram_chat_prompt_choice,
                knowledge_chat_prompt_choice,
                model_selected,
                tone_selected,
                self.get_user(request),
            )
