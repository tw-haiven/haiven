# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import os
from typing import List
from litellm import completion
from config_service import ConfigService
from llms.model_config import ModelConfig
from pydantic import BaseModel
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages.base import BaseMessage


class HaivenMessage(BaseModel):
    content: str


class HaivenAIMessage(HaivenMessage):
    def to_json(self) -> dict:
        # TODO: Is it really always "assistant", for all APIs? ...
        return {"content": self.content, "role": "assistant"}

    def to_langchain(self) -> BaseMessage:
        return AIMessage(content=self.content)


class HaivenHumanMessage(HaivenMessage):
    def to_json(self) -> dict:
        return {"content": self.content, "role": "user"}

    def to_langchain(self) -> BaseMessage:
        return HumanMessage(content=self.content)


class HaivenSystemMessage(HaivenMessage):
    def to_json(self) -> dict:
        return {"content": self.content, "role": "system"}

    def to_langchain(self) -> BaseMessage:
        return SystemMessage(content=self.content)


class MockDelta(BaseModel):
    content: str


class MockChoice(BaseModel):
    delta: MockDelta


class MockResult(BaseModel):
    choices: List[MockChoice]


class MockModelClient:
    def completion(self, messages, model=None, **kwargs):
        message = messages[0]["content"]
        test_data = [
            "[Mock response]",
            "User Stories:",
            "\n\n",
            "1. As a customer, I want to be able to browse the available items in the online store so that",
            " I can find something to add to my basket.",
            "\n",
            "2. As a customer, I want to be able to search for specific items in the online store",
            " so that I can quickly find and add them to my basket.",
            "\n",
        ]
        if "json" in message.lower():
            full_test_scenario = {
                "title": "Full mocked scenario with a very long title title title title",
                "summary": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "probability": "Low - Most users would have no reason to deny",
                "impact": "Medium - This could lead to accountability issues",
            }
            test_data = [
                "[ {",
                ' "title": ',
                ' "Mock scenario 1"',
                ', "summary": ',
                ' "scenario description" ' " }, { ",
                ' "title": ',
                ' "Hello scenario 2" }',
                json.dumps(full_test_scenario),
                "]",
            ]
        for chunk in test_data:
            yield MockResult(choices=[MockChoice(delta=MockDelta(content=chunk))])


class ChatClient:
    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config

    def _get_kwargs(self) -> dict:
        if self.model_config.provider == "ollama":
            return {"api_base": os.environ.get("OLLAMA_HOST", "")}
        else:
            return {}

    def stream(self, messages: List[HaivenMessage], mock: bool = False):
        json_messages = [message.to_json() for message in messages]
        if os.environ.get("MOCK_AI", False):
            completion_fn = MockModelClient().completion
        else:
            completion_fn = completion
        for result in completion_fn(
            model=self.model_config.lite_id,
            messages=json_messages,
            stream=True,
            **self._get_kwargs(),
        ):
            if result.choices[0].delta.content is not None:
                yield {"content": result.choices[0].delta.content}


class ChatClientFactory:
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service

    # Factory method gives us some extra control over how the ChatClients are created
    def new_chat_client(self, model: ModelConfig) -> ChatClient:
        return ChatClient(model_config=model)
