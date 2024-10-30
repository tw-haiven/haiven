# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import gradio as gr
from pydantic import BaseModel

from llms.chats import ChatManager, StreamingChat
from llms.model_config import ModelConfig


class ChatOptions(BaseModel):
    category: str = None
    stop: str = None
    in_chunks: bool = False
    user_identifier: str = None


# Wrapper for the StreamingChat, because the Gradio chat component needs the chat_history as return value
class UIStreamingChatWrapper:
    @staticmethod
    def start_with_prompt(
        chat_client: StreamingChat,
        prompt: str,
        initial_display_message: str = "Let's get started!",
    ):
        chat_history = [[initial_display_message, ""]]
        for chunk in chat_client.run(prompt):
            chat_history[-1][1] += chunk
            yield chat_history


class PromptsTestingUI:
    def __init__(self, chat_manager: ChatManager):
        self.chat_manager = chat_manager
        self.chat_client_config = ModelConfig("azure-gpt35", "azure", "GPT3.5 on Azure")

    def create_gradio_ui(self):
        def send_prompt(prompt_text):
            # self.chat_manager.send_prompt(prompt_text)

            _, chat_client = self.chat_manager.streaming_chat(
                client_config=self.chat_client_config,
                session_id=None,
                options=ChatOptions(category="chat"),
            )

            for chat_history_chunk in UIStreamingChatWrapper.start_with_prompt(
                chat_client, prompt_text
            ):
                yield chat_history_chunk

        def create_column():
            with gr.Column():
                input_prompt = gr.Textbox(label="Prompt", lines=20)
                btn_send = gr.Button("Submit")
                chat_result = gr.Chatbot(label="Result", height=1000)

                btn_send.click(send_prompt, inputs=input_prompt, outputs=chat_result)

        blocks = gr.Blocks(title="Haiven")
        with blocks:
            with gr.Row():
                gr.Markdown(f"""
                            ## Prompt testing
                            
                            This is a little test space to compare different prompt versions and their results
                            
                            Activated model: {self.chat_client_config.name}
                            
                            """)

            with gr.Row():
                create_column()
                create_column()
                create_column()

        return blocks
