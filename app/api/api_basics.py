# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import io
import os
from typing import List, Optional
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
from prompts.inspirations import InspirationsManager

from config_service import ConfigService
from disclaimer_and_guidelines import DisclaimerAndGuidelinesService
from logger import HaivenLogger
from loguru import logger
import hashlib
import json


class PromptRequestBody(BaseModel):
    userinput: Optional[str] = None
    promptid: Optional[str] = None
    chatSessionId: Optional[str] = None
    contexts: Optional[List[str]] = None
    document: Optional[List[str]] = None
    json: bool = False
    userContext: Optional[str] = None


class IterateRequest(PromptRequestBody):
    scenarios: str
    contexts: Optional[List[str]] = None
    user_context: Optional[str] = None


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

    def _is_api_key_auth(self, request):
        """Check if the request is using API key authentication."""
        if request.session and request.session.get("user"):
            user = request.session.get("user")
            return user.get("auth_type") == "api_key"
        return False

    def _get_request_source(self, request):
        """Get the source of the request (mcp, ui, or unknown)."""
        # Check if auth is switched off
        if os.environ.get("AUTH_SWITCHED_OFF") == "true":
            return "unknown"

        # Check if it's an API key auth (MCP)
        if self._is_api_key_auth(request):
            return "mcp"

        # Default to UI
        return "ui"

    def get_hashed_user_id(self, request):
        if request.session and request.session.get("user"):
            user = request.session.get("user")
            # Check if auth_type is api_key, if so use user_id directly from the session
            if user.get("auth_type") == "api_key":
                user_id = user.get("user_id")
            else:
                user_id = user.get("email")

            if user_id is not None:
                hashed_user_id = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
                return hashed_user_id
        return None

    def stream_json_chat(
        self,
        prompt,
        chat_category,
        chat_session_key_value=None,
        document_keys=None,
        prompt_id=None,
        user_identifier=None,
        contexts=None,
        origin_url=None,
        model_config=None,
        userContext=None,
    ):
        """Stream JSON chat with simplified event handling"""
        try:

            def stream_with_events(chat_session, prompt):
                try:
                    # Pass through the formatted events from the chat session (original behavior)
                    for event_str in chat_session.run(prompt):
                        # Ensure we're yielding strings, not dicts
                        if isinstance(event_str, dict):
                            yield json.dumps(event_str)
                        else:
                            yield str(event_str)

                except Exception as error:
                    error_msg = (
                        str(error).strip()
                        or "Error while the model was processing the input"
                    )
                    print(f"[ERROR]: {error_msg}")
                    # Send error in JSON format for JSON chat
                    error_response = {"data": f"[ERROR]: {error_msg}"}
                    yield json.dumps(error_response)

            chat_session_key_value, chat_session = self.chat_manager.json_chat(
                model_config=model_config or self.model_config,
                session_id=chat_session_key_value,
                options=ChatOptions(in_chunks=True, category=chat_category),
                contexts=contexts or [],
                user_context=userContext,
            )

            self.log_run(
                chat_session,
                origin_url,
                user_identifier,
                chat_session_key_value,
                prompt_id,
                contexts,
                userContext,
            )

            return StreamingResponse(
                stream_with_events(chat_session, prompt),
                media_type=streaming_media_type(),
                headers=streaming_headers(chat_session_key_value),
            )

        except Exception as error:
            raise Exception(error)

    def log_run(
        self,
        chat_session,
        origin_url,
        user_identifier,
        chat_session_key_value,
        prompt_id,
        context,
        userContext,
    ):
        return chat_session.log_run(
            {
                "url": origin_url,
                "user_id": user_identifier,
                "session": chat_session_key_value,
                "prompt_id": prompt_id,
                "context": ",".join(context or []),
                "is_user_context_included": True if userContext else False,
            }
        )

    def stream_text_chat(
        self,
        prompt,
        chat_category,
        chat_session_key_value=None,
        document_keys=[],
        prompt_id=None,
        user_identifier=None,
        contexts=None,
        origin_url=None,
        userContext=None,
        model_config=None,
    ):
        """Stream text chat with simplified event handling"""
        try:

            def stream_with_events(chat_session: StreamingChat, prompt):
                try:
                    if document_keys:
                        # Handle document-based streaming
                        for (
                            event_str,
                            sources_markdown,
                        ) in chat_session.run_with_document(document_keys, prompt):
                            # Ensure we're yielding strings, not dicts
                            if isinstance(event_str, dict):
                                yield json.dumps(event_str)
                            else:
                                yield str(event_str)
                    else:
                        # Handle regular streaming
                        for event_str in chat_session.run(prompt):
                            # Ensure we're yielding strings, not dicts
                            if isinstance(event_str, dict):
                                yield json.dumps(event_str)
                            else:
                                yield str(event_str)

                except Exception as error:
                    error_msg = (
                        str(error).strip()
                        or "Error while the model was processing the input"
                    )
                    print(f"[ERROR]: {error_msg}")
                    yield f"[ERROR]: {error_msg}"

            chat_session_key_value, chat_session = self.chat_manager.streaming_chat(
                model_config=model_config or self.model_config,
                session_id=chat_session_key_value,
                options=ChatOptions(in_chunks=True, category=chat_category),
                contexts=contexts or [],
                user_context=userContext,
            )

            self.log_run(
                chat_session,
                origin_url,
                user_identifier,
                chat_session_key_value,
                prompt_id,
                contexts,
                userContext,
            )

            return StreamingResponse(
                stream_with_events(chat_session, prompt),
                media_type=streaming_media_type(),
                headers=streaming_headers(chat_session_key_value),
            )

        except Exception as error:
            raise Exception(error)


