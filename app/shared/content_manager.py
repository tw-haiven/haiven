# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from shared.knowledge import (
    DocumentationBase,
    KnowledgeBaseMarkdown,
)


class ContentManager:
    def __init__(self, domain_name: str, root_dir: str):
        self.knowledge_base_markdown = KnowledgeBaseMarkdown(
            team_name=domain_name, root_dir=root_dir
        )
        self.documentation_base = DocumentationBase(root_dir=root_dir)
