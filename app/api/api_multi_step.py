# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi import HTTPException, Request
from pydantic import BaseModel
from api.api_basics import HaivenBaseApi, PromptRequestBody
from logger import HaivenLogger


class TitleContent(BaseModel):
    title: str = None
    content: str = None


class FollowUpPromptInput(BaseModel):
    input: str
    scenarios: List[TitleContent]


class FollowUpRequest(PromptRequestBody):
    previous_promptid: str = None
    scenarios: List[TitleContent] = []
    userContext: str = None


class ExploreRequest(PromptRequestBody):
    previous_promptid: str = None
    previous_framing: str = None
    item: str = None
    first_step_input: str = None


class ApiMultiStep(HaivenBaseApi):
    def _concat_scenarios(self, promptinput: FollowUpRequest):
        return [
            f"**{pair.title}**\n**REVISED BY ME:** {pair.content}"
            for pair in promptinput.scenarios
        ]

    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        # - Input for frontend: a list of promptIds - first step, multiple prompt options for next step?
        # - First step always returns cards, which are then editable in the UI
        # - Other steps always return text
        #       !! could that just be the break-out chat?!
        # 1. call POST api/prompt with the first prompt id to

        @app.post("/api/prompt/follow-up")
        def generate_follow_up(request: Request, prompt_data: FollowUpRequest):
            origin_url = request.headers.get("referer")

            try:
                stream_fn = self.stream_text_chat
                prompts = self.prompt_list

                user_input = prompt_data.userinput
                if prompt_data.previous_promptid is not None:
                    output_framing = prompts.get(
                        prompt_data.previous_promptid
                    ).metadata.get("output_framing", "")

                    user_input = f"""
                        {prompt_data.userinput}
                        
                        {output_framing}
                        {self._concat_scenarios(prompt_data)}
                    """

                rendered_prompt, _ = prompts.render_prompt(
                    active_knowledge_context=prompt_data.context,
                    prompt_choice=prompt_data.promptid,
                    user_input=user_input,
                    additional_vars={},
                    warnings=[],
                    user_context=prompt_data.userContext,
                )

                return stream_fn(
                    prompt=rendered_prompt,
                    chat_category="follow-up",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_key=prompt_data.document,
                    user_identifier=self.get_hashed_user_id(request),
                    origin_url=origin_url,
                )

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.post("/api/prompt/explore")
        def kick_off_explore(request: Request, prompt_data: ExploreRequest):
            origin_url = request.headers.get("referer")

            try:
                stream_fn = self.stream_text_chat
                prompts = self.prompt_list

                user_input = prompt_data.userinput
                if prompt_data.previous_promptid:
                    if prompt_data.context:
                        context = prompts.get_rendered_context(
                            prompt_data.context, prompt_data.previous_promptid
                        )
                        context = f"""
                        ## General context
                        {context}
                        """
                    else:
                        context = ""

                    user_input = f"""
{context}

## Specific task we're working on

{prompts.get(prompt_data.previous_promptid).metadata["title"]}

{prompt_data.first_step_input}

## What I have so far
{prompts.get(prompt_data.previous_promptid).metadata.get("output_framing", "")}

I want to focus on this item:

{prompt_data.item}

## My follow-up question

{prompt_data.userinput}
                    """
                elif (
                    prompt_data.previous_framing is not None
                    and prompt_data.previous_framing != ""
                ):
                    # For our custom-built pages that don't work with "previous prompt"
                    user_input = f"""
## What we're working on
{prompt_data.previous_framing}

## Context
{prompt_data.first_step_input}

## What I have so far
I want to focus on this item:
{prompt_data.item}

## My follow-up question
{prompt_data.userinput}
                    """

                return stream_fn(
                    prompt=user_input,
                    chat_category="explore",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_key=prompt_data.document,
                    user_identifier=self.get_hashed_user_id(request),
                    origin_url=origin_url,
                )

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )
