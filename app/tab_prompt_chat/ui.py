# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from dotenv import load_dotenv
from shared.services.embeddings_service import EmbeddingsService
from shared.llm_config import LLMConfig
from shared.prompts_factory import PromptsFactory
from shared.chats import ServerChatSessionMemory, StreamingChat
from shared.knowledge import KnowledgeBaseMarkdown
from shared.models.chat_context import ChatContext
from shared.user_feedback import UserFeedback


def enable_chat(
    knowledge_base: KnowledgeBaseMarkdown,
    CHAT_SESSION_MEMORY: ServerChatSessionMemory,
    prompts_factory: PromptsFactory,
    llm_config: LLMConfig,
    user_identifier_state: gr.State,
    prompt_categories=None,
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

    def on_change_prompt_choice(prompt_choice: str, user_input: str):
        chat_context.prompt = prompt_list.get(prompt_choice).metadata.get(
            "title", "Unnamed use case"
        )
        help, knowledge = prompt_list.render_help_markdown(prompt_choice)
        rendered_prompt = prompt_list.render_prompt(prompt_choice, user_input)
        return {ui_prompt: rendered_prompt, ui_help: help, ui_help_knowledge: knowledge}

    def on_change_user_input(prompt_choice: str, user_input: str):
        return {ui_prompt: prompt_list.render_prompt(prompt_choice, user_input)}

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
                        prompt_list.get_title_id_tuples(), label="Choose a task"
                    )
                    ui_help = gr.Markdown(elem_classes="prompt-help")
                    ui_help_knowledge = gr.Markdown(
                        elem_classes=["prompt-help", "knowledge"]
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
                            knowledge_documents = [("All documents", "all")]
                            knowledge_documents.extend(
                                [
                                    (embedding.title, embedding.key)
                                    for embedding in EmbeddingsService.get_embedded_documents()
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
                    outputs=[ui_prompt, ui_help, ui_help_knowledge],
                )
                ui_user_input.change(
                    fn=on_change_user_input,
                    inputs=[ui_prompt_dropdown, ui_user_input],
                    outputs=ui_prompt,
                )

        def clear(chat_session_key_value: str):
            CHAT_SESSION_MEMORY.delete_entry(chat_session_key_value)

            return {ui_message: "", ui_chatbot: []}

        def start(prompt_text: str, user_identifier_state: str):
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
            knowledge_choice: str, chat_history, chat_session_key_value
        ):
            chat_session = CHAT_SESSION_MEMORY.get_chat(chat_session_key_value)

            if knowledge_choice == []:
                raise ValueError("No knowledge base selected")

            for chat_history_chunk in chat_session.next_advice_from_knowledge(
                chat_history, knowledge_choice
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
            [ui_knowledge_choice, ui_chatbot, state_chat_session_key],
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

    def on_tab_selected():
        choices = [("All documents", "all")]
        choices.extend(
            [
                (embedding.title, embedding.key)
                for embedding in EmbeddingsService.get_embedded_documents()
            ]
        )
        udated_dd = gr.update(choices=choices)

        return udated_dd

    main_tab.select(
        on_tab_selected,
        inputs=None,
        outputs=ui_knowledge_choice,
    )

    return ui_prompt_dropdown
