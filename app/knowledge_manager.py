# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

from config_service import ConfigService
from logger import HaivenLogger
from config.constants import SYSTEM_MESSAGE

from embeddings.client import EmbeddingsClient
from knowledge.markdown import KnowledgeBaseMarkdown
from knowledge.pack import (
    KnowledgeContext,
    KnowledgePack,
)
from knowledge.documents import KnowledgeBaseDocuments


class KnowledgeManager:
    def __init__(self, config_service: ConfigService):
        self._config_service = config_service

        self.knowledge_pack_definition = KnowledgePack(
            config_service.load_knowledge_pack_path()
        )

        self._load_context_markdown_knowledge()

        self.knowledge_base_documents = self._load_base_documents_knowledge()

        self.system_message = self._load_system_message()

    def _load_base_documents_knowledge(self):
        embedding_model = self._config_service.load_embedding_model()
        base_embeddings_path = self.knowledge_pack_definition.path + "/embeddings"

        knowledge_base_documents = KnowledgeBaseDocuments(
            self._config_service, EmbeddingsClient(embedding_model)
        )

        try:
            knowledge_base_documents.load_documents_for_base(base_embeddings_path)
        except FileNotFoundError as error:
            HaivenLogger.get().error(
                str(error), extra={"ERROR": "KnowledgePackEmbeddingsNotFound"}
            )

        return knowledge_base_documents

    def _load_context_markdown_knowledge(self):
        self.knowledge_base_markdown = KnowledgeBaseMarkdown()
        for context in self.knowledge_pack_definition.contexts:
            self._load_context_knowledge(context)

    def _load_context_knowledge(self, knowledge_context: KnowledgeContext):
        if knowledge_context is None:
            return

        context_path = (
            self.knowledge_pack_definition.path + "/contexts/" + knowledge_context.path
        )

        try:
            self.knowledge_base_markdown.load_for_context(
                knowledge_context.name, path=context_path
            )
        except FileNotFoundError as error:
            HaivenLogger.get().error(
                str(error), extra={"ERROR": "KnowledgePackContextNotFound"}
            )

    def _load_system_message(self):
        system_message_path = os.path.join(
            self.knowledge_pack_definition.path, "prompts", "system.md"
        )

        try:
            if os.path.exists(system_message_path):
                with open(system_message_path, "r") as file:
                    system_message = file.read().strip()
                    HaivenLogger.get().info(
                        f"Loaded custom system message from {system_message_path}",
                        extra={"INFO": "CustomSystemMessageLoaded"},
                    )
                    return system_message
        except Exception as error:
            HaivenLogger.get().error(
                str(error), extra={"ERROR": "CustomSystemMessageLoadError"}
            )

        # Return default system message if no custom one is found or if there was an error
        HaivenLogger.get().info("Using default system message")
        return SYSTEM_MESSAGE

    def get_system_message(self):
        return self.system_message