class ApiBasics(HaivenBaseApi):
    def __init__(
        self,
        app: FastAPI,
        chat_manager: ChatManager,
        model_config: ModelConfig,
        prompts_guided: PromptList,
        knowledge_manager: KnowledgeManager,
        prompts_chat: PromptList,
        image_service: ImageDescriptionService,
        config_service: ConfigService,
        disclaimer_and_guidelines: DisclaimerAndGuidelinesService,
        inspirations_manager: InspirationsManager,
    ):
        super().__init__(app, chat_manager, model_config, prompts_guided)
        self.knowledge_manager = knowledge_manager
        self.prompts_chat = prompts_chat
        self.image_service = image_service
        self.config_service = config_service
        self.disclaimer_and_guidelines = disclaimer_and_guidelines
        self.inspirations_manager = inspirations_manager

        @app.get("/api/models")
        @logger.catch(reraise=True)
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

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/prompts")
        @logger.catch(reraise=True)
        def get_prompts(request: Request):
            try:
                response_data = prompts_chat.get_prompts_with_follow_ups()
                return JSONResponse(response_data)

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/disclaimer-guidelines")
        @logger.catch(reraise=True)
        def get_disclaimer_and_guidelines(request: Request):
            try:
                if not disclaimer_and_guidelines.is_enabled:
                    return JSONResponse({"enabled": False, "title": "", "content": ""})

                response_data = json.loads(
                    disclaimer_and_guidelines.fetch_disclaimer_and_guidelines()
                )
                response_data["enabled"] = True
                return JSONResponse(response_data)

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/knowledge/snippets")
        @logger.catch(reraise=True)
        def get_knowledge_snippets(request: Request):
            try:
                all_contexts = (
                    knowledge_manager.knowledge_base_markdown.get_all_contexts()
                )
                response_data = []
                for key, context_info in all_contexts.items():
                    response_data.append(
                        {
                            "context": key,
                            "title": context_info.metadata.get("title", key),
                            "snippets": {"context": context_info.content},
                        }
                    )

                response_data.sort(key=lambda x: x["context"])

                return JSONResponse(response_data)

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/knowledge/documents")
        @logger.catch(reraise=True)
        def get_knowledge_documents(request: Request):
            try:
                response_data = []
                documents: List[KnowledgeDocument] = (
                    knowledge_manager.knowledge_base_documents.get_documents()
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

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.post("/api/prompt")
        @logger.catch(reraise=True)
        def chat(request: Request, prompt_data: PromptRequestBody):
            origin_url = request.headers.get("referer")
            try:
                stream_fn = self.stream_text_chat
                if prompt_data.promptid:
                    prompts = (
                        prompts_guided
                        if prompt_data.promptid.startswith("guided-")
                        else prompts_chat
                    )
                    rendered_prompt, _ = prompts.render_prompt(
                        prompt_choice=prompt_data.promptid,
                        user_input=prompt_data.userinput,
                    )
                    if prompts.produces_json_output(prompt_data.promptid):
                        stream_fn = self.stream_json_chat
                else:
                    rendered_prompt = prompt_data.userinput

                if prompt_data.json is True:
                    stream_fn = self.stream_json_chat

                selected_model_config = self.model_config
                if prompt_data.promptid:
                    prompt_obj = prompts.get(prompt_data.promptid)
                    if prompt_obj and prompt_obj.metadata.get("grounded", True):
                        perplexity_model_config = ModelConfig(
                            "perplexity", "perplexity", "Perplexity"
                        )
                        selected_model_config = perplexity_model_config

                prompt = rendered_prompt
                session_id = prompt_data.chatSessionId
                document = prompt_data.document
                promptid = prompt_data.promptid
                user_id = self.get_hashed_user_id(request)
                contexts = prompt_data.contexts
                data = prompt_data
                return stream_fn(
                    prompt=prompt,
                    model_config=selected_model_config,
                    chat_category="boba-chat",
                    chat_session_key_value=session_id,
                    document_keys=document,
                    prompt_id=promptid,
                    user_identifier=user_id,
                    contexts=contexts,
                    userContext=data.userContext,
                    origin_url=origin_url,
                )

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.post("/api/prompt/iterate")
        def iterate(prompt_data: IterateRequest):
            try:
                if prompt_data.chatSessionId is None or prompt_data.chatSessionId == "":
                    raise HTTPException(
                        status_code=400, detail="chatSessionId is required"
                    )
                stream_fn = self.stream_json_chat

                rendered_prompt = (
                    f"""

                    My new request:
                    {prompt_data.userinput}
                    """
                    + """
                    ### Output format: JSON with at least the "id" property repeated
                    Here is my current working state of the data, iterate on those objects based on that request,
                    and only return your new list of the objects in JSON format, nothing else.
                    Be sure to repeat back to me the JSON that I already have, and only update it with my new request.
                    Definitely repeat back to me the "id" property, so I can track your changes back to my original data.
                    For example, if I give you
                    [ { "title": "Paris", "id": 1 }, { "title": "London", "id": 2 } ]
                    and ask you to add information about what you know about each of these cities, then return to me
                    [ { "summary": "capital of France", "id": 1 }, { "summary": "Capital of the UK", "id": 2 } ]
"""
                    + f"""
                    ### Current JSON data
                    {prompt_data.scenarios}
                    Please iterate on this data based on my request. Apply my request to ALL of the objects.
                """
                )

                return stream_fn(
                    prompt=rendered_prompt,
                    chat_category="boba-chat",
                    chat_session_key_value=prompt_data.chatSessionId,
                    contexts=prompt_data.contexts,
                    userContext=prompt_data.user_context,
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @app.post("/api/prompt/render")
        @logger.catch(reraise=True)
        def render_prompt(prompt_data: PromptRequestBody):
            if prompt_data.promptid:
                prompts = (
                    prompts_guided
                    if prompt_data.promptid.startswith("guided-")
                    else prompts_chat
                )

                rendered_prompt, template = prompts.render_prompt(
                    prompt_choice=prompt_data.promptid,
                    user_input=prompt_data.userinput,
                )
                return JSONResponse(
                    {"prompt": rendered_prompt, "template": template.template}
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Server error: promptid is required"
                )

        @app.post("/api/prompt/image")
        @logger.catch(reraise=True)
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
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/inspirations")
        @logger.catch(reraise=True)
        def get_inspirations(request: Request):
            try:
                return JSONResponse(self.inspirations_manager.get_inspirations())
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/inspirations/{inspiration_id}")
        @logger.catch(reraise=True)
        def get_inspiration_by_id(request: Request, inspiration_id: str):
            try:
                inspiration = self.inspirations_manager.get_inspiration_by_id(
                    inspiration_id
                )
                if inspiration is None:
                    raise HTTPException(status_code=404, detail="Inspiration not found")
                return JSONResponse(inspiration)
            except HTTPException:
                raise
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/download-prompt")
        @logger.catch(reraise=True)
        def download_prompt(
            request: Request, prompt_id: str = None, category: str = None
        ):
            import re

            def is_valid_param(val):
                return bool(val) and re.match(r"^[a-zA-Z0-9_-]{1,100}$", val)

            user_id = self.get_hashed_user_id(request)
            source = self._get_request_source(request)

            try:
                if prompt_id is not None:
                    if not is_valid_param(prompt_id):
                        raise HTTPException(status_code=400, detail="Invalid prompt_id")
                    prompt = prompts_chat.get_a_prompt_with_follow_ups(
                        prompt_id, download_prompt=True
                    )

                    if not prompt:
                        raise Exception("Prompt not found")

                    # Check if prompt is download restricted
                    if prompt.get("download_restricted", False):
                        HaivenLogger.get().analytics(
                            "Download restricted prompt attempted",
                            {
                                "user_id": user_id,
                                "prompt_id": prompt_id,
                                "category": "Individual Prompt",
                                "source": source,
                            },
                        )
                        raise HTTPException(
                            status_code=403,
                            detail="This prompt is not available for download",
                        )

                    HaivenLogger.get().analytics(
                        "Download prompt",
                        {
                            "user_id": user_id,
                            "prompt_id": prompt_id,
                            "category": "Individual Prompt",
                            "source": source,
                        },
                    )

                    return JSONResponse([prompt])
                elif category and category.strip():
                    if not is_valid_param(category):
                        raise HTTPException(status_code=400, detail="Invalid category")

                    prompts = prompts_chat.get_prompts_with_follow_ups(
                        download_prompt=True, category=category
                    )

                    # Filter out restricted prompts
                    from prompts.prompts import filter_downloadable_prompts

                    downloadable_prompts = filter_downloadable_prompts(prompts)

                    for prompt in downloadable_prompts:
                        HaivenLogger.get().analytics(
                            "Download prompt",
                            {
                                "user_id": user_id,
                                "prompt_id": prompt.get("identifier"),
                                "category": category,
                                "source": source,
                            },
                        )

                    return JSONResponse(downloadable_prompts)
                else:
                    # Return all prompts if no prompt_id and no category provided (or empty category)
                    prompts = prompts_chat.get_prompts_with_follow_ups(
                        download_prompt=True
                    )

                    # Filter out restricted prompts
                    from prompts.prompts import filter_downloadable_prompts

                    downloadable_prompts = filter_downloadable_prompts(prompts)

                    for prompt in downloadable_prompts:
                        HaivenLogger.get().analytics(
                            "Download prompt",
                            {
                                "user_id": user_id,
                                "prompt_id": prompt.get("identifier"),
                                "category": "all",
                                "source": source,
                            },
                        )

                    return JSONResponse(downloadable_prompts)
            except HTTPException:
                raise
            except Exception as error:
                HaivenLogger.get().error(
                    str(error),
                    extra={
                        "ERROR": "Downloading prompts failed",
                        "user_id": user_id,
                        "prompt_id": prompt_id,
                        "category": category,
                        "source": source,
                    },
                )
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )
