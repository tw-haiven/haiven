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
from llms.model_config import ModelConfig
from llms.image_description_service import ImageDescriptionService
from prompts.prompts import PromptList
from config_service import ConfigService


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
        self,
        app,
        chat_manager: ChatManager,
        model_config: ModelConfig,
        prompt_list: PromptList,
    ):
        self.chat_manager = chat_manager
        self.model_config = model_config
        self.prompt_list = prompt_list

    def stream_json_chat(
        self, prompt, chat_category, chat_session_key_value=None, document_key=None
    ):
        try:
            chat_session_key_value, chat_session = self.chat_manager.json_chat(
                client_config=self.model_config,
                session_id=chat_session_key_value,
                options=ChatOptions(category=chat_category),
            )

            return StreamingResponse(
                chat_session.run(prompt),
                media_type=streaming_media_type(),
                headers=streaming_headers(chat_session_key_value),
            )

        except Exception as e:
            raise Exception(e)

    def stream_text_chat(
        self, prompt, chat_category, chat_session_key_value=None, document_key=None
    ):
        try:

            def stream(chat_session: StreamingChat, prompt):
                try:
                    if document_key:
                        sources = ""
                        for chunk, sources in chat_session.run_with_document(
                            document_key, None, prompt
                        ):
                            sources = sources
                            yield chunk
                        yield "\n\n" + sources
                    else:
                        for chunk in chat_session.run(prompt):
                            yield chunk
                except Exception as error:
                    if not str(error).strip():
                        error = "Error while the model was processing the input"
                    yield f"[ERROR]: {str(error)}"

            chat_session_key_value, chat_session = self.chat_manager.streaming_chat(
                client_config=self.model_config,
                session_id=chat_session_key_value,
                options=ChatOptions(in_chunks=True, category=chat_category),
            )

            return StreamingResponse(
                stream(chat_session, prompt),
                media_type=streaming_media_type(),
                headers=streaming_headers(chat_session_key_value),
            )

        except Exception as e:
            raise Exception(e)


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
        config_service: ConfigService,
    ):
        super().__init__(app, chat_manager, model_key, prompts_guided)

        @app.get("/api/models")
        def get_models(request: Request):
            try:
                embeddings = config_service.load_embedding_model()
                vision = config_service.get_image_model()
                chat = config_service.get_chat_model()
                return JSONResponse(
                    {
                        "chat": {
                            "id": chat.id,
                            "name": chat.name,
                        },
                        "vision": {
                            "id": vision.id,
                            "name": vision.name,
                        },
                        "embeddings": {
                            "id": embeddings.id,
                            "name": embeddings.name,
                        },
                    }
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @app.get("/api/prompts")
        def get_prompts(request: Request):
            try:
                response_data = [entry.metadata for entry in prompts_chat.prompts]
                return JSONResponse(response_data)

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @app.get("/api/knowledge/snippets")
        def get_knowledge_snippets(request: Request):
            try:
                all_contexts = knowledge_manager.get_all_context_keys()

                response_data = []
                for context in all_contexts:
                    snippets = knowledge_manager.knowledge_base_markdown.get_knowledge_content_dict(
                        context
                    )
                    response_data.append({"context": context, "snippets": snippets})

                response_data.sort(key=lambda x: x["context"])

                return JSONResponse(response_data)

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @app.get("/api/knowledge/documents")
        def get_knowledge_documents(request: Request):
            try:
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

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @app.post("/api/prompt")
        def chat(prompt_data: PromptRequestBody):
            try:
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
                    prompt=rendered_prompt,
                    chat_category="boba-chat",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_key=prompt_data.document,
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

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
            try:

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
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
