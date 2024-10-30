# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from config_service import ConfigService
from llms.model_config import ModelConfig
from logger import HaivenLogger
from llms.aws_chat import AWSChat
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
    def __init__(self, langchain_base_chat: BaseChatModel):
        self.langchain_base_chat = langchain_base_chat

    def stream(self, messages: List[HaivenMessage]):
        langchain_messages = [message.to_langchain() for message in messages]
        for result in self.langchain_base_chat.stream(langchain_messages):
            yield result


class ChatClientFactory:
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service

    def new_chat_client(self, model: ModelConfig, stop=None) -> ChatClient:
        HaivenLogger.get().analytics(
            "Model selected",
            {
                "provider": model.provider,
                "model": model.id,
                "temperature": model.temperature,
            },
        )

        match model.provider.lower():
            case "azure":
                model_kwargs = {}

                return ChatClient(
                    AzureChatOpenAI(
                        openai_api_key=model.config.get("api_key"),
                        azure_deployment=model.config.get("azure_deployment"),
                        azure_endpoint=model.config.get("azure_endpoint"),
                        api_version=model.config.get("api_version"),
                        temperature=model.temperature,
                        stop=[stop] if stop is not None else None,
                        model_kwargs=model_kwargs,
                    )
                )

            case "gcp":
                stop_arg = []
                if stop is not None:
                    stop_arg = [stop]
                # TODO: "stop" doesn't seem to work with Gemini?
                # Might be a Langchain problem, it looks as if they're not passing the stop arg on via the constructor
                # but they do pass it on when it's passed to the model call...
                return ChatClient(
                    ChatGoogleGenerativeAI(
                        model=model.config.get("model"),
                        temperature=model.temperature,
                        stop=stop_arg,
                    )
                )

            # AWS
            case "aws":
                model_kwargs = {"temperature": model.temperature}
                if stop is not None:
                    model_kwargs["stop_sequences"] = [stop]
                return ChatClient(
                    AWSChat(
                        model_id=model.config.get("model_id"),
                        region_name=model.config.get("region_name"),
                        model_kwargs=model_kwargs,
                    )
                )

            # OpenAI, mainly to make it easier for folks to run locally
            case "openai":
                model_kwargs = {}

                return ChatClient(
                    ChatOpenAI(
                        api_key=model.config.get("api_key"),
                        model_name=model.config.get("model_name"),
                        temperature=model.temperature,
                        stop=[stop] if stop is not None else None,
                        model_kwargs=model_kwargs,
                    )
                )

            case "ollama":
                model_kwargs = {}
                if stop is not None:
                    model_kwargs["stop"] = [stop]
                return ChatClient(
                    ChatOpenAI(
                        api_key="somerandomkey",
                        base_url=model.config.get("base_url") + "/v1",
                        model=model.config.get("model"),
                        temperature=model.temperature,
                        model_kwargs=model_kwargs,
                    )
                )

            case _:
                print("ERROR: unknown provider '", model.provider, "'")
