# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from tests.utils import get_test_data_path
from shared.knowledge import KnowledgeBaseMarkdown
from shared.prompts import PromptList


ACTIVE_KNOWLEDGE_CONTEXT = "context_a"
TEST_KNOWLEDGE_PACK_PATH = get_test_data_path() + "/test_knowledge_pack"


def create_knowledge_base(knowledge_pack_path):
    knowledge_base = KnowledgeBaseMarkdown()
    knowledge_base.load_context_knowledge(
        ACTIVE_KNOWLEDGE_CONTEXT,
        knowledge_pack_path + "/contexts/" + ACTIVE_KNOWLEDGE_CONTEXT,
    )

    return knowledge_base


def test_init_should_load_files():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    assert len(prompt_list.prompts) == 6


def test_init_should_exclude_readmes():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    assert len(prompt_list.prompts) == 6


def test_init_should_set_defaults_for_metadata():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    prompt_to_assert = next(
        filter(
            lambda prompt: prompt.metadata["identifier"] == "uuid-0",
            prompt_list.prompts,
        ),
        None,
    )
    assert prompt_to_assert.metadata["title"] == "Test0"
    assert prompt_to_assert.metadata["system"] == "You are a useful assistant"
    assert prompt_to_assert.metadata["categories"] == []


def test_init_should_load_all_metadata():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    prompt_to_assert = next(
        filter(
            lambda prompt: prompt.metadata["identifier"] == "uuid-3",
            prompt_list.prompts,
        ),
        None,
    )
    assert prompt_to_assert.metadata["system"] == "Some system message"


def test_get_title_id_tuples():
    # chat_prompts_dir = create_prompts_directory(xtmpdir)
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    titles = prompt_list.get_title_id_tuples()
    assert titles == [
        ("Test0", "uuid-0"),
        ("Test1", "uuid-1"),
        ("Test2", "uuid-2"),
        ("Test3", "uuid-3"),
        ("Test4", "uuid-4"),
        ("Test5", "uuid-5"),
    ]


def test_get_should_return_prompt_data():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    prompt = prompt_list.get("uuid-1")
    assert prompt.metadata["title"] == "Test1"


def test_create_template():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    template = prompt_list.create_template(ACTIVE_KNOWLEDGE_CONTEXT, "uuid-3")
    assert template.template == "Content: {user_input} | Business: {business}"


def test_create_and_render_template():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    template, rendered = prompt_list.create_and_render_template(
        ACTIVE_KNOWLEDGE_CONTEXT, "uuid-3", {"user_input": "Some User Input"}
    )
    assert template.template == "Content: {user_input} | Business: {business}"
    assert (
        rendered
        == "Content: Some User Input | Business: Business knowledge from context_a"
    )


def test_create_and_render_template_with_missing_variables():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    _, rendered = prompt_list.create_and_render_template(
        None,
        "uuid-3",
        {"user_input": "Some User Input"},
    )
    assert (
        rendered
        == "Content: Some User Input | Business: None provided, please try to help without this information."
    )


def test_create_and_render_template_overwrite_knowledge_base():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    _, rendered = prompt_list.create_and_render_template(
        ACTIVE_KNOWLEDGE_CONTEXT,
        "uuid-3",
        {"user_input": "Some User Input", "business": "Overwritten Business"},
    )
    assert rendered == "Content: Some User Input | Business: Overwritten Business"


def test_render_prompt_with_additional_vars():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    rendered = prompt_list.render_prompt(
        ACTIVE_KNOWLEDGE_CONTEXT,
        "uuid-4",
        "Some User Input",
        {"additional": "Additional Var"},
    )
    assert rendered == "Content Some User Input Additional Var"


def test_filter_should_filter_by_one_category_and_include_wihtout_category():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    prompt_list.filter(["architecture"])
    assert len(prompt_list.prompts) == 3


def test_filter_should_filter_by_multiple_categories():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    prompt_list.filter(["architecture", "coding"])
    assert len(prompt_list.prompts) == 4


def test_render_prompt_without_prompt_choice():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)
    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    rendered = prompt_list.render_prompt(
        ACTIVE_KNOWLEDGE_CONTEXT, None, "Some User Input"
    )
    assert rendered == ""


def test_render_help_markdown():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    help, knowledge = prompt_list.render_help_markdown(
        "uuid-5", ACTIVE_KNOWLEDGE_CONTEXT
    )
    assert "Prompt description" in help
    assert "User input description" in help
    assert "Architecture Knowledge" in knowledge
    assert "Business Knowledge" in knowledge


def test_render_help_markdown_when_values_are_empty():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    help, knowledge = prompt_list.render_help_markdown(
        "uuid-1", ACTIVE_KNOWLEDGE_CONTEXT
    )
    assert "## Test1" in help
    assert "Architecture Knowledge" in knowledge


def test_create_markdown_summary():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    markdown_summary = prompt_list.render_prompts_summary_markdown()

    expected_summary = (
        "- **Test4**: Prompt description 4\n" "- **Test5**: Prompt description 5\n"
    )

    assert markdown_summary == expected_summary


def test_get_knowledge_used():
    knowledge_base = create_knowledge_base(TEST_KNOWLEDGE_PACK_PATH)

    prompt_list = PromptList("chat", knowledge_base, root_dir=TEST_KNOWLEDGE_PACK_PATH)
    vars = prompt_list.get_knowledge_used("uuid-5", ACTIVE_KNOWLEDGE_CONTEXT)
    assert len(vars) == 2
    assert {"key": "business", "title": "Business Knowledge"} in vars
    assert {"key": "architecture", "title": "Architecture Knowledge"} in vars
