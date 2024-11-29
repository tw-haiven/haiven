# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

import uvicorn
from dotenv import load_dotenv
from app import App
from logger import HaivenLogger


def backwards_compat_env_vars():
    # temporary support of older env vars, for backwards compatibility
    if os.environ.get("TEAM_CONTENT_PATH"):
        os.environ["KNOWLEDGE_PACK_PATH"] = os.environ.get("TEAM_CONTENT_PATH", "")

    if os.environ.get("OLLAMA_BASE_URL"):
        os.environ["OLLAMA_HOST"] = os.environ.get("OLLAMA_BASE_URL", "")

    # for LiteLLM
    os.environ["AZURE_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY", "")
    os.environ["AZURE_API_BASE"] = os.environ.get("AZURE_OPENAI_API_BASE", "")
    os.environ["AZURE_API_VERSION"] = os.environ.get("AZURE_OPENAI_API_VERSION", "")
    os.environ["AWS_REGION_NAME"] = os.environ.get("AWS_BEDROCK_REGION", "")
    os.environ["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")
    os.environ["GEMINI_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")


def create_server():
    load_dotenv()
    backwards_compat_env_vars()
    DEFAULT_CONFIG_PATH = "config.yaml"

    HaivenLogger.get().logger.info("Starting Haiven...")
    app = App(DEFAULT_CONFIG_PATH)
    return app.launch_via_fastapi_wrapper()


def main():
    server = create_server()
    uvicorn.run(server, host="0.0.0.0", port=8080, forwarded_allow_ips="*")


if __name__ == "__main__":
    main()
