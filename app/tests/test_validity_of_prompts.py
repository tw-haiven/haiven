# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os

import pytest
from shared.knowledge import KnowledgeBaseMarkdown
from shared.prompts import PromptList


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_rendering_of_chat_prompts():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    prompt_list = PromptList(
        "chat",
        KnowledgeBaseMarkdown("team_demo", root_dir=teams_dir),
        root_dir=teams_dir,
    )

    for prompt in prompt_list.prompts:
        prompt_list.create_and_render_template(
            prompt["identifier"], {"user_input": "SOME USER INPUT"}
        )
        prompt_list.render_help_markdown(prompt["identifier"])


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_rendering_of_brainstorming_prompts():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    prompt_list = PromptList(
        "brainstorming",
        KnowledgeBaseMarkdown("team_demo", root_dir=teams_dir),
        root_dir=teams_dir,
    )

    for prompt in prompt_list.prompts:
        prompt_list.create_and_render_template(
            prompt["identifier"], {"user_input": "SOME USER INPUT"}
        )
        prompt_list.render_help_markdown(prompt["identifier"])


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_rendering_of_diagram_prompts():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    prompt_list = PromptList(
        "diagrams",
        KnowledgeBaseMarkdown("team_demo", root_dir=teams_dir),
        ["image_description"],
        root_dir=teams_dir,
    )

    for prompt in prompt_list.prompts:
        prompt_list.create_and_render_template(
            prompt["identifier"],
            {"user_input": "SOME USER INPUT", "image_description": "IMAGE DESCRIPTION"},
        )
        prompt_list.render_help_markdown(prompt["identifier"])
