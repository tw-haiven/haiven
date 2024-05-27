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

    def __get_query_string_dict(self, request: gr.Request):
        # convert querystring from string to dict
        query_string_dict = {}
        query_string_list = request.url.query.split("&")
        for qs in query_string_list:
            qs_split = qs.split("=")
            if len(qs_split) == 2:
                query_string_dict[qs_split[0]] = qs_split[1]
        return query_string_dict

    def __update_ui(
        self,
        request: gr.Request,
    ):
        query_string_dict = self.__get_query_string_dict(request)

        chat_prompt_choice = None
        brainstorming_prompt_choice = None
        diagram_chat_prompt_choice = None
        knowledge_chat_prompt_choice = None

        if "tab" in query_string_dict and "task" in query_string_dict:
            match query_string_dict["tab"]:
                case "chat":
                    chat_prompt_choice = query_string_dict["task"]
                case "brainstorming":
                    brainstorming_prompt_choice = query_string_dict["task"]
                case "diagram_chat":
                    diagram_chat_prompt_choice = query_string_dict["task"]
                case "knowledge_chat":
                    knowledge_chat_prompt_choice = query_string_dict["task"]

        if "kc" in query_string_dict:
            user_context.set_value(
                request,
                "active_knowledge_context",
                query_string_dict["kc"],
                app_level=True,
            )

        if "llm" in query_string_dict:
            user_context.set_value(
                request, "llm_model", query_string_dict["llm"], app_level=True
            )

        if "task" in query_string_dict:
            task = query_string_dict["task"]
            print(task)

        return (
            chat_prompt_choice,
            brainstorming_prompt_choice,
            diagram_chat_prompt_choice,
            knowledge_chat_prompt_choice,
        )

    def on_load_ui(
        self,
        model_selected,
        tone_selected,
        knowledge_context_select,
        chat_prompt_choice,
        brainstorming_prompt_choice,
        diagram_chat_prompt_choice,
        knowledge_chat_prompt_choice,
        request: gr.Request,
    ):
        (
            new_chat_prompt_choice,
            new_brainstorming_prompt_choice,
            new_diagram_chat_prompt_choice,
            new_knowledge_chat_prompt_choice,
        ) = self.__update_ui(request)

        if new_brainstorming_prompt_choice:
            brainstorming_prompt_choice = new_brainstorming_prompt_choice
        else:
            brainstorming_prompt_choice = gr.Dropdown()

        if new_chat_prompt_choice:
            chat_prompt_choice = new_chat_prompt_choice
        else:
            chat_prompt_choice = gr.Dropdown()

        if new_diagram_chat_prompt_choice:
            diagram_chat_prompt_choice = new_diagram_chat_prompt_choice
        else:
            diagram_chat_prompt_choice = gr.Dropdown()

        if new_knowledge_chat_prompt_choice:
            knowledge_chat_prompt_choice = new_knowledge_chat_prompt_choice
        else:
            knowledge_chat_prompt_choice = gr.Dropdown()

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
                    chat_prompt_choice,
                    brainstorming_prompt_choice,
                    diagram_chat_prompt_choice,
                    knowledge_chat_prompt_choice,
                    self.get_user(request),
                )
            return (
                gr.Tabs(selected=selected_tab),
                model_selected,
                tone_selected,
                knowledge_context_select,
                chat_prompt_choice,
                brainstorming_prompt_choice,
                diagram_chat_prompt_choice,
                knowledge_chat_prompt_choice,
                self.get_user(request),
            )
        else:
            return (
                gr.Tabs(),
                model_selected,
                tone_selected,
                knowledge_context_select,
                chat_prompt_choice,
                brainstorming_prompt_choice,
                diagram_chat_prompt_choice,
                knowledge_chat_prompt_choice,
                self.get_user(request),
            )

    def on_load_ui_knowledge(
        self,
        model_selected,
        tone_selected,
        knowledge_context_select,
        request: gr.Request,
    ):
        return self.on_load_ui(
            model_selected,
            tone_selected,
            knowledge_context_select,
            None,
            None,
            None,
            None,
            request,
        )
