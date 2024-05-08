# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from tab_requirements.api import enable_requirements
from tab_threat_modelling.api import enable_threat_modelling
from shared.chats import JSONChat, ServerChatSessionMemory, StreamingChat
from shared.content_manager import ContentManager
from shared.models.model import Model
from shared.prompts_factory import PromptsFactory
from shared.services.config_service import ConfigService
from shared.llm_config import LLMConfig

from pydantic import BaseModel


def get_scenarios_prompt(
    input,
    num_scenarios=5,
    optimism="Pessimistic",
    realism="Bizarre",
    time_horizon="10 years",
    detail=False,
):
    detail_prompt = f"""You are a visionary futurist. Given a strategic prompt, you will create {num_scenarios} futuristic hypothetical scenarios that happen {time_horizon} from now. Each scenario will have a:
  - Title: Must be a complete sentence written in the past tense
  - Summary
  - Plausibility: (low, medium, or high)
  - Probability: (low, medium, or high)
  - Horizon: (short-term, medium-term, long-term) and number of years
  - List of signals that are the driving forces behind this scenario becoming a reality
  - List of threats
  - List of opportunities
  
  You will create exactly {num_scenarios} scenarios. Each scenario must be a {optimism} version of the future. Each scenario must be {realism}.

  You will respond with only a valid JSON array of scenario objects. Each scenario object will have the following schema:
    "title": <string>,  //Must be a complete sentence written in the past tense
    "summary": <string>,
    "plausibility": <string>,
    "horizon": <string>,
    "signals": [<array of strings>],
    "threats": [<array of strings>],
    "opportunities": [<array of strings>]
  
  Strategic prompt: "{input}"
"""

    default_prompt = f"""
        You are a visionary futurist. Given a strategic prompt, you will create {num_scenarios} futuristic, hypothetical scenarios that happen {time_horizon} from now. Each scenario will have a:
    - Title: Must be a complete sentence written in the past tense
    - Description: Must be at least 2 sentences long
    - Plausibility: (low, medium or high)
    - Probability: (low, medium or high)
    - Horizon: (short-term, medium-term, long-term) and number of years
    
    You will create exactly {num_scenarios} scenarios. Each scenario must be a {optimism} version of the future. Each scenario must be {realism}.
    
    You will respond with only a valid JSON array of scenario objects. Each scenario object will have the following schema:
        "title": <string>,    //Must be a complete sentence written in the past tense
        "summary": <string>,  //description
        "plausibility": <string>,
        "horizon": <string>

    Strategic prompt: "{input}"
    
    """

    if detail:
        return detail_prompt
    else:
        return default_prompt


class PromptRequestBody(BaseModel):
    promptid: str
    userinput: str
    chatSessionId: str = None


class BobaApi:
    def __init__(
        self,
        prompts_factory: PromptsFactory,
        content_manager: ContentManager,
        chat_session_memory: ServerChatSessionMemory,
    ):
        self.content_manager = content_manager
        self.prompts_factory = prompts_factory
        self.chat_session_memory = chat_session_memory
        self.prompt_list = self.prompts_factory.create_chat_prompt(
            self.content_manager.knowledge_base_markdown
        )

    def prompt(self, prompt_id, user_input, chat_session):
        rendered_prompt = self.prompt_list.render_prompt(
            active_knowledge_context="demo_crm",
            prompt_choice=prompt_id,
            user_input=user_input,
            additional_vars={},
            warnings=[],
        )

        for chunk in chat_session.start_with_prompt(rendered_prompt):
            yield chunk

    def add_endpoints(self, app: FastAPI):
        @app.get("/api/models")
        def get_models(request: Request):
            models: List[Model] = ConfigService.load_models("config.yaml")
            return JSONResponse(
                [{"id": model.id, "name": model.name} for model in models]
            )

        @app.get("/api/prompts")
        def get_prompts(request: Request):
            response_data = [entry.metadata for entry in self.prompt_list.prompts]
            return JSONResponse(response_data)

        @app.get("/api/make-scenario")
        def make_scenario(request: Request):
            input = request.query_params.get("input", "productization of consulting")
            num_scenarios = request.query_params.get("num_scenarios", 5)
            detail = request.query_params.get("detail") == "true"
            time_horizon = request.query_params.get("time_horizon", "5-year")
            optimism = request.query_params.get("optimism", "optimistic")
            realism = request.query_params.get("realism", "futuristic sci-fi")
            chat = JSONChat()
            return StreamingResponse(
                chat.run(
                    get_scenarios_prompt(
                        input,
                        num_scenarios=num_scenarios,
                        optimism=optimism,
                        realism=realism,
                        time_horizon=time_horizon,
                        detail=detail,
                    )
                ),
                media_type="text/event-stream",
                headers={
                    "Connection": "keep-alive",
                    "Content-Encoding": "none",  # Necessary for the stream to work across the Next rewrite
                },
            )

        enable_threat_modelling(app)
        enable_requirements(app)

        @app.post("/api/prompt")
        def chat(prompt_data: PromptRequestBody):
            chat_session_key_value, chat_session = (
                self.chat_session_memory.get_or_create_chat(
                    lambda: StreamingChat(
                        llm_config=LLMConfig("azure-gpt35", 0.5), stream_in_chunks=True
                    ),
                    prompt_data.chatSessionId,
                    "chat",
                    "birgitta",
                )
            )

            return StreamingResponse(
                self.prompt(prompt_data.promptid, prompt_data.userinput, chat_session),
                media_type="text/event-stream",
                headers={
                    "Connection": "keep-alive",
                    "Content-Encoding": "none",
                    "Access-Control-Expose-Headers": "X-Chat-ID",
                    "X-Chat-ID": chat_session_key_value,
                },
            )
