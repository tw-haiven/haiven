# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from api.models.explore_request import ExploreRequest
from tab_story_validation.api import enable_story_validation
from tab_requirements.api import enable_requirements
from tab_threat_modelling.api import enable_threat_modelling
from shared.chats import (
    JSONChat,
    ServerChatSessionMemory,
    StreamingChat,
)
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


def get_creative_matrix_prompt(rows, columns, prompt, idea_qualifiers, num_ideas):
    return f"""You are a creative strategist. Given a prompt enclosed in <prompt> below, you will respond to the prompt for each combination/permutation of comma-separated list of rows and columns to generate creative and innovative ideas. Each idea must have a title and description. The idea title must be brief and succinct. Each idea must specifically and directly respond to the prompt. If a company is mentioned in the prompt, make sure you generate ideas specifically for that company. Each idea must be {idea_qualifiers}. You must generate exactly {num_ideas} idea(s) per combination/permutation.

  <prompt>{prompt}</prompt>
  <rows>{rows}</rows>
  <columns>{columns}</columns>

  You will respond with a valid JSON array, by row by column by idea. For example:

  If Rows = "row 0, row 1" and Columns = "column 0, column 1" then you will respond with the following:
  [
    {{
      "row": "row 0",
      "columns": [
        {{
          "column": "column 0",
          "ideas": [
            {{
              "title": "Idea 0 title for prompt and row 0 and column 0",
              "description": "idea 0 for prompt and row 0 and column 0"
            }},
            ...
          ]
        }},
        {{
          "column": "column 1",
          "ideas": [
            {{
              "title": "Idea 0 title for prompt and row 0 and column 1",
              "description": "idea 0 for prompt and row 0 and column 1"
            }},
            ...
          ]
        }},
      ]
    }},
    {{
      "row": "row 1",
      "columns": [
        {{
          "column": "column 0",
          "ideas": [
            {{
              "title": "Idea 0 title for prompt and row 1 and column 0",
              "description": "idea 0 for prompt and row 1 and column 0"
            }},
            ...
          ]
        }},
        {{
          "column": "column 1",
          "ideas": [
            {{
              "title": "Idea 0 title for prompt and row 1 and column 1",
              "description": "idea 0 for prompt and row 1 and column 1"
            }},
            ...
          ]
        }}
      ]
    }}
  ]

  Remember that each idea must be {idea_qualifiers}. Remember you mnust generate exactly {num_ideas} idea(s) per combination/permutation.

"""


def explore_scenario_prompt(original_input, item, user_message):
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


def generate_context_queries(context):
    return f"""
    You are a Product Manager, given this context:
    {context}

    Generate 3-4 questions that would allow you to understand,
    the context better, taking business, technical, and user perspectives into account.
    You will respond with only a valid string array of questions.
    For example:
    ["first question", "second question", "third question"] // please ensure that you respect this format, and keep each questions to less than 10 words.

    """


class PromptRequestBody(BaseModel):
    promptid: str
    userinput: str
    chatSessionId: str = None


class ExploreScenarioRequestBody(BaseModel):
    context: str
    input: str


class ScenarioQuestionRequestBody(BaseModel):
    context: str


class ScenarioQuestionResponse(BaseModel):
    questions: List[str]


class BobaApi:
    def __init__(
        self,
        prompts_factory: PromptsFactory,
        content_manager: ContentManager,
        chat_session_memory: ServerChatSessionMemory,
        model: str,
    ):
        self.content_manager = content_manager
        self.prompts_factory = prompts_factory
        self.chat_session_memory = chat_session_memory
        self.prompt_list = self.prompts_factory.create_chat_prompt(
            self.content_manager.knowledge_base_markdown
        )
        self.model = model
        print(f"Using model: {self.model}")

    def prompt(self, prompt_id, user_input, chat_session):
        rendered_prompt = self.prompt_list.render_prompt(
            active_knowledge_context=None,
            prompt_choice=prompt_id,
            user_input=user_input,
            additional_vars={},
            warnings=[],
        )

        return self.chat(rendered_prompt, chat_session)

    def chat(self, rendered_prompt, chat_session):
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

        @app.get("/api/knowledge/snippets")
        def get_knowledge_snippets(request: Request):
            all_contexts = (
                self.content_manager.knowledge_base_markdown.get_all_contexts_keys()
            )

            response_data = []
            for context in all_contexts:
                snippets = self.content_manager.knowledge_base_markdown.get_knowledge_content_dict(
                    context
                )
                response_data.append({"context": context, "snippets": snippets})

            return JSONResponse(response_data)

        @app.get("/api/make-scenario")
        def make_scenario(request: Request):
            input = request.query_params.get("input", "productization of consulting")
            num_scenarios = request.query_params.get("num_scenarios", 5)
            detail = request.query_params.get("detail") == "true"
            time_horizon = request.query_params.get("time_horizon", "5-year")
            optimism = request.query_params.get("optimism", "optimistic")
            realism = request.query_params.get("realism", "futuristic sci-fi")
            chat = JSONChat(llm_config=LLMConfig(self.model, 0.2))
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

        enable_threat_modelling(app, self.chat_session_memory, self.chat)
        enable_requirements(app, self.chat_session_memory, self.chat)
        enable_story_validation(app, self.chat_session_memory)

        @app.post("/api/prompt")
        def chat(prompt_data: PromptRequestBody):
            chat_session_key_value, chat_session = (
                self.chat_session_memory.get_or_create_chat(
                    lambda: StreamingChat(
                        llm_config=LLMConfig(self.model, 0.5), stream_in_chunks=True
                    ),
                    prompt_data.chatSessionId,
                    "chat",
                    # TODO: Pass user identifier from session
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

        @app.post("/api/scenario/explore")
        def explore_scenario(explore_request: ExploreRequest):
            chat_session_key_value, chat_session = (
                self.chat_session_memory.get_or_create_chat(
                    lambda: StreamingChat(
                        llm_config=LLMConfig(self.model, 0.5), stream_in_chunks=True
                    ),
                    explore_request.chatSessionId,
                    "chat",
                    # TODO: Pass user identifier from session
                )
            )

            prompt = explore_request.userMessage
            if explore_request.chatSessionId is None:
                prompt = explore_scenario_prompt(
                    explore_request.originalInput,
                    explore_request.item,
                    explore_request.userMessage,
                )

            return StreamingResponse(
                self.chat(prompt, chat_session),
                media_type="text/event-stream",
                headers={
                    "Connection": "keep-alive",
                    "Content-Encoding": "none",
                    "Access-Control-Expose-Headers": "X-Chat-ID",
                    "X-Chat-ID": chat_session_key_value,
                },
            )

        @app.get("/api/creative-matrix")
        async def creative_matrix(request: Request):
            rows = request.query_params.getlist("rows")
            columns = request.query_params.getlist("columns")
            prompt = request.query_params.get("prompt")
            idea_qualifiers = request.query_params.get("idea_qualifiers", None)
            num_ideas = int(request.query_params.get("num_ideas", 3))

            creative_matrix_prompt = get_creative_matrix_prompt(
                rows, columns, prompt, idea_qualifiers, num_ideas
            )
            chat = JSONChat(llm_config=LLMConfig(self.model, 0.2))
            return StreamingResponse(
                chat.run(creative_matrix_prompt),
                media_type="text/event-stream",
                headers={
                    "Connection": "keep-alive",
                    "Content-Encoding": "none",
                },
            )
