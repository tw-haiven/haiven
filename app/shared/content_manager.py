# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from shared.knowledge import KnowledgeBaseMarkdown


class ContentManager:
    def __init__(self, path: str):
        self.knowledge_base_markdown = KnowledgeBaseMarkdown(path=path)
