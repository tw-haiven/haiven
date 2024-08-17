# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

import uvicorn
from dotenv import load_dotenv
from app import App
from llms.chats import ServerChatSessionMemory
from content_manager import ContentManager
from ui.event_handler import EventHandler
from logger import HaivenLogger
from ui.navigation import NavigationManager
from prompts.prompts_factory import PromptsFactory
from config_service import ConfigService
from ui.ui import UIBaseComponents
from ui.ui_factory import UIFactory


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

    # preparing for ConfigService to not be static anymore
    config_service = ConfigService(DEFAULT_CONFIG_PATH)

    knowledge_pack_path = config_service.load_knowledge_pack_path()
    content_manager = ContentManager(config_service=config_service)

    prompts_factory = PromptsFactory(knowledge_pack_path)
    chat_session_memory = ServerChatSessionMemory()

    ui_factory = UIFactory(
        ui_base_components=UIBaseComponents(),
        prompts_factory=prompts_factory,
        navigation_manager=NavigationManager(),
        event_handler=EventHandler(HaivenLogger),
        prompts_parent_dir=knowledge_pack_path,
        content_manager=content_manager,
        chat_session_memory=chat_session_memory,
    )

    HaivenLogger.get().logger.info("Starting Haiven...")
    app = App(
        content_manager=content_manager,
        config_service=config_service,
        prompts_factory=prompts_factory,
        chat_session_memory=chat_session_memory,
        ui_factory=ui_factory,
    )
    return app.launch_via_fastapi_wrapper()


def main():
    server = create_server()
    uvicorn.run(server, host="0.0.0.0", port=8080, forwarded_allow_ips="*")


if __name__ == "__main__":
    main()
