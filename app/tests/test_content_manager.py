# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest.mock import MagicMock, patch
from shared.content_manager import ContentManager


class TestContentManager:
    @patch("shared.content_manager.KnowledgeBaseMarkdown")
    @patch("shared.content_manager.KnowledgeBasePDFs")
    @patch("shared.content_manager.KnowledgeBaseDocuments")
    @patch("shared.content_manager.DocumentationBase")
    def test_init(
        self,
        DocumentationBase,
        KnowledgeBaseDocuments,
        KnowledgeBasePDFs,
        KnowledgeBaseMarkdown,
    ):
        domain_name = "example.com"
        root_dir = "/path/to/root"

        knowledge_base_markdown = MagicMock()
        KnowledgeBaseMarkdown.return_value = knowledge_base_markdown
        knowledge_base_pdfs = MagicMock()
        KnowledgeBasePDFs.return_value = knowledge_base_pdfs
        knowledge_base_documents = MagicMock()
        KnowledgeBaseDocuments.return_value = knowledge_base_documents
        documentation_base = MagicMock()
        DocumentationBase.return_value = documentation_base

        content_manager = ContentManager(domain_name, root_dir)

        KnowledgeBaseMarkdown.assert_called_with(
            team_name=domain_name, root_dir=root_dir
        )
        KnowledgeBasePDFs.assert_called_with(team_name=domain_name, root_dir=root_dir)
        KnowledgeBaseDocuments.assert_called_with(
            team_name=domain_name, root_dir=root_dir
        )
        DocumentationBase.assert_called_with(root_dir=root_dir)

        assert content_manager.knowledge_base_markdown == knowledge_base_markdown
        assert content_manager.knowledge_base_pdfs == knowledge_base_pdfs
        assert content_manager.knowledge_base_documents == knowledge_base_documents
        assert content_manager.documentation_base == documentation_base
