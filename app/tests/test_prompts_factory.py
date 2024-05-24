# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import call, patch, MagicMock
from shared.prompts_factory import PromptsFactory


class TestPromptsFactory:
    @patch("shared.prompts_factory.PromptList")
    def test_create_all_prompts(self, prompt_list_mock):
        chat_prompt = MagicMock(name="chat_prompt")
        brainstorming_prompt = MagicMock(name="brainstorming_prompt")
        diagrams_prompt = MagicMock(name="diagrams_prompt")

        def mock_prompt_list_init(*args, **kwargs):
            if args[0] == "chat":
                return chat_prompt
            elif args[0] == "brainstorming":
                return brainstorming_prompt
            elif args[0] == "diagrams":
                return diagrams_prompt

        prompt_list_mock.side_effect = mock_prompt_list_init
        knowledge_base_markdown = MagicMock()
        prompts_parent_dir = "test_prompts_parent_dir"

        prompts = PromptsFactory(prompts_parent_dir).create_all_prompts(
            knowledge_base_markdown
        )

        assert chat_prompt in prompts
        assert brainstorming_prompt in prompts
        assert diagrams_prompt in prompts
        prompt_list_mock.assert_has_calls(
            [
                call("chat", knowledge_base_markdown, root_dir=prompts_parent_dir),
                call(
                    "brainstorming",
                    knowledge_base_markdown,
                    root_dir=prompts_parent_dir,
                ),
                call("diagrams", knowledge_base_markdown, root_dir=prompts_parent_dir),
            ]
        )

    @patch("shared.prompts_factory.PromptList")
    def test_create_brainstorming_prompt(self, prompt_list_mock):
        brainstorming_prompt = MagicMock(name="brainstorming_prompt")
        prompt_list_mock.return_value = brainstorming_prompt
        knowledge_base_markdown = MagicMock()
        prompts_parent_dir = "test_prompts_parent_dir"

        prompt = PromptsFactory(prompts_parent_dir).create_brainstorming_prompt(
            knowledge_base_markdown
        )

        assert brainstorming_prompt == prompt
        assert prompt_list_mock.call_args == call(
            "brainstorming", knowledge_base_markdown, root_dir=prompts_parent_dir
        )

    @patch("shared.prompts_factory.PromptList")
    def test_create_chat_prompt(self, prompt_list_mock):
        chat_prompt = MagicMock(name="chat_prompt")
        prompt_list_mock.return_value = chat_prompt
        knowledge_base_markdown = MagicMock()
        prompts_parent_dir = "test_prompts_parent_dir"

        prompt = PromptsFactory(prompts_parent_dir).create_chat_prompt(
            knowledge_base_markdown
        )

        assert chat_prompt == prompt
        assert prompt_list_mock.call_args == call(
            "chat", knowledge_base_markdown, root_dir=prompts_parent_dir
        )

    @patch("shared.prompts_factory.PromptList")
    def test_create_diagrams_prompt(self, prompt_list_mock):
        diagrams_prompt = MagicMock(name="diagrams_prompt")
        prompt_list_mock.return_value = diagrams_prompt
        knowledge_base_documents = MagicMock()
        variables = ["image_description"]
        prompts_parent_dir = "test_prompts_parent_dir"

        prompt = PromptsFactory(prompts_parent_dir).create_diagrams_prompt(
            knowledge_base_documents, variables
        )

        assert diagrams_prompt == prompt
        assert prompt_list_mock.call_args == call(
            "diagrams",
            knowledge_base_documents,
            variables=variables,
            root_dir=prompts_parent_dir,
        )
