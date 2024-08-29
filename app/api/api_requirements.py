# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from api.models.explore_request import ExploreRequest
from fastapi import Request
from api.api_basics import HaivenBaseApi


def get_explore_kickoff_prompt(originalInput, item, user_message):
    return f"""
    ## ROLE
    
    You are an expert agile coach and will help me, the product owner and analyst, refine the user stories. 
    
    I'm currently trying to refine REQUIREMENTS in the following area:

    {originalInput}
     
    More specifically, I'm looking to refine this SUB-REQUIREMENT:

    {item}
    
    ## TASK

    Your task as is to answer my questions and make suggestions to refine and improve the requirement and 
    take into account my suggestions and clarifications towards writing the final definition for the user story. 
    Keep your suggestions strictly to the SUB-REQUIREMENT I provided, 
    and do not expand the scope to related scenarios or features.

    ## MY QUESTION / MY ASK FOR YOU

    {user_message}
    """


class ApiRequirementsBreakdown(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        @app.get("/api/requirements")
        def requirements(request: Request):
            prompt, _ = prompt_list.render_prompt(
                active_knowledge_context=None,
                prompt_choice="guided-requirements",
                user_input=request.query_params.get("input"),
                additional_vars={},
                warnings=[],
            )

            return self.stream_json_chat(prompt, "requirements-breakdown")

        @app.post("/api/requirements/explore")
        def chat(explore_request: ExploreRequest):
            prompt = explore_request.userMessage
            if explore_request.chatSessionId is None:
                prompt = get_explore_kickoff_prompt(
                    explore_request.originalInput,
                    explore_request.item,
                    explore_request.userMessage,
                )

            return self.stream_text_chat(
                prompt, "requirements-breakdown-explore", explore_request.chatSessionId
            )
