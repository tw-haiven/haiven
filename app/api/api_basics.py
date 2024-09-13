# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import io
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import File, Form, UploadFile
from PIL import Image

from pydantic import BaseModel
from embeddings.documents import KnowledgeDocument
from knowledge_manager import KnowledgeManager
from llms.chats import ChatManager, ChatOptions, StreamingChat
from llms.clients import ChatClientConfig
from llms.image_description_service import ImageDescriptionService
from llms.model import Model
from prompts.prompts import PromptList


class PromptRequestBody(BaseModel):
    userinput: str = None
    promptid: str = None
    chatSessionId: str = None
    context: str = None
    document: str = None


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

    def stream_json_chat(
        self,
        user_input,
        prompt,
        chat_category,
        chat_session_key_value=None,
        document_key=None,
    ):
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

    def stream_text_chat(
        self,
        user_input,
        prompt,
        chat_category,
        chat_session_key_value=None,
        document_key=None,
    ):
        def stream(chat_session: StreamingChat, prompt):
            if document_key:
                sources = ""
                for chunk, sources in chat_session.run_with_document(
                    document_key, None, prompt, user_input
                ):
                    sources = sources if sources else ""
                    yield chunk
                yield "\n\n" + sources
            else:
                for chunk in chat_session.run(prompt):
                    yield chunk

        chat_session_key_value, chat_session = self.chat_manager.streaming_chat(
            client_config=ChatClientConfig(self.model_key, 0.5),
            session_id=chat_session_key_value,
            options=ChatOptions(in_chunks=True, category=chat_category),
        )

        return StreamingResponse(
            stream(chat_session, prompt),
            media_type=streaming_media_type(),
            headers=streaming_headers(chat_session_key_value),
        )


class ApiBasics(HaivenBaseApi):
    def __init__(
        self,
        app: FastAPI,
        chat_manager: ChatManager,
        model_key: str,
        prompts_guided: PromptList,
        knowledge_manager: KnowledgeManager,
        prompts_chat: PromptList,
        image_service: ImageDescriptionService,
    ):
        super().__init__(app, chat_manager, model_key, prompts_guided)

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
            all_contexts = knowledge_manager.get_all_context_keys()

            response_data = []
            for context in all_contexts:
                snippets = knowledge_manager.knowledge_base_markdown.get_knowledge_content_dict(
                    context
                )
                response_data.append({"context": context, "snippets": snippets})

            response_data.sort(key=lambda x: x["context"])

            return JSONResponse(response_data)

        @app.get("/api/knowledge/documents")
        def get_knowledge_documents(request: Request):
            base_context = None
            all_contexts = knowledge_manager.get_all_context_keys()

            all_contexts.append(base_context)
            response_data = []
            for context in all_contexts:
                documents: List[KnowledgeDocument] = (
                    knowledge_manager.knowledge_base_documents.get_documents(
                        context=context, include_base_context=False
                    )
                )

                for document in documents:
                    response_data.append(
                        {
                            "key": document.key,
                            "title": document.title,
                            "description": document.description,
                            "source": document.get_source_title_link(),
                        }
                    )

            return JSONResponse(response_data)

        @app.post("/api/prompt")
        def chat(prompt_data: PromptRequestBody):
            stream_fn = self.stream_text_chat
            if prompt_data.promptid:
                prompts = (
                    prompts_guided
                    if prompt_data.promptid.startswith("guided-")
                    else prompts_chat
                )
                rendered_prompt, _ = prompts.render_prompt(
                    active_knowledge_context=prompt_data.context,
                    prompt_choice=prompt_data.promptid,
                    user_input=prompt_data.userinput,
                    additional_vars={},
                    warnings=[],
                )
                if prompt_data.promptid.startswith("guided-"):
                    stream_fn = self.stream_json_chat
            else:
                rendered_prompt = prompt_data.userinput

            return stream_fn(
                user_input=prompt_data.userinput,
                prompt=rendered_prompt,
                chat_category="boba-chat",
                chat_session_key_value=prompt_data.chatSessionId,
                document_key=prompt_data.document,
            )

        @app.post("/api/prompt/render")
        def render_prompt(prompt_data: PromptRequestBody):
            if prompt_data.promptid:
                prompts = (
                    prompts_guided
                    if prompt_data.promptid.startswith("guided-")
                    else prompts_chat
                )

                rendered_prompt, template = prompts.render_prompt(
                    active_knowledge_context=prompt_data.context,
                    prompt_choice=prompt_data.promptid,
                    user_input=prompt_data.userinput,
                    additional_vars={},
                    warnings=[],
                )
                return JSONResponse(
                    {"prompt": rendered_prompt, "template": template.template}
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Server error: promptid is required"
                )

        @app.post("/api/prompt/image")
        async def describe_image(prompt: str = Form(...), file: UploadFile = File(...)):
            def chat_with_yield(image, prompt):
                for chunk in image_service.prompt_with_image(image, prompt):
                    yield chunk

            contents = await file.read()
            image = Image.open(io.BytesIO(contents))

            return StreamingResponse(
                chat_with_yield(image, prompt),
                media_type=streaming_media_type(),
                headers=streaming_headers(None),
            )
