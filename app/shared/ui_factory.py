# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from shared.chats import ServerChatSessionMemory
from shared.content_manager import ContentManager
from shared.event_handler import EventHandler
from shared.navigation import NavigationManager
from shared.prompts_factory import PromptsFactory
from shared.ui import UI
from tab_brainstorming.ui import enable_brainstorming
from tab_db_exploration.ui import enable_db_exploration
from tab_diagram_chat.ui import enable_image_chat
from tab_knowledge_chat.ui import enable_knowledge_chat
from tab_plain_chat.ui import enable_plain_chat
from tab_prompt_chat.ui import enable_chat


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
        blocks = gr.Blocks(theme=theme, css=css, title="Team AI")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_coding_navigation()
            )
            self.ui.ui_header(navigation=navigation)
            user_identifier_state = gr.State()
            with gr.Group(elem_classes="teamai-group"):
                with gr.Row():
                    model_select, tone_select, llm_config = (
                        self.ui.create_llm_settings_ui()
                    )
                    model_select.change(fn=llm_config.change_model, inputs=model_select)
                    tone_select.change(
                        fn=llm_config.change_temperature, inputs=tone_select
                    )
            with gr.Row():
                with gr.Tabs() as all_tabs:
                    category_filter = ["coding", "architecture"]
                    self.ui.create_about_tab_for_task_area(
                        category_filter,
                        category_metadata,
                        self.prompts_factory.create_all_prompts(
                            self.content_manager.knowledge_base_markdown
                        ),
                        _db_exploration_addendum(),
                    )
                    enable_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_brainstorming(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_image_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_knowledge_chat(
                        self.chat_session_memory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_db_exploration(category_filter)

            blocks.load(
                self.event_handler.on_ui_load_with_tab_deeplink,
                None,
                [all_tabs, user_identifier_state],
            )
            blocks.queue()

        return blocks

    def create_ui_testing(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Team AI")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_testing_navigation()
            )
            self.ui.ui_header(navigation=navigation)

            with gr.Group(elem_classes="teamai-group"):
                with gr.Row():
                    model_select, tone_select, llm_config = (
                        self.ui.create_llm_settings_ui()
                    )
                    model_select.change(fn=llm_config.change_model, inputs=model_select)
                    tone_select.change(
                        fn=llm_config.change_temperature, inputs=tone_select
                    )
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
                        _db_exploration_addendum(),
                    )
                    enable_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_brainstorming(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_image_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_knowledge_chat(
                        self.chat_session_memory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_db_exploration(category_filter)

            blocks.load(
                self.event_handler.on_ui_load_with_tab_deeplink,
                None,
                [all_tabs, user_identifier_state],
            )
            blocks.queue()

        return blocks

    def create_ui_analysts(
        self,
    ):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Team AI")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_analysis_navigation()
            )
            self.ui.ui_header(navigation=navigation)

            with gr.Group(elem_classes="teamai-group"):
                with gr.Row():
                    model_select, tone_select, llm_config = (
                        self.ui.create_llm_settings_ui()
                    )
                    model_select.change(fn=llm_config.change_model, inputs=model_select)
                    tone_select.change(
                        fn=llm_config.change_temperature, inputs=tone_select
                    )
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
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_brainstorming(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_image_chat(
                        self.content_manager.knowledge_base_markdown,
                        self.chat_session_memory,
                        self.prompts_factory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )
                    enable_knowledge_chat(
                        self.chat_session_memory,
                        llm_config,
                        user_identifier_state,
                        category_filter,
                    )

            blocks.load(
                self.event_handler.on_ui_load_with_tab_deeplink,
                None,
                [all_tabs, user_identifier_state],
            )
            blocks.queue()

        return blocks

    def create_ui_knowledge(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Team AI")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_knowledge_navigation()
            )
            self.ui.ui_header(navigation=navigation)

            self.ui.ui_show_knowledge(self.content_manager.knowledge_base_markdown)

        return blocks

    def create_ui_about(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="About Team AI")
        with blocks:
            navigation, category_metadata = (
                self.navigation_manager.get_about_navigation()
            )
            self.ui.ui_header(navigation=navigation)

            self.ui.ui_show_about()

        return blocks

    def create_plain_chat(self):
        theme, css = self.ui.styling()
        blocks = gr.Blocks(theme=theme, css=css, title="Team AI")

        with blocks:
            self.ui.ui_header()
            user_identifier_state = gr.State()

            with gr.Row():
                with gr.Tabs():
                    enable_plain_chat(self.chat_session_memory, user_identifier_state)

            blocks.load(
                self.event_handler.on_ui_load, None, outputs=[user_identifier_state]
            )

        blocks.queue()
        return blocks


def _db_exploration_addendum():
    return "\n#### Test DB Exploration\n\nUse natural language queries to explore the test database"
