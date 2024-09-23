# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import Query
from api.models.explore_request import ExploreRequest
from api.api_basics import HaivenBaseApi, PromptRequestBody


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

        def _get_variation_prompt(variation: str):
            if variation == "timeline":
                return """
                    - Timeline-Based Breakdown: Divide the epic into phases or milestones.
                    Prioritize user stories for each sprint duration, tackling high-priority items first.
                """
            elif variation == "story-telling":
                return """
                    Storytelling Approach: Visualize the epic's journey from start to finish. What are the main events or sequences?
                """
            elif variation == "workflow":
                return """
                    - Workflow Breakdown: List the specific tasks or activities that need to be completed. Example: For a product launch epic, you might have design, prototyping, manufacturing, marketing, and distribution.
                """
            elif variation == "data-boundaries":
                return """
                    - Data Boundaries: Separate the epic based on varying data or information needs. Example: One story might tackle displaying company stats, while another handles company contacts.
                """
            elif variation == "operational-boundaries":
                return """
                    Operational Boundaries: Determine the epic's core functionality or minimum viable feature. Sequentially add slices of extended functionality.
                    """
            elif variation == "cross-cutting-concerns":
                return """
                    Cross-cutting Concerns: Recognize overarching attributes required for every feature. Separate out concerns such as security, validation, and exception handling.
                """
            return ""

        @app.post("/api/requirements")
        def requirements(
            prompt_data: PromptRequestBody, variation: str = Query("workflow")
        ):
            variation_prompt = _get_variation_prompt(variation)

            rendered_prompt, _ = self.prompt_list.render_prompt(
                active_knowledge_context=prompt_data.context,
                prompt_choice="guided-requirements",
                user_input=prompt_data.userinput,
                additional_vars={"variation": variation_prompt},
                warnings=[],
            )

            return self.stream_json_chat(
                prompt=rendered_prompt,
                chat_category="boba-requirements",
                chat_session_key_value=prompt_data.chatSessionId,
                document_key=prompt_data.document,
            )

        @app.post("/api/requirements/explore")
        def requirements_explore(explore_request: ExploreRequest):
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
