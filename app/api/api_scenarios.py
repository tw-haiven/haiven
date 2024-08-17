# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import Request
from api.api_basics import HaivenBaseApi
from api.models.explore_request import ExploreRequest


class ApiScenarios(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        @app.get("/api/make-scenario")
        def make_scenario(request: Request):
            variables = {
                "input": request.query_params.get(
                    "input", "productization of consulting"
                ),
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

            return self.stream_json_chat(prompt, "scenarios")

        @app.post("/api/scenario/explore")
        def explore_scenario(explore_request: ExploreRequest):
            prompt = explore_request.userMessage
            if explore_request.chatSessionId is None:
                prompt = self.explore_scenario_prompt(
                    explore_request.originalInput,
                    explore_request.item,
                    explore_request.userMessage,
                )

            return self.stream_text_chat(
                prompt, "scenarios-explore", explore_request.chatSessionId
            )

    def explore_scenario_prompt(self, original_input, item, user_message):
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
