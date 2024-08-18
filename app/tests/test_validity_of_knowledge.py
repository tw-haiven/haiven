# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

import pytest
from knowledge.markdown import (
    KnowledgeBaseMarkdown,
)


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_markdown_knowledge():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    knowledge_base_markdown = KnowledgeBaseMarkdown(
        path=teams_dir + "/team_demo/knowledge"
    )

    knowledge_dict = knowledge_base_markdown.get_knowledge_content_dict()

    for key, value in knowledge_dict.items():
        assert isinstance(key, str), "Key is not a string"
        assert isinstance(value, str), "Value is not a string"
