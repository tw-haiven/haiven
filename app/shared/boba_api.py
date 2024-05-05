# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import requests
import json
from shared.content_manager import ContentManager
from shared.models.model import Model
from shared.prompts_factory import PromptsFactory
from shared.services.config_service import ConfigService
from shared.llm_config import LLMChatFactory, LLMConfig

from pydantic import BaseModel

from langchain.schema import HumanMessage


def get_threat_modelling_prompt(input):
    return f"""
        Based on the application description, help me to brainstorm for a threat modelling analysis all the things that could go wrong from a security perspective. Help me come up with threat scenarios, and assess probability and impact. Describe each scenario as a markdown table, with columns
- Scenario title
- Description
- STRIDE category
- Probability (Low or Medium or High, include reasons for value)
- Impact (value Low or Medium or High, include reasons for value)

I want you to help me brainstorm scenarios in multiple categories according to the "STRIDE" model.
- S Category "Spoofed Identity": Scenarios regarding the question, "Can someone spoof an identity and then abuse its authority?" based on my application description.
- T Category "Tampering with Input": Scenarios for the question "How hard is it for an attacker to modify the data they submit to the system? Can they break a trust boundary and modify the code which runs as part of your system?"
- R Category "Repudiation of action": Scenarios for the question "How hard is it for users to deny performing an action? What evidence does the system collect to help you to prove otherwise?" Non-repudiation refers to the ability of a system to ensure people are accountable for their actions.
- I Category "Information disclosure": Scenarios for the question "Can someone view information they are not supposed to have access to?" Information disclosure threats involve the exposure or interception of information to unauthorised individuals.
- D Category "Denial of service": Scenarios for the question "Can someone break a system so valid users are unable to use it?" Denial of service attacks work by flooding, wiping or otherwise breaking a particular service or system.
- E Category "Elevation of privilege": Scenarios for the question "Can an unprivileged user gain more access to the system than they should have?" Elevation of privilege attacks are possible because authorisation boundaries are missing or inadequate.

You will create at least one scenario for each category. Give me at least 10 scenarios.

You will respond with only a valid JSON array of scenario objects. Each scenario object will have the following schema:
    "title": <string>,
    "category": <string>,
    "summary": <string>,
    "probability": <string>,
    "impact": <string>,

Make sure to apply each scenario category to MY input, and give me scenarios that are relevant to my particular application.

Here is my input that describes my application:
    {input}
    
    """


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


userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"


class PromptRequestBody(BaseModel):
    promptid: str
    userinput: str


class BobaApi:
    def __init__(
        self, prompts_factory: PromptsFactory, content_manager: ContentManager
    ):
        self.prompts_factory = prompts_factory
        self.content_manager = content_manager

    def prompt(self, prompt_id, user_input):
        prompt_list = self.prompts_factory.create_chat_prompt(
            self.content_manager.knowledge_base_markdown
        )
        rendered_prompt = prompt_list.render_prompt(
            active_knowledge_context="demo_crm",
            prompt_choice=prompt_id,
            user_input=user_input,
            additional_vars={},
            warnings=[],
        )
        data = self.stream_from_model(rendered_prompt)
        for chunk in data:
            yield chunk

    def stream_from_model(self, prompt, model="azure-gpt35"):
        client = LLMChatFactory.new_llm_chat(LLMConfig(model, 0.5))
        messages = [HumanMessage(content=prompt)]
        stream = client.stream(messages)
        for chunk in stream:
            yield chunk.content

        yield "[DONE]"

    def event_stream_json(self, prompt):
        data = self.stream_from_model(prompt, "azure-gpt4")
        for chunk in data:
            if chunk == "[DONE]":
                print("done, send", f"data: {chunk}")
                yield f"data: {chunk}\n\n"
            else:
                message = '{ "data": ' + json.dumps(chunk) + " }"
                yield f"data: {message}\n\n"

    def auth_error_response_for_content(accept_header, error):
        if "text/event-stream" in accept_header:
            return StreamingResponse(
                error, media_type="text/event-stream", status_code=403
            )
        else:
            return JSONResponse({"error": error}, status_code=403)

    def validate_token_via_userinfo(self, access_token, userinfo_url):
        # TODO: Right now this happens on every request - cache this for a bit?
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(userinfo_url, headers=headers)
        if response.status_code == 200:
            return response.json()  # Token is valid
        else:
            return None  # Token is invalid or expired

    async def check_bearer(self, request: Request, call_next):
        try:
            content_type = request.headers.get("Accept")
            bearer = request.headers.get("Authorization")
            if not bearer:
                return self.auth_error_response_for_content(
                    content_type, "Authentication error"
                )

            token = bearer.split(" ")[1]
            user_info = self.validate_token_via_userinfo(token, userinfo_url)
            if not user_info:
                return self.auth_error_response_for_content(
                    content_type, "Authentication error"
                )

            return await call_next(request)
        except Exception as error:
            print(f"Error validating token: {error}")
            return self.auth_error_response_for_content(content_type, error)

    def add_endpoints(self, app: FastAPI):
        @app.get("/api/models")
        def get_models(request: Request):
            models: List[Model] = ConfigService.load_models("config.yaml")
            return JSONResponse(
                [{"id": model.id, "name": model.name} for model in models]
            )

        @app.get("/api/make-scenario")
        def make_scenario(request: Request):
            input = request.query_params.get("input", "productization of consulting")
            num_scenarios = request.query_params.get("num_scenarios", 5)
            detail = request.query_params.get("detail") == "true"
            time_horizon = request.query_params.get("time_horizon", "5-year")
            optimism = request.query_params.get("optimism", "optimistic")
            realism = request.query_params.get("realism", "futuristic sci-fi")
            return StreamingResponse(
                self.event_stream_json(
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

        @app.get("/api/threat-modelling")
        def threat_modelling(request: Request):
            input = request.query_params.get("input", "productization of consulting")
            return StreamingResponse(
                self.event_stream_json(get_threat_modelling_prompt(input)),
                media_type="text/event-stream",
                headers={
                    "Connection": "keep-alive",
                    "Content-Encoding": "none",  # Necessary for the stream to work across the Next rewrite
                },
            )

        @app.post("/api/prompt")
        def prompt(prompt_data: PromptRequestBody):
            return StreamingResponse(
                self.prompt(prompt_data.promptid, prompt_data.userinput),
                media_type="text/event-stream",
                headers={
                    "Connection": "keep-alive",
                    "Content-Encoding": "none",
                },
            )
