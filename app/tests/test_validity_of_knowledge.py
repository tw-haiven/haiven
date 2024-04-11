# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os

import pytest
from shared.knowledge import (
    KnowledgeBaseMarkdown,
)


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_markdown_knowledge():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    knowledge_base_markdown = KnowledgeBaseMarkdown("team_demo", root_dir=teams_dir)

    knowledge_dict = knowledge_base_markdown.get_knowledge_content_dict()

    for key, value in knowledge_dict.items():
        assert isinstance(key, str), "Key is not a string"
        assert isinstance(value, str), "Value is not a string"
