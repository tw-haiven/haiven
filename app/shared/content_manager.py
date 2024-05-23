# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from shared.logger import HaivenLogger

from shared.embeddings import Embeddings
from shared.knowledge import KnowledgeBaseMarkdown
from shared.models.knowledge_pack import KnowledgeContext, KnowledgePack
from shared.services.config_service import ConfigService
from shared.services.embeddings_service import EmbeddingsService

DEFAULT_CONFIG_PATH = "config.yaml"


class ContentManager:
    def __init__(
        self, knowledge_pack_path: str, config_path: str = DEFAULT_CONFIG_PATH
    ):
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
            HaivenLogger.get().analytics(
                "KnowledgePackKnowledgeNotFound", {"error": str(e)}
            )

    def _load_base_embeddings(self):
        embedding_model = ConfigService.load_embedding_model(DEFAULT_CONFIG_PATH)
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
