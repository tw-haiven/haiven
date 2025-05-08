# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import Request
from api.api_basics import HaivenBaseApi
from llms.model_config import ModelConfig

CONFIG_TO_PROMPT_MAPPING = {
    "company": "guided-company-research",
    "ai-tool": "guided-ai-tool-research",
}


class ApiCompanyResearch(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        @app.post("/api/research")
        async def company_research(request: Request):
            origin_url = request.headers.get("referer")
            chat_category = "company-research"

            body = await request.json()
            user_input = body.get("userinput", "")
            config = body.get("config", "company")

            prompt, _ = prompt_list.render_prompt(
                prompt_choice=CONFIG_TO_PROMPT_MAPPING.get(
                    config, "guided-company-research"
                ),
                user_input=user_input,
            )

            perplexity_model_config = ModelConfig(
                "perplexity", "perplexity", "Perplexity"
            )

            return self.stream_json_chat(
                prompt,
                chat_category=chat_category,
                prompt_id="company-research",
                user_identifier=self.get_hashed_user_id(request),
                origin_url=origin_url,
                model_config=perplexity_model_config,
            )
