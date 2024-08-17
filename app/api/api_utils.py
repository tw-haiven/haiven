# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi.responses import StreamingResponse
from llms.chats import JSONChat, StreamingChat
from llms.llm_config import LLMConfig


def streaming_media_type() -> str:
    return "text/event-stream"


def streaming_headers(chat_session_key_value=None):
    return {
        "Connection": "keep-alive",
        "Content-Encoding": "none",
        "Access-Control-Expose-Headers": "X-Chat-ID",
        "X-Chat-ID": chat_session_key_value,
    }


class HaivenBaseApi:
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        self.app = app
        self.chat_session_memory = chat_session_memory
        self.model_key = model_key
        self.prompt_list = prompt_list

    def stream_json_chat(self, prompt, chat_category, chat_session_key_value=None):
        chat_session_key_value, chat_session = (
            self.chat_session_memory.get_or_create_chat(
                lambda: JSONChat(
                    llm_config=LLMConfig(self.model_key, 0.5),
                    event_stream_standard=False,
                ),
                chat_session_key_value=chat_session_key_value,
                chat_category=chat_category,
                # TODO: Pass user identifier from session
            )
        )

        return StreamingResponse(
            chat_session.run(prompt),
            media_type=streaming_media_type(),
            headers=streaming_headers(chat_session_key_value),
        )

    def stream_text_chat(self, prompt, chat_category, chat_session_key_value=None):
        def chat_with_yield(chat_session, prompt):
            for chunk in chat_session.start_with_prompt(prompt):
                yield chunk

        chat_session_key_value, chat_session = (
            self.chat_session_memory.get_or_create_chat(
                lambda: StreamingChat(
                    llm_config=LLMConfig(self.model_key, 0.5), stream_in_chunks=True
                ),
                chat_session_key_value=chat_session_key_value,
                chat_category=chat_category,
                # TODO: Pass user identifier from session
            )
        )

        return StreamingResponse(
            chat_with_yield(chat_session, prompt),
            media_type=streaming_media_type(),
            headers=streaming_headers(chat_session_key_value),
        )
