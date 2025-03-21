# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

import pytest
from knowledge.markdown import KnowledgeBaseMarkdown
from prompts.prompts import PromptList


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_rendering_of_chat_prompts():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    prompt_list = PromptList(
        "chat",
        KnowledgeBaseMarkdown(path=teams_dir + "/team_demo/knowledge"),
        root_dir=teams_dir,
    )

    for prompt in prompt_list.prompts:
        prompt_list.create_and_render_template(
            prompt["identifier"], {"user_input": "SOME USER INPUT"}
        )


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_rendering_of_brainstorming_prompts():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    prompt_list = PromptList(
        "brainstorming",
        KnowledgeBaseMarkdown(path=teams_dir + "/team_demo/knowledge"),
        root_dir=teams_dir,
    )

    for prompt in prompt_list.prompts:
        prompt_list.create_and_render_template(
            prompt["identifier"], {"user_input": "SOME USER INPUT"}
        )


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_rendering_of_diagram_prompts():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    prompt_list = PromptList(
        "diagrams",
        KnowledgeBaseMarkdown(path=teams_dir + "/team_demo/knowledge"),
        ["image_description"],
        root_dir=teams_dir,
    )

    for prompt in prompt_list.prompts:
        prompt_list.create_and_render_template(
            prompt["identifier"],
            {"user_input": "SOME USER INPUT", "image_description": "IMAGE DESCRIPTION"},
        )
