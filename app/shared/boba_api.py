# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import requests
import json
from shared.llm_config import LLMChatFactory, LLMConfig

from langchain.schema import HumanMessage


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


class BobaApi:
    def get_new_data(self, prompt):
        client = LLMChatFactory.new_llm_chat(LLMConfig("azure-gpt35", 0.3))
        messages = [HumanMessage(content=prompt)]
        stream = client.stream(messages)
        for chunk in stream:
            yield chunk.content

        yield "[DONE]"

    def event_stream(self, prompt):
        data = self.get_new_data(prompt)
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
        ## ENDPOINTS ##############################

        @app.get("/api/make-scenario")
        def make_scenario(request: Request):
            input = request.query_params.get("input", "productization of consulting")
            num_scenarios = request.query_params.get("num_scenarios", 5)
            detail = request.query_params.get("detail") == "true"
            time_horizon = request.query_params.get("time_horizon", "5-year")
            optimism = request.query_params.get("optimism", "optimistic")
            realism = request.query_params.get("realism", "futuristic sci-fi")
            return StreamingResponse(
                self.event_stream(
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
