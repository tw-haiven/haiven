# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import Request
from api.api_basics import HaivenBaseApi


class ApiCreativeMatrix(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        @app.get("/api/creative-matrix")
        async def creative_matrix(request: Request):
            origin_url = request.headers.get("referer")

            variables = {
                "rows": request.query_params.get("rows"),
                "columns": request.query_params.get("columns"),
                "prompt": request.query_params.get("prompt"),
                "idea_qualifiers": request.query_params.get("idea_qualifiers", None),
                "num_ideas": request.query_params.get("num_ideas", "3"),
            }

            prompt, _ = prompt_list.render_prompt(
                active_knowledge_context=None,
                prompt_choice="guided-creative-matrix",
                user_input="",
                additional_vars=variables,
                warnings=[],
            )

            return self.stream_json_chat(
                prompt,
                "creative-matrix",
                origin_url=origin_url,
                prompt_id="creative-matrix",
            )
