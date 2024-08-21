# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import io
from typing import List
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import File, Form, UploadFile
from PIL import Image

from pydantic import BaseModel
from llms.chats import ChatManager, ChatOptions
from llms.clients import ChatClientConfig
from llms.image_description_service import ImageDescriptionService
from llms.model import Model
from prompts.prompts import PromptList


class PromptRequestBody(BaseModel):
    promptid: str
    userinput: str
    chatSessionId: str = None
    context: str = None


def streaming_media_type() -> str:
    return "text/event-stream"


def streaming_headers(chat_session_key_value=None):
    headers = {
        "Connection": "keep-alive",
        "Content-Encoding": "none",
        "Access-Control-Expose-Headers": "X-Chat-ID",
    }
    if chat_session_key_value:
        headers["X-Chat-ID"] = chat_session_key_value

    return headers


class HaivenBaseApi:
    def __init__(
        self, app, chat_manager: ChatManager, model_key: str, prompt_list: PromptList
    ):
        self.chat_manager = chat_manager
        self.model_key = model_key
        self.prompt_list = prompt_list

    def stream_json_chat(self, prompt, chat_category, chat_session_key_value=None):
        chat_session_key_value, chat_session = self.chat_manager.json_chat(
            client_config=ChatClientConfig(self.model_key, 0.5),
            session_id=chat_session_key_value,
            options=ChatOptions(category=chat_category),
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

        chat_session_key_value, chat_session = self.chat_manager.streaming_chat(
            client_config=ChatClientConfig(self.model_key, 0.5),
            session_id=chat_session_key_value,
            options=ChatOptions(in_chunks=True, category=chat_category),
        )

        return StreamingResponse(
            chat_with_yield(chat_session, prompt),
            media_type=streaming_media_type(),
            headers=streaming_headers(chat_session_key_value),
        )


class ApiBasics(HaivenBaseApi):
    def __init__(
        self,
        app,
        chat_session_memory,
        model_key,
        prompts_guided,
        knowledge_manager,
        prompts_chat,
        image_service: ImageDescriptionService,
    ):
        super().__init__(app, chat_session_memory, model_key, prompts_guided)

        @app.get("/api/models")
        def get_models(request: Request):
            models: List[Model] = self.config_service.load_enabled_models()
            return JSONResponse(
                [{"id": model.id, "name": model.name} for model in models]
            )

        @app.get("/api/prompts")
        def get_prompts(request: Request):
            response_data = [entry.metadata for entry in prompts_chat.prompts]
            return JSONResponse(response_data)

        @app.get("/api/knowledge/snippets")
        def get_knowledge_snippets(request: Request):
            all_contexts = (
                knowledge_manager.knowledge_base_markdown.get_all_contexts_keys()
            )

            response_data = []
            for context in all_contexts:
                snippets = knowledge_manager.knowledge_base_markdown.get_knowledge_content_dict(
                    context
                )
                response_data.append({"context": context, "snippets": snippets})

            return JSONResponse(response_data)

        @app.post("/api/prompt")
        def chat(prompt_data: PromptRequestBody):
            rendered_prompt = prompts_chat.render_prompt(
                active_knowledge_context=prompt_data.context,
                prompt_choice=prompt_data.promptid,
                user_input=prompt_data.userinput,
                additional_vars={},
                warnings=[],
            )

            return self.stream_text_chat(
                rendered_prompt, "boba-chat", prompt_data.chatSessionId
            )

        @app.post("/api/prompt/image")
        async def describe_image(prompt: str = Form(...), file: UploadFile = File(...)):
            def chat_with_yield(image, prompt):
                for chunk in image_service.prompt_with_image(image, prompt, True):
                    yield chunk

            contents = await file.read()
            image = Image.open(io.BytesIO(contents))

            return StreamingResponse(
                chat_with_yield(image, prompt),
                media_type=streaming_media_type(),
                headers=streaming_headers(None),
            )
