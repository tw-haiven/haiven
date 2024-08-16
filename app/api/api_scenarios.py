# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import Request
from fastapi.responses import StreamingResponse
from api.api_utils import streaming_headers, streaming_media_type
from llms.chats import JSONChat, StreamingChat, ServerChatSessionMemory
from llms.llm_config import LLMConfig
from prompts.prompts import PromptList
from config_service import ConfigService
from api.models.explore_request import ExploreRequest


def explore_scenario_prompt(original_input, item, user_message):
    return f"""
    You are a prospector, I am exploring the following context:
    {original_input}

    ...and the following scenario:
    {item}

    You are able to give me a concise elaboration of the scenario described in the
    context, here is my request for exploration:

    {user_message}

    Please respond in 3-5 sentences.
    """


def enable_scenarios(
    app,
    chat_session_memory: ServerChatSessionMemory,
    model_key: str,
    prompt_list: PromptList,
):
    # TODO: Refactor this at some point, annoying that this is needed all over the place
    def chat_with_yield(chat_session, prompt):
        for chunk in chat_session.start_with_prompt(prompt):
            yield chunk

    @app.get("/api/make-scenario")
    def make_scenario(request: Request):
        variables = {
            "input": request.query_params.get("input", "productization of consulting"),
            "num_scenarios": request.query_params.get("num_scenarios", 5),
            "time_horizon": request.query_params.get("time_horizon", "5-year"),
            "optimism": request.query_params.get("optimism", "optimistic"),
            "realism": request.query_params.get("realism", "futuristic sci-fi"),
        }
        detailed = request.query_params.get("detail") == "true"

        prompt = prompt_list.render_prompt(
            active_knowledge_context=None,
            prompt_choice="guided-scenarios-detailed"
            if detailed
            else "guided-scenarios",
            user_input="",
            additional_vars=variables,
            warnings=[],
        )

        chat_session_key_value, chat_session = chat_session_memory.get_or_create_chat(
            lambda: JSONChat(
                llm_config=LLMConfig(
                    ConfigService.get_default_guided_mode_model(), 0.5
                ),
                event_stream_standard=False,
            ),
            None,
            "scenarios",
            # TODO: Pass user identifier from session
        )

        return StreamingResponse(
            chat_session.run(prompt),
            media_type=streaming_media_type(),
            headers=streaming_headers(chat_session_key_value),
        )

    @app.post("/api/scenario/explore")
    def explore_scenario(explore_request: ExploreRequest):
        chat_session_key_value, chat_session = chat_session_memory.get_or_create_chat(
            lambda: StreamingChat(
                llm_config=LLMConfig(model_key, 0.5), stream_in_chunks=True
            ),
            explore_request.chatSessionId,
            "chat",
            # TODO: Pass user identifier from session
        )

        prompt = explore_request.userMessage
        if explore_request.chatSessionId is None:
            prompt = explore_scenario_prompt(
                explore_request.originalInput,
                explore_request.item,
                explore_request.userMessage,
            )

        return StreamingResponse(
            chat_with_yield(chat_session, prompt),
            media_type=streaming_media_type(),
            headers=streaming_headers(chat_session_key_value),
        )
