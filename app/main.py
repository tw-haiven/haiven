# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

import uvicorn
from dotenv import load_dotenv
from app import App
from logger import HaivenLogger


def backwards_compat_env_vars():
    # temporary support of older env vars, for backwards compatibility
    if os.environ.get("TEAM_CONTENT_PATH"):
        os.environ["KNOWLEDGE_PACK_PATH"] = os.environ["TEAM_CONTENT_PATH"]

    if os.environ.get("OLLAMA_BASE_URL"):
        os.environ["OLLAMA_HOST"] = os.environ["OLLAMA_BASE_URL"]


def create_server():
    load_dotenv()
    backwards_compat_env_vars()
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "false"
    DEFAULT_CONFIG_PATH = "config.yaml"

    HaivenLogger.get().logger.info("Starting Haiven...")
    app = App(DEFAULT_CONFIG_PATH)
    return app.launch_via_fastapi_wrapper()


def main():
    server = create_server()
    uvicorn.run(server, host="0.0.0.0", port=8080, forwarded_allow_ips="*")


if __name__ == "__main__":
    main()
