# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest.mock import MagicMock, patch
from shared.content_manager import ContentManager


class TestContentManager:
    @patch("shared.content_manager.KnowledgeBaseMarkdown")
    def test_init(
        self,
        KnowledgeBaseMarkdown,
    ):
        domain_name = "example.com"
        root_dir = "/path/to/root"

        knowledge_base_markdown = MagicMock()
        KnowledgeBaseMarkdown.return_value = knowledge_base_markdown

        knoeledge_path = root_dir + "/" + domain_name + "/knowledge"
        content_manager = ContentManager(knoeledge_path)

        KnowledgeBaseMarkdown.assert_called_with(path=knoeledge_path)

        assert content_manager.knowledge_base_markdown == knowledge_base_markdown
