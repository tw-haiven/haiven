# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from config_service import ConfigService
from logger import HaivenLogger

from embeddings.client import EmbeddingsClient
from knowledge.markdown import KnowledgeBaseMarkdown
from knowledge.pack import (
    KnowledgeContext,
    KnowledgePack,
)
from knowledge.documents import KnowledgeBaseDocuments


class ContentManager:
    def __init__(self, config_service: ConfigService):
        self._config_service = config_service

        self.knowledge_pack_definition = KnowledgePack(
            config_service.load_knowledge_pack_path()
        )
        self.active_knowledge_context = None

        self.knowledge_base_markdown = self._load_base_markdown_knowledge()
        self._load_context_markdown_knowledge()

        self.knowledge_base_documents = self._load_base_documents_knowledge()
        self._load_context_documents_knowledge()

    def _load_base_markdown_knowledge(self):
        knowledge_base_markdown = KnowledgeBaseMarkdown()
        try:
            knowledge_base_markdown.load_for_base(self.knowledge_pack_definition.path)
        except FileNotFoundError as e:
            # TODO: Should this be an analytics() log?
            HaivenLogger.get().analytics(
                "KnowledgePackKnowledgeNotFound", {"error": str(e)}
            )

        return knowledge_base_markdown

    def _load_base_documents_knowledge(self):
        embedding_model = self._config_service.load_embedding_model()
        base_embeddings_path = self.knowledge_pack_definition.path + "/embeddings"

        knowledge_base_documents = KnowledgeBaseDocuments(
            self._config_service, EmbeddingsClient(embedding_model)
        )

        try:
            knowledge_base_documents.load_documents_for_base(base_embeddings_path)
        except FileNotFoundError as e:
            HaivenLogger.get().analytics(
                "KnowledgePackEmbeddingsNotFound", {"error": str(e)}
            )

        return knowledge_base_documents

    def _load_context_markdown_knowledge(self):
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
        except FileNotFoundError as e:
            HaivenLogger.get().analytics(
                "KnowledgePackContextNotFound", {"error": str(e)}
            )

    def _load_context_documents_knowledge(self):
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
            self.knowledge_base_documents.load_documents_for_context(
                knowledge_context.name, context_embeddings_path
            )
        except FileNotFoundError as e:
            HaivenLogger.get().analytics(
                "KnowledgePackEmbeddingsNotFound", {"error": str(e)}
            )

    def on_context_selected(self, context_name: str) -> str:
        self.active_knowledge_context = context_name

        return self.active_knowledge_context
