# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import Request
from api.api_basics import HaivenBaseApi


class ApiScenarios(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        @app.get("/api/make-scenario")
        def make_scenario(request: Request):
            origin_url = request.headers.get("referer")
            chat_category = "scenarios"
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

            prompt, _ = prompt_list.render_prompt(
                active_knowledge_context=None,
                prompt_choice="guided-scenarios-detailed"
                if detailed
                else "guided-scenarios",
                user_input="",
                additional_vars=variables,
                warnings=[],
            )

            return self.stream_json_chat(
                prompt,
                chat_category=chat_category,
                user_identifier=self.get_hashed_user_id(request),
                origin_url=origin_url,
                prompt_id_for_logging=chat_category,
            )
