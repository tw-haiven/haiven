# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from shared.llm_config import LLMConfig
from shared.prompts_factory import PromptsFactory
from shared.chats import Q_A_Chat, ServerChatSessionMemory
from shared.knowledge import KnowledgeBaseMarkdown
from shared.models.chat_context import ChatContext
from shared.user_feedback import UserFeedback


def enable_brainstorming(
    knowledge_base: KnowledgeBaseMarkdown,
    CHAT_SESSION_MEMORY: ServerChatSessionMemory,
    prompts_factory: PromptsFactory,
    llm_config: LLMConfig,
    user_identifier_state: gr.State,
    prompt_categories=None,
):
    tab_id = "brainstorming"
    prompt_list = prompts_factory.create_brainstorming_prompt(knowledge_base)
    interaction_pattern_name = prompt_list.interaction_pattern_name

    chat_context = ChatContext(
        tab_id=tab_id,
        interaction_pattern=prompt_categories[0],
        model="",
        temperature=0.2,
        prompt="",
        message="",
    )

    prompt_list.filter(prompt_categories)

    def on_change_prompt_choice(prompt_choice: str, user_input: str) -> dict:
        chat_context.prompt = prompt_list.get(prompt_choice).metadata.get(
            "title", "Unnamed use case"
        )
        help, knowledge = prompt_list.render_help_markdown(prompt_choice)
        return {
            ui_prompt: prompt_list.render_prompt(prompt_choice, user_input),
            ui_help: help,
            ui_help_knowledge: knowledge,
        }

    with gr.Tab(interaction_pattern_name, id=tab_id):
        with gr.Row():
            gr.Markdown(
                "This 'question and answer' pattern currently does not work with all models yet. The GPTs should work."
            )

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
                    ui_user_input = gr.Textbox(label="User input", lines=5)

                with gr.Group(elem_classes="teamai-group"):
                    gr.Markdown(
                        "## 2. Start the chat", elem_classes="teamai-group-title"
                    )
                    ui_start_btn = gr.Button("Start >>", variant="primary")
                    with gr.Accordion(label="View or change the prompt", open=False):
                        ui_prompt = gr.Textbox(
                            label="Prompt",
                            lines=10,
                            info="Will be composed from your inputs above",
                        )

            with gr.Column(scale=5):
                with gr.Group(elem_classes="teamai-group"):
                    gr.Markdown("## 3. Chat", elem_classes="teamai-group-title")
                    ui_chatbot = gr.Chatbot(
                        label="Assistant",
                        height=600,
                        show_copy_button=True,
                        show_label=False,
                        likeable=True,
                    )
                    ui_message = gr.Textbox(label="Message (hit Enter to send)")

        ui_prompt_dropdown.change(
            fn=on_change_prompt_choice,
            inputs=[ui_prompt_dropdown, ui_user_input],
            outputs=[ui_prompt, ui_help, ui_help_knowledge],
        )
        ui_user_input.change(
            fn=prompt_list.render_prompt,
            inputs=[ui_prompt_dropdown, ui_user_input],
            outputs=ui_prompt,
        )

        def start(prompt_choice: str, prompt_text: str, user_identifier_state: str):
            system_message = prompt_list.get(prompt_choice).metadata["system"]

            chat_session_key_value, chat_session = (
                CHAT_SESSION_MEMORY.get_or_create_chat(
                    lambda: Q_A_Chat(
                        llm_config=llm_config, system_message=system_message
                    ),
                    None,
                    "brainstorming",
                    user_identifier_state,
                )
            )

            response = chat_session.start_with_prompt(prompt_text)
            chat_history = [[system_message + "\n" + prompt_text, response]]

            return {
                ui_message: "",
                ui_chatbot: chat_history,
                state_chat_session_key: chat_session_key_value,
            }

        def chat(message_value: str, chat_history, chat_session_key_value: str):
            chat_session = CHAT_SESSION_MEMORY.get_chat(chat_session_key_value)

            response = chat_session.next(message_value)
            chat_history.append((message_value, response))

            return {ui_message: "", ui_chatbot: chat_history}

        state_chat_session_key = gr.State()

        ui_start_btn.click(
            start,
            [ui_prompt_dropdown, ui_prompt, user_identifier_state],
            [ui_message, ui_chatbot, state_chat_session_key],
            scroll_to_output=True,
        )
        ui_message.submit(
            chat,
            [ui_message, ui_chatbot, state_chat_session_key],
            [ui_message, ui_chatbot],
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
