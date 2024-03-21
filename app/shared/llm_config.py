# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from langchain_community.chat_models import BedrockChat, ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from shared.logger import TeamAILogger
from shared.models.model import Model
from shared.services.models_service import ModelsService


class LLMConfig:
    def __init__(self, init_service_name: str, init_temperature: float):
        self.service_name: str = init_service_name
        self.temperature: float = init_temperature

    def change_model(self, new_value: str):
        self.service_name = new_value

    def change_temperature(self, new_tone: float):
        self.temperature = new_tone

    def supports_system_messages(self) -> bool:
        if self.service_name == "google-gemini":
            return False
        return True


class LLMChatFactory:
    @staticmethod
    def new_llm_chat(llm_config: LLMConfig, stop=None) -> BaseChatModel:
        model: Model = ModelsService.get_model(llm_config.service_name)

        TeamAILogger.get().analytics(
            "Model selected",
            {
                "provider": model.provider,
                "model": model.id,
                "temperature": llm_config.temperature,
            },
        )

        match model.provider.lower():
            case "azure":
                model_kwargs = {}
                if stop is not None:
                    model_kwargs["stop"] = [stop]

                return AzureChatOpenAI(
                    openai_api_key=model.config.get("api_key"),
                    azure_deployment=model.config.get("azure_deployment"),
                    azure_endpoint=model.config.get("azure_endpoint"),
                    api_version=model.config.get("api_version"),
                    temperature=llm_config.temperature,
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
                    temperature=llm_config.temperature,
                    stop=stop_arg,
                )

            # AWS
            case "aws":
                model_kwargs = {"temperature": llm_config.temperature}
                if stop is not None:
                    model_kwargs["stop_sequences"] = [stop]
                return BedrockChat(
                    model_id=model.config.get("model_id"),
                    region_name=model.config.get("region_name"),
                    model_kwargs=model_kwargs,
                )

            # OpenAI, mainly to make it easier for folks to run locally
            case "openai":
                model_kwargs = {}
                if stop is not None:
                    model_kwargs["stop"] = [stop]
                return ChatOpenAI(
                    api_key=model.config.get("api_key"),
                    model_name=model.config.get("model_name"),
                    temperature=llm_config.temperature,
                    model_kwargs=model_kwargs,
                )

            case "lmstudio":
                model_kwargs = {}
                if stop is not None:
                    model_kwargs["stop"] = [stop]
                return ChatOpenAI(
                    api_key="",  # LMStudio doesn't need an API key
                    base_url=model.config.get("base_url"),
                    model_name=model.config.get("model_name"),
                    temperature=llm_config.temperature,
                    model_kwargs=model_kwargs,
                )

            case "ollama":
                model_kwargs = {}
                if stop is not None:
                    model_kwargs["stop"] = [stop]
                return ChatOllama(
                    base_url=model.config.get("base_url"),
                    model=model.config.get("model"),
                    temperature=llm_config.temperature,
                    model_kwargs=model_kwargs,
                )

            case _:
                print("ERROR: unknown provider '", model.provider, "'")
