# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
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


class ChatClient:
    def __init__(self, model_config: ModelConfig = None):
        self.model_config = model_config

    def stream(self, messages: List[HaivenMessage]):
        json_messages = [message.to_json() for message in messages]
        for result in completion(
            model=self.model_config.lite_id, messages=json_messages, stream=True
        ):
            if result.choices[0].delta.content is not None:
                yield {"content": result.choices[0].delta.content}


class ChatClientFactory:
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service

    # Factory method gives us some extra control over how the ChatClients are created
    def new_chat_client(self, model: ModelConfig) -> ChatClient:
        return ChatClient(model_config=model)
