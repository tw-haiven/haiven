# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import Query, Request
from api.api_basics import HaivenBaseApi, PromptRequestBody


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
            request: Request,
            prompt_data: PromptRequestBody,
            variation: str = Query("workflow"),
        ):
            origin_url = request.headers.get("referer")
            chat_category = "boba-requirements"
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
                prompt_id="requirements",
                chat_category=chat_category,
                chat_session_key_value=prompt_data.chatSessionId,
                document_key=prompt_data.document,
                user_identifier=self.get_hashed_user_id(request),
                context=prompt_data.context,
                origin_url=origin_url,
            )
