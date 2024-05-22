# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List

import gradio as gr
from dotenv import load_dotenv
from shared.chats import ServerChatSessionMemory, StreamingChat
from shared.knowledge import KnowledgeBaseMarkdown
from shared.llm_config import LLMConfig
from shared.models.chat_context import ChatContext
from shared.prompts import PromptList
from shared.prompts_factory import PromptsFactory
from shared.services.embeddings_service import EmbeddingsService
from shared.user_context import user_context
from shared.user_feedback import UserFeedback


def enable_chat(
    knowledge_base: KnowledgeBaseMarkdown,
    CHAT_SESSION_MEMORY: ServerChatSessionMemory,
    prompts_factory: PromptsFactory,
    llm_config: LLMConfig,
    active_knowledge_context: str,
    user_identifier_state: gr.State,
    prompt_categories: List[str],
    knowledge_context_select: gr.Dropdown = None,
):
    load_dotenv()
    tab_id = "chat"
    prompt_list = prompts_factory.create_chat_prompt(knowledge_base)
    interaction_pattern_name = prompt_list.interaction_pattern_name
    prompt_list.filter(prompt_categories)

    chat_context = ChatContext(
        tab_id=tab_id,
        interaction_pattern=prompt_categories[0],
        model="",
        temperature=0.2,
        prompt="",
        message="",
    )

    def __render_prompt_with_warnings(
        prompt_list: PromptList,
        active_knowledge_context: str,
        prompt_choice: str,
        user_input: str,
        additional_vars: dict = {},
        show_warning: bool = True,
    ):
        if not prompt_choice:
            return ""

        warnings = []
        rendered_prompt = prompt_list.render_prompt(
            active_knowledge_context=active_knowledge_context,
            prompt_choice=prompt_choice,
            user_input=user_input,
            additional_vars=additional_vars,
            warnings=warnings,
        )
        if show_warning and len(warnings) > 0:
            warnings = "\n".join(warnings)
            gr.Warning(f"{warnings}")
        return rendered_prompt

    def update_llm_config(request: gr.Request):
        llm_config_from_session = user_context.get_value(
            request, "llm_model", app_level=True
        )

        temperature_from_session = user_context.get_value(
            request, "llm_tone", app_level=True
        )

        if llm_config_from_session:
            llm_config.change_model(llm_config_from_session)

        if temperature_from_session:
            llm_config.change_temperature(temperature_from_session)

    def on_change_prompt_choice(
        prompt_choice: str, user_input: str, request: gr.Request
    ):
        context_selected = user_context.get_value(
            request, "active_knowledge_context", app_level=True
        )

        if prompt_choice and context_selected is None:
            gr.Warning("Please select a knowledge context first")
            return [None, "", "", ""]

        if prompt_choice and prompt_list.get(prompt_choice):
            user_context.set_value(request, "chat_prompt_choice", prompt_choice)
            chat_context.prompt = prompt_list.get(prompt_choice).metadata.get(
                "title", "Unnamed use case"
            )
            help, knowledge = prompt_list.render_help_markdown(
                prompt_choice, context_selected
            )

            rendered_prompt = __render_prompt_with_warnings(
                prompt_list, context_selected, prompt_choice, user_input
            )

            return [
                prompt_choice,
                rendered_prompt,
                help,
                knowledge,
            ]
        else:
            return [None, "", "", ""]

    def on_change_user_input(prompt_choice: str, user_input: str, request: gr.Request):
        context_selected = user_context.get_value(
            request, "active_knowledge_context", app_level=True
        )

        if prompt_choice and context_selected is None:
            gr.Warning("Please select a knowledge context first")
            return ""

        ui_prompt = __render_prompt_with_warnings(
            prompt_list, context_selected, prompt_choice, user_input, show_warning=False
        )
        return ui_prompt

    main_tab = gr.Tab(interaction_pattern_name, id=tab_id)

    with main_tab:
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Group(elem_classes=["prompt-choice", "teamai-group"]):
                    gr.Markdown(
                        "## 1. What do you want to do?",
                        elem_classes="teamai-group-title",
                    )
                    ui_prompt_dropdown = gr.Dropdown(
                        prompt_list.get_title_id_tuples(),
                        label="Choose a task",
                        elem_id="chat_prompt_choice",
                    )
                    ui_help = gr.Markdown(
                        elem_classes="prompt-help", elem_id="chat_help"
                    )
                    ui_help_knowledge = gr.Markdown(
                        elem_classes=["prompt-help", "knowledge"],
                        elem_id="chat_help_knowledge",
                    )
                    ui_user_input = gr.Textbox(label="Your input", lines=5)

                with gr.Group(elem_classes="teamai-group"):
                    gr.Markdown(
                        "## 2. Start the chat", elem_classes="teamai-group-title"
                    )
                    ui_start_btn = gr.Button("Start >>", variant="primary")
                    with gr.Accordion(label="View or change the prompt", open=False):
                        ui_prompt = gr.Textbox(
                            label="Prompt",
                            lines=10,
                            info="Will be composed from your inputs above, or write your own",
                        )

            with gr.Column(scale=5):
                with gr.Group(elem_classes="teamai-group"):
                    gr.Markdown("## 3. Chat", elem_classes="teamai-group-title")
                    ui_chatbot = gr.Chatbot(
                        label="Chat conversation",
                        height=500,
                        show_copy_button=True,
                        show_label=False,
                        likeable=True,
                    )
                    ui_message = gr.Textbox(label="Message (hit Enter to send)")

                    with gr.Group():
                        with gr.Row(elem_classes="knowledge-advice"):
                            context_selected = active_knowledge_context
                            knowledge_documents = [("All documents", "all")]
                            knowledge_documents.extend(
                                [
                                    (embedding.title, embedding.key)
                                    for embedding in EmbeddingsService.get_embedded_documents(
                                        context=context_selected
                                    )
                                ]
                            )
                            ui_knowledge_choice = gr.Dropdown(
                                knowledge_documents,
                                elem_classes="knowledge-label",
                                label="Team knowledge",
                            )
                            ui_get_knowledge_advice_button = gr.Button(
                                "Get input from team knowledge",
                                elem_classes="knowledge-button",
                            )
                    ui_clear_button = gr.Button("Clear and start a new chat")

                ui_prompt_dropdown.change(
                    fn=on_change_prompt_choice,
                    inputs=[ui_prompt_dropdown, ui_user_input],
                    outputs=[ui_prompt_dropdown, ui_prompt, ui_help, ui_help_knowledge],
                )
                ui_user_input.change(
                    fn=on_change_user_input,
                    inputs=[ui_prompt_dropdown, ui_user_input],
                    outputs=ui_prompt,
                )

        def clear(chat_session_key_value: str):
            CHAT_SESSION_MEMORY.delete_entry(chat_session_key_value)

            return {ui_message: "", ui_chatbot: []}

        def start(prompt_text: str, user_identifier_state: str, request: gr.Request):
            if prompt_text:
                update_llm_config(request)

                chat_session_key_value, chat_session = (
                    CHAT_SESSION_MEMORY.get_or_create_chat(
                        lambda: StreamingChat(llm_config=llm_config),
                        None,
                        "chat",
                        user_identifier_state,
                    )
                )

                for chat_history_chunk in chat_session.start_with_prompt(prompt_text):
                    yield {
                        ui_message: "",
                        ui_chatbot: chat_history_chunk,
                        state_chat_session_key: chat_session_key_value,
                    }
            else:
                gr.Warning("Please choose a task first")
                gr.update(ui_message="", ui_chatbot=[], state_chat_session_key=None)

        def chat(
            message_value: str,
            chat_history,
            chat_session_key_value,
            user_identifier_state,
        ):
            chat_session_key_value, chat_session = (
                CHAT_SESSION_MEMORY.get_or_create_chat(
                    fn_create_chat=lambda: StreamingChat(llm_config=llm_config),
                    chat_session_key_value=chat_session_key_value,
                    chat_category="chat",
                    user_identifier=user_identifier_state,
                )
            )

            for chat_history_chunk in chat_session.next(message_value, chat_history):
                yield {ui_message: "", ui_chatbot: chat_history_chunk}

        def chat_with_knowledge(
            knowledge_choice: str,
            chat_history,
            chat_session_key_value,
            request: gr.Request,
        ):
            chat_session = CHAT_SESSION_MEMORY.get_chat(chat_session_key_value)
            update_llm_config(request)
            chat_session.llm_config = llm_config

            if knowledge_choice == []:
                raise ValueError("No knowledge base selected")

            context_selected = user_context.get_value(
                request, "active_knowledge_context", True
            )

            for chat_history_chunk in chat_session.next_advice_from_knowledge(
                chat_history, knowledge_choice, context_selected
            ):
                yield {ui_chatbot: chat_history_chunk}

        state_chat_session_key = gr.State()

        ui_start_btn.click(
            start,
            [ui_prompt, user_identifier_state],
            [ui_message, ui_chatbot, state_chat_session_key],
            scroll_to_output=True,
        )
        ui_message.submit(
            fn=chat,
            inputs=[
                ui_message,
                ui_chatbot,
                state_chat_session_key,
                user_identifier_state,
            ],
            outputs=[ui_message, ui_chatbot],
            scroll_to_output=True,
        )
        ui_get_knowledge_advice_button.click(
            chat_with_knowledge,
            [
                ui_knowledge_choice,
                ui_chatbot,
                state_chat_session_key,
            ],
            [ui_chatbot],
            scroll_to_output=True,
        )
        ui_clear_button.click(
            fn=clear,
            inputs=[state_chat_session_key],
            outputs=[ui_chatbot, ui_message],
            scroll_to_output=True,
        )

        def on_vote(vote: gr.LikeData):
            chat_context.model = llm_config.service_name
            chat_context.temperature = llm_config.temperature
            chat_context.message = vote.value

            UserFeedback.on_message_voted(
                "liked" if vote.liked else "disliked",
                chat_context.to_dict(),
            )

        ui_chatbot.like(on_vote, None, None)

    def is_empty(value) -> bool:
        return value is None or value == "" or len(value) == 0

    def on_knowledge_context_selected(knowledge_context_select, request: gr.Request):
        if is_empty(knowledge_context_select):
            return

        choices = [("All Documents", "all")]
        choices.extend(
            (embedding.title, embedding.key)
            for embedding in EmbeddingsService.get_embedded_documents(
                context=knowledge_context_select
            )
        )

        udated_dd = gr.update(choices=choices)

        return udated_dd

    if knowledge_context_select:
        gr.on(
            triggers=[knowledge_context_select.change],
            fn=on_knowledge_context_selected,
            inputs=knowledge_context_select,
            outputs=ui_knowledge_choice,
        )
