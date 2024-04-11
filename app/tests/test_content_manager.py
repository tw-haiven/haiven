# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest.mock import MagicMock, patch
from shared.content_manager import ContentManager


class TestContentManager:
    @patch("shared.content_manager.KnowledgeBaseMarkdown")
    @patch("shared.content_manager.DocumentationBase")
    def test_init(
        self,
        DocumentationBase,
        KnowledgeBaseMarkdown,
    ):
        domain_name = "example.com"
        root_dir = "/path/to/root"

        knowledge_base_markdown = MagicMock()
        KnowledgeBaseMarkdown.return_value = knowledge_base_markdown
        documentation_base = MagicMock()
        DocumentationBase.return_value = documentation_base

        content_manager = ContentManager(domain_name, root_dir)

        KnowledgeBaseMarkdown.assert_called_with(
            team_name=domain_name, root_dir=root_dir
        )
        DocumentationBase.assert_called_with(root_dir=root_dir)

        assert content_manager.knowledge_base_markdown == knowledge_base_markdown
        assert content_manager.documentation_base == documentation_base
