# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from tests.utils import get_test_data_path
from knowledge.markdown import KnowledgeBaseMarkdown
from prompts.prompts import PromptList
from unittest.mock import MagicMock

TEST_KNOWLEDGE_PACK_PATH = get_test_data_path() + "/test_knowledge_pack"
ACTIVE_KNOWLEDGE_CONTEXT = "context_a"
CONTEXT_B = "context_b"


def create_knowledge_manager():
    return MagicMock()


def create_knowledge_base(knowledge_pack_path):
    knowledge_base = KnowledgeBaseMarkdown()
    knowledge_base.load_for_context(
        ACTIVE_KNOWLEDGE_CONTEXT,
        knowledge_pack_path + "/contexts/" + ACTIVE_KNOWLEDGE_CONTEXT + ".md",
    )
    knowledge_base.load_for_context(
        CONTEXT_B,
        knowledge_pack_path + "/contexts/" + CONTEXT_B + ".md",
    )
    return knowledge_base


def test_init_should_load_files():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    assert len(prompt_list.prompts) == 7


def test_init_should_exclude_readmes():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    assert len(prompt_list.prompts) == 7


def test_init_should_set_defaults_for_metadata():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    prompt_to_assert = next(
        filter(
            lambda prompt: prompt.metadata["identifier"] == "uuid-0",
            prompt_list.prompts,
        ),
        None,
    )
    assert prompt_to_assert.metadata["title"] == "Test0"
    assert prompt_to_assert.metadata["categories"] == []
    assert prompt_to_assert.metadata["type"] == "chat"
    assert prompt_to_assert.metadata["editable"] is False
    assert prompt_to_assert.metadata["show"] is True


def test_get_should_return_prompt_data():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    prompt = prompt_list.get("uuid-1")
    assert prompt.metadata["title"] == "Test1"


def test_create_template():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    template = prompt_list.create_template("uuid-3")
    assert template.template == "Content: {user_input} | Business: {context}"


def test_create_and_render_template_with_missing_variables():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    rendered, _ = prompt_list.create_and_render_template(
        "uuid-3",
        {"user_input": "Some User Input"},
    )
    assert (
        rendered
        == "Content: Some User Input | Business: None provided, please try to help without this information."
    )


def test_render_prompt_with_additional_vars():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    rendered, _ = prompt_list.render_prompt(
        "uuid-4",
        "Some User Input",
        {"additional": "Additional Var"},
    )
    assert rendered == "Content Some User Input Additional Var"


def test_filter_should_filter_by_one_category_and_include_without_category():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    prompt_list.filter(["architecture"])
    assert len(prompt_list.prompts) == 4


def test_filter_should_filter_by_multiple_categories():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    prompt_list.filter(["architecture", "coding"])
    assert len(prompt_list.prompts) == 5


def test_render_prompt_without_prompt_choice():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()
    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    rendered, _ = prompt_list.render_prompt(None, "Some User Input")
    assert rendered == ""


def test_create_markdown_summary():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    markdown_summary = prompt_list.render_prompts_summary_markdown()

    expected_summary = (
        "- **Test4**: Prompt description 4\n" "- **Test5**: Prompt description 5\n"
    )

    assert expected_summary in markdown_summary


def test_get_prompts_with_follow_ups():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    prompts_with_follow_ups = prompt_list.get_prompts_with_follow_ups()

    uuid_1_entry = [
        prompt for prompt in prompts_with_follow_ups if prompt["identifier"] == "uuid-1"
    ][0]
    assert uuid_1_entry is not None
    assert len(uuid_1_entry["follow_ups"]) == 2
    assert "grounded" in uuid_1_entry
    assert uuid_1_entry["grounded"] is False
    assert uuid_1_entry["follow_ups"][0]["identifier"] == "uuid-2"
    assert uuid_1_entry["follow_ups"][0]["title"] == "Test2"
    assert "prompt 2" in uuid_1_entry["follow_ups"][0]["help_prompt_description"]
    assert uuid_1_entry["follow_ups"][1]["identifier"] == "uuid-3"
    assert uuid_1_entry["follow_ups"][1]["title"] == "Test3"
    assert "prompt 3" in uuid_1_entry["follow_ups"][1]["help_prompt_description"]

    uuid_3_entry = [
        prompt for prompt in prompts_with_follow_ups if prompt["identifier"] == "uuid-3"
    ][0]
    assert uuid_3_entry is not None
    assert uuid_3_entry["follow_ups"] == []


def test_get_prompts_with_follow_ups_invalid_prompt_id():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )
    prompts_with_follow_ups = prompt_list.get_prompts_with_follow_ups()

    # test knowledge pack configures invalid follow-up and valid follow-up for uuid-2

    uuid_2_entry = [
        prompt for prompt in prompts_with_follow_ups if prompt["identifier"] == "uuid-2"
    ][0]
    assert uuid_2_entry is not None
    assert len(uuid_2_entry["follow_ups"]) == 1
    assert uuid_2_entry["follow_ups"][0]["identifier"] == "uuid-3"


def test_get_prompts_with_follow_ups_with_categor_and_includeContent():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    knowledge_manager = create_knowledge_manager()

    prompt_list = PromptList(
        "chat", knowledge_base, knowledge_manager, root_dir=TEST_KNOWLEDGE_PACK_PATH
    )

    # Get prompts with category "architecture" and includeContent=True
    prompts_with_follow_ups = prompt_list.get_prompts_with_follow_ups(
        includeContent=True, category="architecture"
    )

    # Verify only prompts with "architecture" category are returned
    assert all(
        "architecture" in prompt["categories"] for prompt in prompts_with_follow_ups
    )

    # Verify content is included in the response
    uuid_1_entry = [
        prompt for prompt in prompts_with_follow_ups if prompt["identifier"] == "uuid-1"
    ][0]
    assert uuid_1_entry["content"] == "Content {user_input} {context}"

    uuid_5_entry = [
        prompt for prompt in prompts_with_follow_ups if prompt["identifier"] == "uuid-5"
    ][0]
    assert uuid_5_entry["content"] == "Content  {context}"
