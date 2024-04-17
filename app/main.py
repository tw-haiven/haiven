# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

import os

import uvicorn
from dotenv import load_dotenv
from shared.embeddings import Embeddings
from shared.app import App
from shared.chats import ServerChatSessionMemory
from shared.content_manager import ContentManager
from shared.event_handler import EventHandler
from shared.logger import TeamAILogger
from shared.navigation import NavigationManager
from shared.prompts_factory import PromptsFactory
from shared.services.config_service import ConfigService
from shared.services.embeddings_service import EmbeddingsService
from shared.ui import UI
from shared.ui_factory import UIFactory


def create_server():
    load_dotenv()
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "false"
    DEFAULT_CONFIG_PATH = "config.yaml"

    knowledge_pack = ConfigService.load_knowledge_pack(DEFAULT_CONFIG_PATH)
    embedding_model = ConfigService.load_embedding_model(DEFAULT_CONFIG_PATH)
    knowledge_base_path = knowledge_pack.path + "/" + knowledge_pack.domain.name + "/knowledge"
    EmbeddingsService.initialize(Embeddings(embedding_model))
    EmbeddingsService.load_knowledge_pack(
        knowledge_base_path + "/pdfs"
    )
    EmbeddingsService.load_knowledge_pack(
        knowledge_base_path + "/documents"
    )
    content_manager = ContentManager(knowledge_base_path)
    ui_factory = UIFactory(
        ui=UI(),
        prompts_factory=PromptsFactory(knowledge_pack.path),
        navigation_manager=NavigationManager(),
        event_handler=EventHandler(TeamAILogger),
        prompts_parent_dir=knowledge_pack.path,
        content_manager=content_manager,
        chat_session_memory=ServerChatSessionMemory(),
    )

    TeamAILogger.get().logger.info("Starting Team AI...")
    app = App(content_manager=content_manager, ui_factory=ui_factory)
    return app.launch_via_fastapi_wrapper()


def main():
    server = create_server()
    uvicorn.run(server, host="0.0.0.0", port=8080, forwarded_allow_ips="*")


if __name__ == "__main__":
    main()
