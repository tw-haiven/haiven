# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from config_service import ConfigService
from logger import HaivenLogger

from embeddings.client import EmbeddingsClient
from knowledge.knowledge import KnowledgeBaseMarkdown
from knowledge.knowledge_pack import (
    KnowledgeContext,
    KnowledgePack,
)
from embeddings.service import EmbeddingsService

DEFAULT_CONFIG_PATH = "config.yaml"


class ContentManager:
    def __init__(self, config_service: ConfigService):
        knowledge_pack_path = config_service.load_knowledge_pack_path()

        self._config_service = config_service
        self.knowledge_pack_definition = KnowledgePack(knowledge_pack_path)

        self.knowledge_base_markdown = None
        self.active_knowledge_context = None

        self._load_base_knowledge()
        self._pre_load_context_knowledge()
        self._load_base_embeddings()
        self._pre_load_context_embeddings()

    def _load_base_knowledge(self):
        self.knowledge_base_markdown = KnowledgeBaseMarkdown()
        try:
            self.knowledge_base_markdown.load_base_knowledge(
                self.knowledge_pack_definition.path
            )
        except FileNotFoundError as e:
            # TODO: Should this be an analytics() log?
            HaivenLogger.get().analytics(
                "KnowledgePackKnowledgeNotFound", {"error": str(e)}
            )

    def _load_base_embeddings(self):
        embedding_model = self._config_service.load_embedding_model()
        base_embeddings_path = self.knowledge_pack_definition.path + "/embeddings"
        EmbeddingsService.initialize(
            EmbeddingsClient(embedding_model), self._config_service
        )

        try:
            EmbeddingsService.load_knowledge_base(base_embeddings_path)
        except FileNotFoundError as e:
            HaivenLogger.get().analytics(
                "KnowledgePackEmbeddingsNotFound", {"error": str(e)}
            )

    def _pre_load_context_knowledge(self):
        for context in self.knowledge_pack_definition.contexts:
            self._load_context_knowledge(context)

    def _load_context_knowledge(self, knowledge_context: KnowledgeContext):
        if knowledge_context is None:
            return

        context_path = (
            self.knowledge_pack_definition.path + "/contexts/" + knowledge_context.path
        )

        try:
            self.knowledge_base_markdown.load_context_knowledge(
                knowledge_context.name, path=context_path
            )
        except FileNotFoundError as e:
            HaivenLogger.get().analytics(
                "KnowledgePackContextNotFound", {"error": str(e)}
            )

    def _pre_load_context_embeddings(self):
        for context in self.knowledge_pack_definition.contexts:
            self._load_context_embeddings(context)

    def _load_context_embeddings(self, knowledge_context: KnowledgeContext):
        if knowledge_context is None:
            return

        context_embeddings_path = (
            self.knowledge_pack_definition.path
            + "/contexts/"
            + knowledge_context.path
            + "/embeddings"
        )

        try:
            EmbeddingsService.load_knowledge_context(
                knowledge_context.name, context_embeddings_path
            )
        except FileNotFoundError as e:
            HaivenLogger.get().analytics(
                "KnowledgePackEmbeddingsNotFound", {"error": str(e)}
            )

    def on_context_selected(self, context_name: str) -> str:
        self.active_knowledge_context = context_name

        return self.active_knowledge_context
