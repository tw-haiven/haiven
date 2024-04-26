# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from shared.logger import TeamAILogger

from shared.embeddings import Embeddings
from shared.knowledge import KnowledgeBaseMarkdown
from shared.models.knowledge_pack import KnowledgeContext, KnowledgePack
from shared.services.config_service import ConfigService
from shared.services.embeddings_service import EmbeddingsService
from shared.user_context import UserContext

DEFAULT_CONFIG_PATH = "config.yaml"


class ContentManager:
    def __init__(
        self, knowledge_pack_path: str, config_path: str = DEFAULT_CONFIG_PATH
    ):
        self._user_context = UserContext.get_instance()

        self._config_path = config_path
        self.knowledge_pack_definition = KnowledgePack(knowledge_pack_path)

        self.knowledge_base_markdown = None
        self.knowledge_context_active = None

        self._load_base_knowledge()
        self._load_base_embeddings()
        self._pre_load_context_embeddings()

    def _load_base_knowledge(self):
        self.knowledge_base_markdown = KnowledgeBaseMarkdown(
            path=self.knowledge_pack_definition.path
        )

    def _load_base_embeddings(self):
        embedding_model = ConfigService.load_embedding_model(DEFAULT_CONFIG_PATH)
        base_embeddings_path = self.knowledge_pack_definition.path + "/embeddings"
        EmbeddingsService.initialize(Embeddings(embedding_model))

        try:
            EmbeddingsService.load_knowledge_base(base_embeddings_path)
        except FileNotFoundError as e:
            TeamAILogger.get().analytics(
                "KnowledgePackEmbeddingsNotFound", {"error": str(e)}
            )

    def _get_context(self, context_name: str) -> str:
        context = next(
            (
                context
                for context in self.knowledge_pack_definition.contexts
                if context.name == context_name
            ),
            None,
        )

        if context is None:
            TeamAILogger.get().analytics(
                "KnowledgePackContextNotFound", {"context_name": context_name}
            )
            raise KeyError(f"KnowledgePackContextNotFound: {context_name}")

        return context

    def load_context_knowledge(self, context_name: str):
        if context_name is None:
            return

        knowledge_context = self._get_context(context_name)

        context_path = (
            self.knowledge_pack_definition.path + "/contexts/" + knowledge_context.path
        )
        self.knowledge_base_markdown.set_context_content(path=context_path)

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
            TeamAILogger.get().analytics(
                "KnowledgePackEmbeddingsNotFound", {"error": str(e)}
            )

    def on_context_selected(self, context_name: str) -> str:
        self.knowledge_context_active = context_name
        try:
            self.load_context_knowledge(self.knowledge_context_active)
            return self.knowledge_context_active
        except KeyError as _:
            return None
