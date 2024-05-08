# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr
from dotenv import load_dotenv
from shared.chats import ServerChatSessionMemory, StreamingChat
from shared.models.chat_context import ChatContext
from shared.ui import UI
from shared.user_feedback import UserFeedback


def enable_plain_chat(
    CHAT_SESSION_MEMORY: ServerChatSessionMemory, user_identifier_state: gr.State
):
    load_dotenv()
    ui = UI()

    chat_context = ChatContext(
        tab_id="chat",
        interaction_pattern="plain-chat",
        model="",
        temperature=0.2,
        prompt="None",
        message="",
    )

    with gr.Group(elem_classes="teamai-group"):
        with gr.Row():
            model_select, tone_radio, llm_config = ui.create_llm_settings_ui()
            model_select.change(fn=llm_config.change_model, inputs=model_select)
            tone_radio.change(fn=llm_config.change_temperature, inputs=tone_radio)

    with gr.Row():
        with gr.Column(scale=5):
            with gr.Group(elem_classes="teamai-group"):
                ui_chatbot = gr.Chatbot(
                    label="Chat conversation",
                    height=500,
                    show_copy_button=True,
                    show_label=False,
                    likeable=True,
                )
                with gr.Row():
                    with gr.Column(scale=9):
                        ui_message = gr.Textbox(
                            label="Message (hit Enter to send, Shift+Enter for line breaks)"
                        )
                    with gr.Column(scale=1):
                        ui_send_button = gr.Button("Send", variant="primary")
                ui_clear_button = gr.Button("Clear and start a new chat")

        with gr.Column(scale=1, elem_classes="user-help-col"):
            gr.Markdown("""
                        This is a plain chat interface to give some access to the models for experimentation.
                        [To see "Haiven proper", click here](/about).

                        !! If you change the model settings or temperature mid-chat, it will not take effect. To change them, you have to "Clear and start a new chat".
                        """)

    def clear(chat_session_key_value: str):
        CHAT_SESSION_MEMORY.delete_entry(chat_session_key_value)

        return {ui_message: "", ui_chatbot: [], state_chat_session_key: None}

    def chat(
        message_value: str, chat_history, chat_session_key_value, user_identifier_state
    ):
        chat_session_key_value, chat_session = CHAT_SESSION_MEMORY.get_or_create_chat(
            fn_create_chat=lambda: StreamingChat(llm_config=llm_config),
            chat_session_key_value=chat_session_key_value,
            chat_category="chat",
            user_identifier=user_identifier_state,
        )

        for chat_history_chunk in chat_session.next(message_value, chat_history):
            yield {
                ui_message: "",
                ui_chatbot: chat_history_chunk,
                state_chat_session_key: chat_session_key_value,
            }

    state_chat_session_key = gr.State()

    ui_message.submit(
        fn=chat,
        inputs=[ui_message, ui_chatbot, state_chat_session_key, user_identifier_state],
        outputs=[ui_message, ui_chatbot, state_chat_session_key],
        scroll_to_output=True,
    )
    ui_send_button.click(
        fn=chat,
        inputs=[ui_message, ui_chatbot, state_chat_session_key, user_identifier_state],
        outputs=[ui_message, ui_chatbot, state_chat_session_key],
        scroll_to_output=True,
    )
    ui_clear_button.click(
        fn=clear,
        inputs=[state_chat_session_key],
        outputs=[ui_chatbot, ui_message, state_chat_session_key],
        scroll_to_output=True,
    )
    model_select.change(
        fn=clear,
        inputs=[state_chat_session_key],
        outputs=[ui_chatbot, ui_message, state_chat_session_key],
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
