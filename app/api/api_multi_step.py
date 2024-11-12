# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi import HTTPException
from pydantic import BaseModel
from api.api_basics import HaivenBaseApi, PromptRequestBody


class TitleContent(BaseModel):
    title: str = None
    content: str = None


class IterateRequest(PromptRequestBody):
    scenarios: str


class FollowUpRequest(PromptRequestBody):
    previous_promptid: str = None
    scenarios: List[TitleContent] = []


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

        @app.post("/api/prompt/follow-up")
        def generate_follow_up(prompt_data: FollowUpRequest):
            try:
                stream_fn = self.stream_text_chat
                prompts = self.prompt_list

                user_input = prompt_data.userinput
                if prompt_data.previous_promptid is not None:
                    output_framing = prompts.get(
                        prompt_data.previous_promptid
                    ).metadata["output_framing"]

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
                )

                return stream_fn(
                    prompt=rendered_prompt,
                    chat_category="follow-up",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_key=prompt_data.document,
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @app.post("/api/prompt/explore")
        def kick_off_explore(prompt_data: ExploreRequest):
            try:
                stream_fn = self.stream_text_chat
                prompts = self.prompt_list

                user_input = prompt_data.userinput
                if (
                    prompt_data.previous_promptid is not None
                    and prompt_data.previous_promptid != ""
                ):
                    context = prompts.get_rendered_context(
                        prompt_data.context, prompt_data.previous_promptid
                    )

                    user_input = f"""
## General context
{context}

## Specific task we're working on

{prompts.get(prompt_data.previous_promptid).metadata["title"]}

{prompt_data.first_step_input}

## What I have so far
{prompts.get(prompt_data.previous_promptid).metadata["output_framing"]}

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
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

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
