# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from shared.logger import HaivenLogger

from shared.embeddings.embeddings import Embeddings
from shared.knowledge.knowledge import KnowledgeBaseMarkdown
from shared.knowledge.knowledge_pack import (
    KnowledgeContext,
    KnowledgePack,
    KnowledgePackError,
)
from shared.config_service import ConfigService
from shared.embeddings.embeddings_service import EmbeddingsService

DEFAULT_CONFIG_PATH = "config.yaml"


class ContentManager:
    def __init__(
        self, knowledge_pack_path: str, config_path: str = DEFAULT_CONFIG_PATH
    ):
        if not os.path.exists(config_path):
            raise KnowledgePackError(f"Cannot find configuration file {config_path}")

        if not os.path.exists(knowledge_pack_path):
            raise KnowledgePackError(
                f"Cannot find path to Knowledge Pack: `{knowledge_pack_path}`. Please check the `knowledge_pack_path` in your {config_path} file."
            )

        self._config_path = config_path
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
        embedding_model = ConfigService.load_embedding_model(self._config_path)
        base_embeddings_path = self.knowledge_pack_definition.path + "/embeddings"
        EmbeddingsService.initialize(Embeddings(embedding_model))

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
