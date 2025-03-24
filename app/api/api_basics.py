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
from prompts.inspirations import InspirationsManager

from config_service import ConfigService
from disclaimer_and_guidelines import DisclaimerAndGuidelinesService
from logger import HaivenLogger
from loguru import logger
import hashlib
import json


class PromptRequestBody(BaseModel):
    userinput: str = None
    promptid: str = None
    chatSessionId: str = None
    context: str = None
    document: str = None
    json: bool = False
    userContext: str = None


class IterateRequest(PromptRequestBody):
    scenarios: str


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

    def get_hashed_user_id(self, request):
        if request.session and request.session.get("user"):
            user_id = request.session.get("user").get("email")
            hashed_user_id = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
            return hashed_user_id
        else:
            return None

    def stream_json_chat(
        self,
        prompt,
        chat_category,
        chat_session_key_value=None,
        document_key=None,
        prompt_id=None,
        user_identifier=None,
        context=None,
        origin_url=None,
        model_config=None,
    ):
        try:
            chat_session_key_value, chat_session = self.chat_manager.json_chat(
                model_config=model_config or self.model_config,
                session_id=chat_session_key_value,
                options=ChatOptions(category=chat_category),
            )

            chat_session.log_run(
                {
                    "url": origin_url,
                    "user_id": user_identifier,
                    "session": chat_session_key_value,
                    "prompt_id": prompt_id,
                    "context": context,
                }
            )

            return StreamingResponse(
                chat_session.run(prompt),
                media_type=streaming_media_type(),
                headers=streaming_headers(chat_session_key_value),
            )

        except Exception as error:
            raise Exception(error)

    def stream_text_chat(
        self,
        prompt,
        chat_category,
        chat_session_key_value=None,
        document_key=None,
        prompt_id=None,
        user_identifier=None,
        context=None,
        origin_url=None,
    ):
        try:

            def stream(chat_session: StreamingChat, prompt):
                try:
                    if document_key:
                        sources = ""
                        for chunk, sources in chat_session.run_with_document(
                            document_key, prompt
                        ):
                            sources = sources
                            yield chunk
                        yield "\n\n" + sources if sources else ""
                    else:
                        for chunk in chat_session.run(prompt):
                            yield chunk
                except Exception as error:
                    if not str(error).strip():
                        error = "Error while the model was processing the input"
                    print(f"[ERROR]: {str(error)}")
                    yield f"[ERROR]: {str(error)}"

            chat_session_key_value, chat_session = self.chat_manager.streaming_chat(
                model_config=self.model_config,
                session_id=chat_session_key_value,
                options=ChatOptions(in_chunks=True, category=chat_category),
            )

            chat_session.log_run(
                {
                    "url": origin_url,
                    "user_id": user_identifier,
                    "session": chat_session_key_value,
                    "prompt_id": prompt_id,
                    "context": context,
                }
            )

            return StreamingResponse(
                stream(chat_session, prompt),
                media_type=streaming_media_type(),
                headers=streaming_headers(chat_session_key_value),
            )

        except Exception as error:
            raise Exception(error)


def contextNameForLogging(prompt_data):
    if prompt_data.userContext:
        return "User context: " + prompt_data.userContext
    else:
        return prompt_data.context


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
                all_contexts = knowledge_manager.get_all_context_keys()
                response_data = []
                for context_info in all_contexts:
                    snippets = knowledge_manager.knowledge_base_markdown.get_knowledge_content_dict(
                        context_info["context"]
                    )
                    response_data.append(
                        {
                            "context": context_info["context"],
                            "title": context_info["title"],
                            "snippets": snippets,
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
                        active_knowledge_context=prompt_data.context,
                        prompt_choice=prompt_data.promptid,
                        user_input=prompt_data.userinput,
                        additional_vars={},
                        warnings=[],
                        user_context=prompt_data.userContext,
                    )
                    if prompts.produces_json_output(prompt_data.promptid):
                        stream_fn = self.stream_json_chat
                else:
                    rendered_prompt = prompt_data.userinput

                if prompt_data.json is True:
                    stream_fn = self.stream_json_chat

                return stream_fn(
                    prompt=rendered_prompt,
                    chat_category="boba-chat",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_key=prompt_data.document,
                    prompt_id=prompt_data.promptid,
                    user_identifier=self.get_hashed_user_id(request),
                    context=contextNameForLogging(prompt_data),
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
                    active_knowledge_context=prompt_data.context,
                    prompt_choice=prompt_data.promptid,
                    user_input=prompt_data.userinput,
                    additional_vars={},
                    warnings=[],
                    user_context=prompt_data.userContext,
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
