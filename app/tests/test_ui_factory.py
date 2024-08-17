# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock
from ui.ui_factory import UIFactory
import gradio as gr


class TestUIFactory(unittest.TestCase):
    @patch("llms.image_description_service.ImageDescriptionService")
    @patch("ui.ui_factory.gr.State")
    @patch("ui.ui_factory.gr.Blocks")
    @patch("ui.ui_factory.gr.Tabs")
    @patch("ui.ui_factory.enable_chat")
    @patch("ui.ui_factory.enable_brainstorming")
    @patch("ui.ui_factory.enable_image_chat")
    @patch("ui.ui_factory.enable_knowledge_chat")
    def test_create_ui_coding(
        self,
        mock_enable_knowledge_chat,
        mock_enable_image_chat,
        mock_enable_brainstorming,
        mock_enable_chat,
        mock_tabs,
        mock_blocks,
        mock_state,
        mock_image_description_service,
    ):
        # Setup
        ui = Mock()
        prompts_factory = MagicMock()
        navigation_manager = MagicMock()
        event_handler = MagicMock()
        prompts_parent_dir = "test_parent_dir"
        knowledge_base_markdown = MagicMock()
        active_context = "test_context"
        content_manager = MagicMock()
        content_manager.knowledge_base_markdown = knowledge_base_markdown
        content_manager.active_knowledge_context = active_context
        chat_manager = MagicMock()

        ui_factory = UIFactory(
            ui_base_components=ui,
            prompts_factory=prompts_factory,
            navigation_manager=navigation_manager,
            event_handler=event_handler,
            prompts_parent_dir=prompts_parent_dir,
            content_manager=content_manager,
            chat_manager=chat_manager,
            image_service=mock_image_description_service,
        )

        blocks = MagicMock()
        mock_blocks.return_value = blocks
        state = MagicMock()
        mock_state.return_value = state
        all_tabs = MagicMock()
        tabs = MagicMock()
        tabs.__enter__.return_value = all_tabs
        mock_tabs.return_value = tabs
        category_filter = ["coding", "architecture"]
        all_prompts = MagicMock()
        prompts_factory.create_all_prompts_for_user_choice.return_value = all_prompts
        theme = MagicMock()
        css = MagicMock()
        ui.styling.return_value = (theme, css)
        llm_config = MagicMock()
        model_select = MagicMock()
        tone_select = MagicMock()
        ui.create_llm_settings_ui.return_value = (model_select, tone_select, llm_config)
        knowledge_context_select = MagicMock()
        ui.create_knowledge_context_selector_ui.return_value = knowledge_context_select
        navigation = MagicMock()
        category_metadata = MagicMock()
        ui_factory.navigation_manager.get_coding_navigation.return_value = (
            navigation,
            category_metadata,
        )

        # Mocking the tab controls
        element_ids = [
            "chat_prompt_choice",
            "brainstorming_prompt_choice",
            "diagram_chat_prompt_choice",
            "knowledge_chat_prompt_choice",
        ]
        all_tabs.children = []
        for element_id in element_ids:
            all_tabs.children.append(gr.Markdown(elem_id=element_id))
        # Action
        returned_blocks = ui_factory.create_ui(ui_type="coding")

        # Assert
        ui.styling.assert_called_once()
        mock_blocks.assert_called_with(theme=theme, css=css, title="Haiven")
        navigation_manager.get_coding_navigation.assert_called_once()
        ui.ui_header.assert_called_with(navigation=navigation)
        prompts_factory.create_all_prompts_for_user_choice.assert_called_with(
            knowledge_base_markdown
        )
        ui.create_about_tab_for_task_area.assert_called_with(
            category_filter, category_metadata, all_prompts
        )
        mock_enable_chat.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            knowledge_context_select,
        )
        mock_enable_brainstorming.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            state,
            category_filter,
        )
        mock_enable_image_chat.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            mock_image_description_service,
            knowledge_context_select,
        )
        mock_enable_knowledge_chat.assert_called_with(
            chat_manager,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            knowledge_context_select,
        )

        blocks.load.assert_called_with(
            event_handler.on_load_ui,
            [model_select, tone_select, knowledge_context_select],
            [
                all_tabs,
                model_select,
                tone_select,
                knowledge_context_select,
                state,
            ],
        )
        blocks.queue.assert_called_once()

        assert returned_blocks == blocks

    @patch("llms.image_description_service.ImageDescriptionService")
    @patch("ui.ui_factory.gr.State")
    @patch("ui.ui_factory.gr.Blocks")
    @patch("ui.ui_factory.gr.Tabs")
    @patch("ui.ui_factory.enable_chat")
    @patch("ui.ui_factory.enable_brainstorming")
    @patch("ui.ui_factory.enable_image_chat")
    @patch("ui.ui_factory.enable_knowledge_chat")
    def test_create_ui_testing(
        self,
        mock_enable_knowledge_chat,
        mock_enable_image_chat,
        mock_enable_brainstorming,
        mock_enable_chat,
        mock_tabs,
        mock_blocks,
        mock_state,
        mock_image_description_service,
    ):
        # Setup
        ui = Mock()
        prompts_factory = MagicMock()
        navigation_manager = MagicMock()
        event_handler = MagicMock()
        prompts_parent_dir = "test_parent_dir"
        knowledge_base_markdown = MagicMock()
        active_context = "test_context"
        content_manager = MagicMock()
        content_manager.knowledge_base_markdown = knowledge_base_markdown
        content_manager.active_knowledge_context = active_context
        chat_manager = MagicMock()

        ui_factory = UIFactory(
            ui_base_components=ui,
            prompts_factory=prompts_factory,
            navigation_manager=navigation_manager,
            event_handler=event_handler,
            prompts_parent_dir=prompts_parent_dir,
            content_manager=content_manager,
            chat_manager=chat_manager,
            image_service=mock_image_description_service,
        )

        blocks = MagicMock()
        mock_blocks.return_value = blocks
        state = MagicMock()
        mock_state.return_value = state
        all_tabs = MagicMock()
        tabs = MagicMock()
        tabs.__enter__.return_value = all_tabs
        mock_tabs.return_value = tabs
        category_filter = ["testing"]
        all_prompts = MagicMock()
        prompts_factory.create_all_prompts_for_user_choice.return_value = all_prompts
        theme = MagicMock()
        css = MagicMock()
        ui.styling.return_value = (theme, css)
        llm_config = MagicMock()
        model_select = MagicMock()
        tone_select = MagicMock()
        ui.create_llm_settings_ui.return_value = (model_select, tone_select, llm_config)
        knowledge_context_select = MagicMock()
        ui.create_knowledge_context_selector_ui.return_value = knowledge_context_select
        navigation = MagicMock()
        category_metadata = MagicMock()
        ui_factory.navigation_manager.get_testing_navigation.return_value = (
            navigation,
            category_metadata,
        )

        # Mocking the tab controls
        element_ids = [
            "chat_prompt_choice",
            "brainstorming_prompt_choice",
            "diagram_chat_prompt_choice",
            "knowledge_chat_prompt_choice",
        ]
        all_tabs.children = []
        for element_id in element_ids:
            all_tabs.children.append(gr.Markdown(elem_id=element_id))

        # Action
        returned_blocks = ui_factory.create_ui(ui_type="testing")

        # # Assert
        ui.styling.assert_called_once()
        mock_blocks.assert_called_with(theme=theme, css=css, title="Haiven")
        navigation_manager.get_testing_navigation.assert_called_once()
        ui.ui_header.assert_called_with(navigation=navigation)
        prompts_factory.create_all_prompts_for_user_choice.assert_called_with(
            knowledge_base_markdown
        )
        ui.create_about_tab_for_task_area.assert_called_with(
            category_filter, category_metadata, all_prompts
        )
        mock_enable_chat.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            knowledge_context_select,
        )
        mock_enable_brainstorming.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            state,
            category_filter,
        )
        mock_enable_image_chat.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            mock_image_description_service,
            knowledge_context_select,
        )
        mock_enable_knowledge_chat.assert_called_with(
            chat_manager,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            knowledge_context_select,
        )
        blocks.load.assert_called_with(
            event_handler.on_load_ui,
            [model_select, tone_select, knowledge_context_select],
            [
                all_tabs,
                model_select,
                tone_select,
                knowledge_context_select,
                state,
            ],
        )
        blocks.queue.assert_called_once()

        assert returned_blocks == blocks

    @patch("llms.image_description_service.ImageDescriptionService")
    @patch("ui.ui_factory.gr.State")
    @patch("ui.ui_factory.gr.Blocks")
    @patch("ui.ui_factory.gr.Tabs")
    @patch("ui.ui_factory.enable_chat")
    @patch("ui.ui_factory.enable_brainstorming")
    @patch("ui.ui_factory.enable_image_chat")
    @patch("ui.ui_factory.enable_knowledge_chat")
    def test_create_ui_analysts(
        self,
        mock_enable_knowledge_chat,
        mock_enable_image_chat,
        mock_enable_brainstorming,
        mock_enable_chat,
        mock_tabs,
        mock_blocks,
        mock_state,
        mock_image_description_service,
    ):
        # Setup
        ui = Mock()
        prompts_factory = MagicMock()
        navigation_manager = MagicMock()
        event_handler = MagicMock()
        prompts_parent_dir = "test_parent_dir"
        knowledge_base_markdown = MagicMock()
        active_knowldge_context = "test_context"
        content_manager = MagicMock()
        content_manager.knowledge_base_markdown = knowledge_base_markdown
        content_manager.active_knowledge_context = active_knowldge_context
        chat_manager = MagicMock()

        ui_factory = UIFactory(
            ui_base_components=ui,
            prompts_factory=prompts_factory,
            navigation_manager=navigation_manager,
            event_handler=event_handler,
            prompts_parent_dir=prompts_parent_dir,
            content_manager=content_manager,
            chat_manager=chat_manager,
            image_service=mock_image_description_service,
        )

        blocks = MagicMock()
        mock_blocks.return_value = blocks
        state = MagicMock()
        mock_state.return_value = state
        all_tabs = MagicMock()
        tabs = MagicMock()
        tabs.__enter__.return_value = all_tabs
        mock_tabs.return_value = tabs
        category_filter = ["analysis"]
        all_prompts = MagicMock()
        prompts_factory.create_all_prompts_for_user_choice.return_value = all_prompts
        theme = MagicMock()
        css = MagicMock()
        ui.styling.return_value = (theme, css)
        llm_config = MagicMock()
        model_select = MagicMock()
        tone_select = MagicMock()
        ui.create_llm_settings_ui.return_value = (model_select, tone_select, llm_config)
        knowledge_context_select = MagicMock()
        ui.create_knowledge_context_selector_ui.return_value = knowledge_context_select
        navigation = MagicMock()
        category_metadata = MagicMock()
        ui_factory.navigation_manager.get_analysis_navigation.return_value = (
            navigation,
            category_metadata,
        )

        # Mocking the tab controls
        element_ids = [
            "chat_prompt_choice",
            "brainstorming_prompt_choice",
            "diagram_chat_prompt_choice",
            "knowledge_chat_prompt_choice",
        ]
        all_tabs.children = []
        for element_id in element_ids:
            all_tabs.children.append(gr.Markdown(elem_id=element_id))

        # Action
        returned_blocks = ui_factory.create_ui(ui_type="analysts")

        # Assert
        ui.styling.assert_called_once()
        mock_blocks.assert_called_with(theme=theme, css=css, title="Haiven")
        navigation_manager.get_analysis_navigation.assert_called_once()
        ui.ui_header.assert_called_with(navigation=navigation)
        prompts_factory.create_all_prompts_for_user_choice.assert_called_with(
            knowledge_base_markdown
        )
        ui.create_about_tab_for_task_area.assert_called_with(
            category_filter, category_metadata, all_prompts
        )
        mock_enable_chat.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            knowledge_context_select,
        )
        mock_enable_brainstorming.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            state,
            category_filter,
        )
        mock_enable_image_chat.assert_called_with(
            knowledge_base_markdown,
            chat_manager,
            prompts_factory,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            mock_image_description_service,
            knowledge_context_select,
        )
        mock_enable_knowledge_chat.assert_called_with(
            chat_manager,
            llm_config,
            content_manager.active_knowledge_context,
            state,
            category_filter,
            knowledge_context_select,
        )
        blocks.load.assert_called_with(
            event_handler.on_load_ui,
            [model_select, tone_select, knowledge_context_select],
            [
                all_tabs,
                model_select,
                tone_select,
                knowledge_context_select,
                state,
            ],
        )
        blocks.queue.assert_called_once()

        assert returned_blocks == blocks

    @patch("ui.ui_factory.enable_chat")
    @patch("ui.ui_factory.gr.State")
    @patch("ui.ui_factory.gr.Blocks")
    def test_create_ui_knowledge(self, mock_blocks, mock_state, mock_enable_chat):
        # Setup
        model_select = MagicMock()
        tone_select = MagicMock()
        llm_config = MagicMock()
        change_model = MagicMock()
        type(llm_config).change_model = PropertyMock(return_value=change_model)
        change_temperature = MagicMock()
        type(llm_config).change_temperature = PropertyMock(
            return_value=change_temperature
        )
        ui = MagicMock()
        ui.create_llm_settings_ui.return_value = model_select, tone_select, llm_config
        knowledge_context_select = MagicMock()
        ui.create_knowledge_context_selector_ui.return_value = knowledge_context_select
        prompts_factory = MagicMock()
        navigation_manager = MagicMock()
        event_handler = MagicMock()
        prompts_parent_dir = "test_parent_dir"
        knowledge_base_markdown = MagicMock()
        active_knowledge_context = "test_context"
        knowledge_pack = MagicMock()
        content_manager = MagicMock()
        content_manager.knowledge_pack_definition = knowledge_pack
        content_manager.knowledge_base_markdown = knowledge_base_markdown
        content_manager.active_knowledge_context = active_knowledge_context
        chat_manager = MagicMock()

        ui_factory = UIFactory(
            ui_base_components=ui,
            prompts_factory=prompts_factory,
            navigation_manager=navigation_manager,
            event_handler=event_handler,
            prompts_parent_dir=prompts_parent_dir,
            content_manager=content_manager,
            chat_manager=chat_manager,
            image_service=MagicMock(),
        )

        blocks = MagicMock()
        mock_blocks.return_value = blocks
        theme = MagicMock()
        css = MagicMock()
        ui_factory.ui_base_components.styling.return_value = (theme, css)
        ui_factory.navigation_manager.get_knowledge_navigation.return_value = (
            MagicMock(),
            MagicMock(),
        )
        user_identifier_state = MagicMock()
        mock_state.return_value = user_identifier_state

        # Action
        returned_blocks = ui_factory.create_ui("knowledge")

        # Assert
        mock_blocks.assert_called_with(theme=theme, css=css, title="Haiven")
        ui_factory.ui_base_components.styling.assert_called_once()
        ui_factory.navigation_manager.get_knowledge_navigation.assert_called_once()
        ui_factory.ui_base_components.ui_header.assert_called_once()
        ui_factory.ui_base_components.ui_show_knowledge.assert_called_with(
            knowledge_base_markdown, content_manager.knowledge_pack_definition
        )
        ui.create_llm_settings_ui.assert_called_once()

        assert returned_blocks == blocks

    @patch("ui.ui_factory.gr.Blocks")
    def test_create_ui_about(self, mock_blocks):
        # Setup
        ui = Mock()
        prompts_factory = MagicMock()
        navigation_manager = MagicMock()
        event_handler = MagicMock()
        prompts_parent_dir = "test_parent_dir"
        knowledge_base_markdown = MagicMock()
        content_manager = MagicMock()
        content_manager.knowledge_base_markdown = knowledge_base_markdown
        content_manager.active_knowledge_context = None
        chat_manager = MagicMock()

        ui_factory = UIFactory(
            ui_base_components=ui,
            prompts_factory=prompts_factory,
            navigation_manager=navigation_manager,
            event_handler=event_handler,
            prompts_parent_dir=prompts_parent_dir,
            content_manager=content_manager,
            chat_manager=chat_manager,
            image_service=MagicMock(),
        )

        blocks = MagicMock()
        mock_blocks.return_value = blocks
        theme = MagicMock()
        css = MagicMock()
        ui_factory.ui_base_components.styling.return_value = (theme, css)
        navigation = MagicMock()
        category_metadata = MagicMock()
        ui_factory.navigation_manager.get_about_navigation.return_value = (
            navigation,
            category_metadata,
        )

        # Action
        returned_blocks = ui_factory.create_ui(ui_type="about")

        # Assert
        mock_blocks.assert_called_with(theme=theme, css=css, title="About Haiven")
        ui_factory.ui_base_components.styling.assert_called_once()
        ui_factory.navigation_manager.get_about_navigation.assert_called_once()
        ui_factory.ui_base_components.ui_header.assert_called_once()
        ui_factory.ui_base_components.ui_show_about.assert_called_once()

        assert returned_blocks == blocks

    @patch("ui.ui_factory.gr.Blocks")
    @patch("ui.ui_factory.gr.Row")
    @patch("ui.ui_factory.gr.State")
    @patch("ui.ui_factory.enable_plain_chat")
    def test_create_plain_chat(
        self, mock_enable_plain_chat, mock_state, mock_row, mock_blocks
    ):
        # Setup
        ui = Mock()
        prompts_factory = MagicMock()
        navigation_manager = MagicMock()
        event_handler = MagicMock()
        prompts_parent_dir = "test_parent_dir"
        knowledge_base_markdown = MagicMock()
        content_manager = MagicMock()
        content_manager.knowledge_base_markdown = knowledge_base_markdown
        chat_manager = MagicMock()

        ui_factory = UIFactory(
            ui_base_components=ui,
            prompts_factory=prompts_factory,
            navigation_manager=navigation_manager,
            event_handler=event_handler,
            prompts_parent_dir=prompts_parent_dir,
            content_manager=content_manager,
            chat_manager=chat_manager,
            image_service=MagicMock(),
        )

        theme = MagicMock()
        css = MagicMock()

        ui.styling.return_value = (theme, css)
        blocks = MagicMock()
        mock_blocks.return_value = blocks
        row = MagicMock()
        mock_row.return_value = row
        state = MagicMock()
        mock_state.return_value = state

        # Action
        returned_blocks = ui_factory.create_ui(ui_type="plain_chat")

        # Assert
        ui.styling.assert_called_once()
        mock_blocks.assert_called_with(theme=theme, css=css, title="Haiven")
        ui.ui_header.assert_called_once()
        blocks.load.assert_called_with(
            event_handler.on_load_plain_chat_ui, None, outputs=[state]
        )
        mock_enable_plain_chat.assert_called_with(chat_manager, state, ui)
        blocks.queue.assert_called_once()

        assert returned_blocks == blocks
