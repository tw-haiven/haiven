# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from fastapi import Request
from api.api_basics import HaivenBaseApi
from llms.model_config import ModelConfig
from logger import HaivenLogger

CONFIG_TO_PROMPT_MAPPING = {
    "company": "company-overview",
    "ai-tool": "company-overview-ai-tool",
}


class ApiCompanyResearch(HaivenBaseApi):
    def __init__(self, app, chat_session_memory, model_key, prompt_list):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        @app.post("/api/research")
        async def company_research(request: Request):
            user_id = self.get_hashed_user_id(request)
            origin_url = request.headers.get("referer")
            chat_category = "company-research"

            body = await request.json()
            user_input = body.get("userinput", "")
            config = body.get("config", "company")
            prompt_id = CONFIG_TO_PROMPT_MAPPING.get(config, "company-overview")

            HaivenLogger.get().analytics(
                "Company overview",
                {"user_id": user_id, "prompt_id": prompt_id, "category": None},
            )

            prompt, _ = prompt_list.render_prompt(
                prompt_choice=prompt_id,
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
