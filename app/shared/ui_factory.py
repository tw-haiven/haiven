# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from shared.chats import ServerChatSessionMemory
from shared.content_manager import ContentManager
from shared.event_handler import EventHandler
from shared.navigation import NavigationManager
from shared.prompts_factory import PromptsFactory
from shared.ui import UI
from tab_brainstorming.ui import enable_brainstorming
from tab_diagram_chat.ui import enable_image_chat
from tab_knowledge_chat.ui import enable_knowledge_chat
from tab_plain_chat.ui import enable_plain_chat
from tab_prompt_chat.ui import enable_chat
from shared.user_context import user_context
from datetime import datetime


class UIFactory:
    def __init__(
        self,
        ui: UI,
        prompts_factory: PromptsFactory,
        navigation_manager: NavigationManager,
        event_handler: EventHandler,
        prompts_parent_dir: str,
        content_manager: ContentManager,
        chat_session_memory: ServerChatSessionMemory,
    ):
        self.ui: UI = ui
        self.prompts_factory: PromptsFactory = prompts_factory
        self.navigation_manager: NavigationManager = navigation_manager
        self.event_handler: EventHandler = event_handler
        self.prompts_parent_dir: str = prompts_parent_dir
        self.content_manager: ContentManager = content_manager
        self.chat_session_memory: ServerChatSessionMemory = chat_session_memory
        self.__llm_config = None
        self.__copyright_text = f"© {str(datetime.now().year)} Thoughtworks, Inc."

    def _model_changed(self, model_select, request: gr.Request):
        self.__llm_config.change_model(model_select)
        user_context.set_value(request, "llm_model", model_select, app_level=True)

    def _tone_changed(self, tone_select, request: gr.Request):
        self.__llm_config.change_temperature(tone_select)
        user_context.set_value(request, "llm_tone", tone_select, app_level=True)

    def is_empty(self, value) -> bool:
        return value is None or value == "" or len(value) == 0

    def __knowledge_context_select_changed(
        self, knowledge_context_select, request: gr.Request
    ):
        if not self.is_empty(knowledge_context_select):
            knowledge_context = self.content_manager.on_context_selected(
                knowledge_context_select
            )
            if knowledge_context is not None:
                user_context.set_value(
                    request,
                    "active_knowledge_context",
                    knowledge_context,
                    app_level=True,
                )

    def create_ui(self, ui_type):
        match ui_type:
            case "coding":
                return self.create_ui_coding()
            case "testing":
                return self.create_ui_testing()
            case "analysts":
                return self.create_ui_analysts()
            case "knowledge":
                return self.create_ui_knowledge()
            case "about":
                return self.create_ui_about()
            case "plain_chat":
                return self.create_plain_chat()

    def create_ui_coding(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Haiven")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_coding_navigation()
            )
            self.ui.ui_header(navigation=navigation)
            user_identifier_state = gr.State()
            with gr.Group(elem_classes="teamai-group"):
                with gr.Accordion("Settings"):
                    with gr.Row():
                        knowledge_context_select = (
                            self.ui.create_knowledge_context_selector_ui(
                                self.content_manager.knowledge_pack_definition
                            )
                        )
                        knowledge_context_select.change(
                            fn=self.__knowledge_context_select_changed,
                            inputs=knowledge_context_select,
                        )

                        model_select, tone_select, self.__llm_config = (
                            self.ui.create_llm_settings_ui()
                        )
                        model_select.change(fn=self._model_changed, inputs=model_select)
                        tone_select.change(fn=self._tone_changed, inputs=tone_select)
            with gr.Row():
                with gr.Tabs() as all_tabs:
                    category_filter = ["coding", "architecture"]
                    self.ui.create_about_tab_for_task_area(
                        category_filter,
                        category_metadata,
                        self.prompts_factory.create_all_prompts(
                            self.content_manager.knowledge_base_markdown
                        ),
                    )
                    enable_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )
                    enable_brainstorming(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_image_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )
                    enable_knowledge_chat(
                        self.chat_session_memory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )

            with gr.Row():
                gr.HTML(self.__copyright_text, elem_classes=["copyright_text"])

            blocks.load(
                self.event_handler.on_load_ui,
                [
                    model_select,
                    tone_select,
                    knowledge_context_select,
                ],
                [
                    all_tabs,
                    model_select,
                    tone_select,
                    knowledge_context_select,
                    user_identifier_state,
                ],
            )
            ##add a label

            blocks.queue()

        return blocks

    def create_ui_testing(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Haiven")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_testing_navigation()
            )
            self.ui.ui_header(navigation=navigation)
            with gr.Group(elem_classes="teamai-group"):
                with gr.Accordion("Settings"):
                    with gr.Row():
                        knowledge_context_select = (
                            self.ui.create_knowledge_context_selector_ui(
                                self.content_manager.knowledge_pack_definition
                            )
                        )
                        knowledge_context_select.change(
                            fn=self.__knowledge_context_select_changed,
                            inputs=knowledge_context_select,
                        )

                        model_select, tone_select, self.__llm_config = (
                            self.ui.create_llm_settings_ui()
                        )
                        model_select.change(fn=self._model_changed, inputs=model_select)
                        tone_select.change(fn=self._tone_changed, inputs=tone_select)
            with gr.Row():
                category_filter = ["testing"]

                with gr.Tabs() as all_tabs:
                    user_identifier_state = gr.State()
                    self.ui.create_about_tab_for_task_area(
                        category_filter,
                        category_metadata,
                        self.prompts_factory.create_all_prompts(
                            self.content_manager.knowledge_base_markdown,
                        ),
                    )
                    enable_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )
                    enable_brainstorming(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_image_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )
                    enable_knowledge_chat(
                        self.chat_session_memory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )

            with gr.Row():
                gr.HTML(self.__copyright_text, elem_classes=["copyright_text"])

            blocks.load(
                self.event_handler.on_load_ui,
                [model_select, tone_select, knowledge_context_select],
                [
                    all_tabs,
                    model_select,
                    tone_select,
                    knowledge_context_select,
                    user_identifier_state,
                ],
            )
            blocks.queue()

        return blocks

    def create_ui_analysts(
        self,
    ):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Haiven")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_analysis_navigation()
            )
            self.ui.ui_header(navigation=navigation)
            with gr.Group(elem_classes="teamai-group"):
                with gr.Accordion("Settings"):
                    with gr.Row():
                        knowledge_context_select = (
                            self.ui.create_knowledge_context_selector_ui(
                                self.content_manager.knowledge_pack_definition
                            )
                        )
                        knowledge_context_select.change(
                            fn=self.__knowledge_context_select_changed,
                            inputs=knowledge_context_select,
                        )

                        model_select, tone_select, self.__llm_config = (
                            self.ui.create_llm_settings_ui()
                        )
                        model_select.change(fn=self._model_changed, inputs=model_select)
                        tone_select.change(fn=self._tone_changed, inputs=tone_select)
            with gr.Row():
                category_filter = ["analysis"]
                with gr.Tabs() as all_tabs:
                    user_identifier_state = gr.State()
                    self.ui.create_about_tab_for_task_area(
                        category_filter,
                        category_metadata,
                        self.prompts_factory.create_all_prompts(
                            self.content_manager.knowledge_base_markdown
                        ),
                    )
                    enable_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )
                    enable_brainstorming(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_image_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )
                    enable_knowledge_chat(
                        self.chat_session_memory,
                        self.__llm_config,
                        self.content_manager.active_knowledge_context,
                        user_identifier_state,
                        category_filter,
                        knowledge_context_select,
                    )

            with gr.Row():
                gr.HTML(self.__copyright_text, elem_classes=["copyright_text"])

            blocks.load(
                self.event_handler.on_load_ui,
                [model_select, tone_select, knowledge_context_select],
                [
                    all_tabs,
                    model_select,
                    tone_select,
                    knowledge_context_select,
                    user_identifier_state,
                ],
            )
            blocks.queue()

        return blocks

    def create_ui_knowledge(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Haiven")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_knowledge_navigation()
            )
            self.ui.ui_header(navigation=navigation)

            with gr.Group(elem_classes="teamai-group"):
                with gr.Accordion("Settings"):
                    with gr.Row():
                        knowledge_context_select = (
                            self.ui.create_knowledge_context_selector_ui(
                                self.content_manager.knowledge_pack_definition
                            )
                        )
                        knowledge_context_select.change(
                            fn=self.__knowledge_context_select_changed,
                            inputs=knowledge_context_select,
                        )

                        model_select, tone_select, self.__llm_config = (
                            self.ui.create_llm_settings_ui()
                        )
                        model_select.change(fn=self._model_changed, inputs=model_select)
                        tone_select.change(fn=self._tone_changed, inputs=tone_select)

            with gr.Row():
                category_filter = ["prompting"]
                with gr.Tabs() as all_tabs:
                    user_identifier_state = gr.State()
                    with gr.Tab("Knowledge"):
                        self.ui.ui_show_knowledge(
                            self.content_manager.knowledge_base_markdown,
                            self.content_manager.knowledge_pack_definition,
                        )
                    # TODO: Change tab title to "Prompt development"? And move the LLM choice in there??!
                    with gr.Tab("Prompt Development"):
                        gr.Markdown(
                            "Experimental feature to support prompt development - still in development",
                            elem_classes="disclaimer",
                        )
                        enable_chat(
                            self.content_manager.knowledge_base_markdown,
                            self.chat_session_memory,
                            self.prompts_factory,
                            self.__llm_config,
                            self.content_manager.active_knowledge_context,
                            user_identifier_state,
                            category_filter,
                            knowledge_context_select,
                        )

            with gr.Row():
                gr.HTML(self.__copyright_text, elem_classes=["copyright_text"])

            blocks.load(
                self.event_handler.on_load_ui,
                [model_select, tone_select, knowledge_context_select],
                [
                    all_tabs,
                    model_select,
                    tone_select,
                    knowledge_context_select,
                    user_identifier_state,
                ],
            )
            blocks.queue()

        return blocks

    def create_ui_about(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="About Haiven")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_about_navigation()
            )
            self.ui.ui_header(navigation=navigation)

            with gr.Tab("About"):
                self.ui.ui_show_about()
            with gr.Tab("Data processing"):
                self.ui.ui_show_data_processing()

            with gr.Row():
                gr.HTML(self.__copyright_text, elem_classes=["copyright_text"])

        return blocks

    def create_plain_chat(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Haiven")

        with blocks:
            self.ui.ui_header()
            user_identifier_state = gr.State()

            with gr.Row():
                with gr.Tabs():
                    enable_plain_chat(self.chat_session_memory, user_identifier_state)

            with gr.Row():
                gr.HTML(self.__copyright_text, elem_classes=["copyright_text"])

            blocks.load(
                self.event_handler.on_ui_load, None, outputs=[user_identifier_state]
            )

        blocks.queue()
        return blocks
