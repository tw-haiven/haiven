# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from shared.logger import TeamAILogger

from shared.embeddings import Embeddings
from shared.knowledge import KnowledgeBaseMarkdown
from shared.models.knowledge_pack import Domain, KnowledgePack
from shared.services.config_service import ConfigService
from shared.services.embeddings_service import EmbeddingsService
from shared.user_context import UserContext

DEFAULT_CONFIG_PATH = "config.yaml"


class ContentManager:
    def __init__(
        self, knowledge_pack: KnowledgePack, config_path: str = DEFAULT_CONFIG_PATH
    ):
        self._user_context = UserContext.get_instance()

        self._knowledge_pack_definition = knowledge_pack
        self._config_path = config_path

        self.knowledge_base_markdown = None
        self.knowledge_pack_domain_active = None

        self._load_base_knowledge()
        self._load_base_embeddings()
        self._pre_load_domain_embeddings()

    def _load_base_knowledge(self):
        self.knowledge_base_markdown = KnowledgeBaseMarkdown(
            path=self._knowledge_pack_definition.path
        )

    def _load_base_embeddings(self):
        embedding_model = ConfigService.load_embedding_model(DEFAULT_CONFIG_PATH)
        base_embeddings_path = self._knowledge_pack_definition.path + "/embeddings"
        EmbeddingsService.initialize(Embeddings(embedding_model))
        EmbeddingsService.load_base_knowledge_pack(base_embeddings_path)

    def _get_domain(self, domain_name: str) -> str:
        domain = next(
            (
                domain
                for domain in self._knowledge_pack_definition.domains
                if domain.name == domain_name
            ),
            None,
        )

        if domain is None:
            TeamAILogger.get().analytics(
                "KnowledgePackDomainNotFound", {"domain_name": domain_name}
            )
            raise KeyError(f"KnowledgePackDomainNotFound: {domain_name}")

        return domain

    def load_domain_knowledge(self, domain_name: str):
        if domain_name is None:
            return

        knowledge_domain = self._get_domain(domain_name)

        domain_path = self._knowledge_pack_definition.path + "/" + knowledge_domain.path
        self.knowledge_base_markdown.set_domain_content(path=domain_path)

    def _pre_load_domain_embeddings(self):
        for domain in self._knowledge_pack_definition.domains:
            self._load_domain_embeddings(domain)

    def _load_domain_embeddings(self, domain: Domain):
        if domain is None:
            return

        domain_embeddings_path = (
            self._knowledge_pack_definition.path + "/" + domain.path + "/embeddings"
        )
        EmbeddingsService.load_domain_knowledge_pack(
            domain.name, domain_embeddings_path
        )

    def on_domain_selected(self, domain_name: str) -> str:
        self.knowledge_pack_domain_active = domain_name
        try:
            self.load_domain_knowledge(self.knowledge_pack_domain_active)
            return self.knowledge_pack_domain_active
        except KeyError as _:
            return None
