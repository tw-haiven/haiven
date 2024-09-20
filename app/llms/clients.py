# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from pydantic import BaseModel
from config_service import ConfigService
from logger import HaivenLogger
from llms.model import Model
from llms.aws_chat import AWSChat


class ChatClientConfig:
    def __init__(self, init_service_name: str, init_temperature: float):
        self.service_name: str = init_service_name
        self.temperature: float = init_temperature

    def change_model(self, new_value: str):
        self.service_name = new_value

    def change_temperature(self, new_tone: float):
        self.temperature = new_tone


class MockChunk(BaseModel):
    content: str


class MockModelClient:
    def stream(self, messages):
        message = messages[0].content
        test_data = [
            'User "Stories:"',
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
                "title": "Full scenario",
                "summary": "A description",
                "probability": "Low - Most users would have no reason to deny",
                "impact": "Medium - This could lead to accountability issues",
            }
            test_data = [
                "[ {",
                ' "title": ',
                ' "Hello scenario 1"',
                ', "summary": ',
                ' "scenario description" ' " }, { ",
                ' "title": ',
                ' "Hello scenario 2" }',
                json.dumps(full_test_scenario),
                "]",
            ]
        for chunk in test_data:
            yield MockChunk(content=chunk)


class ChatClientFactory:
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service

    def new_chat_client(
        self, client_config: ChatClientConfig, stop=None
    ) -> BaseChatModel:
        if client_config.service_name == "mock":
            return MockModelClient()

        model: Model = self.config_service.get_model(client_config.service_name)

        HaivenLogger.get().analytics(
            "Model selected",
            {
                "provider": model.provider,
                "model": model.id,
                "temperature": client_config.temperature,
            },
        )

        match model.provider.lower():
            case "azure":
                model_kwargs = {}

                return AzureChatOpenAI(
                    openai_api_key=model.config.get("api_key"),
                    azure_deployment=model.config.get("azure_deployment"),
                    azure_endpoint=model.config.get("azure_endpoint"),
                    api_version=model.config.get("api_version"),
                    temperature=client_config.temperature,
                    stop=[stop] if stop is not None else None,
                    model_kwargs=model_kwargs,
                )

            case "gcp":
                stop_arg = []
                if stop is not None:
                    stop_arg = [stop]
                # TODO: "stop" doesn't seem to work with Gemini?
                # Might be a Langchain problem, it looks as if they're not passing the stop arg on via the constructor
                # but they do pass it on when it's passed to the model call...
                return ChatGoogleGenerativeAI(
                    model=model.config.get("model"),
                    temperature=client_config.temperature,
                    stop=stop_arg,
                )

            # AWS
            case "aws":
                model_kwargs = {"temperature": client_config.temperature}
                if stop is not None:
                    model_kwargs["stop_sequences"] = [stop]
                return AWSChat(
                    model_id=model.config.get("model_id"),
                    region_name=model.config.get("region_name"),
                    model_kwargs=model_kwargs,
                )

            # OpenAI, mainly to make it easier for folks to run locally
            case "openai":
                model_kwargs = {}

                return ChatOpenAI(
                    api_key=model.config.get("api_key"),
                    model_name=model.config.get("model_name"),
                    temperature=client_config.temperature,
                    stop=[stop] if stop is not None else None,
                    model_kwargs=model_kwargs,
                )

            case "ollama":
                model_kwargs = {}
                if stop is not None:
                    model_kwargs["stop"] = [stop]
                return ChatOpenAI(
                    api_key="somerandomkey",
                    base_url=model.config.get("base_url") + "/v1",
                    model=model.config.get("model"),
                    temperature=client_config.temperature,
                    model_kwargs=model_kwargs,
                )

            case _:
                print("ERROR: unknown provider '", model.provider, "'")
