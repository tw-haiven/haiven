# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi import HTTPException
from pydantic import BaseModel
from api.api_basics import HaivenBaseApi, PromptRequestBody


class TitleContent(BaseModel):
    title: str = None
    content: str = None


class FollowUpPromptInput(BaseModel):
    input: str
    scenarios: List[TitleContent]


class FollowUpRequest(PromptRequestBody):
    scenarios: List[TitleContent] = []
    previous_promptid: str = None


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
        def generate_follow_up(prompt_data: FollowUpRequest):
            try:
                # TODO: !! text vs JSON - guided or not?
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
                    chat_category="boba-chat",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_key=prompt_data.document,
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
