# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import os
from typing import List, Dict, Any, Optional
from config_service import ConfigService
from llms.model_config import ModelConfig
from pydantic import BaseModel
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages.base import BaseMessage
from llms.litellm_wrapper import llmCompletion


class HaivenMessage(BaseModel):
    content: str

    def to_json(self) -> dict:
        # Default implementation - subclasses should override with proper role
        return {"content": self.content, "role": "user"}


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
    usage: Optional[Dict[str, Any]] = None


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

        # Mock token usage for testing
        mock_usage = {"prompt_tokens": 25, "completion_tokens": 15, "total_tokens": 40}

        for i, chunk in enumerate(test_data):
            result = MockResult(choices=[MockChoice(delta=MockDelta(content=chunk))])
            # Add usage data only on the last chunk
            if i == len(test_data) - 1:
                result.usage = mock_usage
            yield result


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
            completion_fn = llmCompletion

        citations = None
        usage_data = None
        for result in completion_fn(
            model=self.model_config.lite_id,
            messages=json_messages,
            stream=True,
            stream_options={"include_usage": True},
            **self._get_kwargs(),
        ):
            # Handle different response types safely
            try:
                if isinstance(result, dict):
                    citations = citations or result.get("citations", None)
                    if self._is_token_usage_result(result):
                        usage_data = result.get("usage")
                else:
                    # Handle object-like responses
                    if hasattr(result, "usage") and getattr(result, "usage", None):
                        usage_data = getattr(result, "usage")
                    if hasattr(result, "get"):
                        citations = citations or getattr(result, "get")(
                            "citations", None
                        )

                # Extract content from streaming response
                if hasattr(result, "choices") and getattr(result, "choices", None):
                    choices = getattr(result, "choices")
                    if choices and len(choices) > 0 and hasattr(choices[0], "delta"):
                        delta = getattr(choices[0], "delta")
                        if (
                            hasattr(delta, "content")
                            and getattr(delta, "content") is not None
                        ):
                            yield {"content": getattr(delta, "content")}
            except (AttributeError, TypeError, IndexError):
                # Skip malformed responses
                continue

        if citations is not None:
            yield {"metadata": {"citations": citations}}

        # Yield usage data if available - simplified
        if usage_data is not None:
            # Simple normalization - just extract basic fields
            try:
                normalized_usage = {
                    "prompt_tokens": getattr(usage_data, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage_data, "completion_tokens", 0),
                    "total_tokens": getattr(usage_data, "total_tokens", 0),
                }
                yield {"usage": normalized_usage}
            except Exception:
                # If we can't extract, just provide zeros
                yield {
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    }
                }

    def _is_token_usage_result(self, result):
        """Check if a result contains token usage data, not just any content containing 'usage'"""
        if not isinstance(result, dict):
            return False

        # Must have "usage" as a top-level key
        if "usage" not in result:
            return False

        usage_data = result["usage"]

        # For dict usage data, check for expected token fields
        if isinstance(usage_data, dict):
            expected_fields = ["prompt_tokens", "completion_tokens", "total_tokens"]
            return any(field in usage_data for field in expected_fields)

        # For object usage data, check for expected token attributes
        if (
            hasattr(usage_data, "prompt_tokens")
            or hasattr(usage_data, "completion_tokens")
            or hasattr(usage_data, "total_tokens")
        ):
            return True

        return False


class ChatClientFactory:
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service

    # Factory method gives us some extra control over how the ChatClients are created
    def new_chat_client(self, model: ModelConfig) -> ChatClient:
        return ChatClient(model_config=model)
