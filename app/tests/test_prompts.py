# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from shared.knowledge import KnowledgeBaseMarkdown
from shared.prompts import PromptList
import tempfile


def create_base_prompts_directory(tmpdir):
    prompts_dir = os.path.join(tmpdir, "base-prompts")
    os.makedirs(prompts_dir)
    chat_prompts_dir = os.path.join(prompts_dir, "chat")
    os.makedirs(chat_prompts_dir)
    return chat_prompts_dir


def create_some_prompt_files(tmpdir, count=3):
    chat_prompts_dir = create_base_prompts_directory(tmpdir)
    for i in range(count):
        with open(os.path.join(chat_prompts_dir, f"test{i}.md"), "w") as f:
            f.write(f"---\nidentifier: uuid-{i}\ntitle: Test{i}\n---\nContent")
    return chat_prompts_dir


def create_knowledge_base(tmpdir):
    team_dir = os.path.join(tmpdir, "team_test")
    os.makedirs(team_dir)
    knowledge_dir = os.path.join(team_dir, "knowledge")
    os.makedirs(knowledge_dir)

    with open(os.path.join(knowledge_dir, "business_context.md"), "w") as f:
        f.write(
            "---\nkey: business\ntitle: Business Knowledge\n---\n\nbusiness knowledge"
        )
    with open(os.path.join(knowledge_dir, "architecture.md"), "w") as f:
        f.write(
            "---\nkey: architecture\ntitle: Architecture Knowledge\n---\n\narchitecture knowledge"
        )
    with open(os.path.join(knowledge_dir, "frontend_coding_patterns.md"), "w") as f:
        f.write(
            "---\nkey: frontend_coding_patterns\n---\n\nfrontend coding patterns knowledge"
        )

    return KnowledgeBaseMarkdown(path=tmpdir + "/team_test/knowledge")


def test_init_should_load_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        create_some_prompt_files(tmpdir, 3)

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        assert len(prompt_list.prompts) == 3
        assert set(prompt_list.variables) == {
            "user_input",
            "business",
            "architecture",
            "frontend_coding_patterns",
        }


def test_init_should_exclude_readmes():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        create_some_prompt_files(tmpdir, 2)
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("""Readme""")

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        assert len(prompt_list.prompts) == 2


def test_init_should_set_defaults_for_metadata():
    with tempfile.TemporaryDirectory() as tmpdir:
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        knowledge_base = create_knowledge_base(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test0.md"), "w") as f:
            f.write("""---\ntitle: Test0\n---\nContent""")

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        assert prompt_list.prompts[0].metadata["title"] == "Test0"
        assert prompt_list.prompts[0].metadata["system"] == "You are a useful assistant"
        assert prompt_list.prompts[0].metadata["categories"] == []


def test_init_should_load_all_metadata():
    with tempfile.TemporaryDirectory() as tmpdir:
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        knowledge_base = create_knowledge_base(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write("""---
title: Test
system: "Some system message"
---
Content {user_input}
                    """)

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        assert prompt_list.prompts[0].metadata["system"] == "Some system message"


def test_get_title_id_tuples():
    with tempfile.TemporaryDirectory() as xtmpdir:
        # chat_prompts_dir = create_prompts_directory(xtmpdir)
        knowledge_base = create_knowledge_base(xtmpdir)
        chat_dir = create_some_prompt_files(xtmpdir, 3)
        with open(os.path.join(chat_dir, "additional-prompt.md"), "w") as f:
            f.write(
                """---\nidentifier: uuid-alphabet\ntitle: A in the Alphabet\n---\nContent"""
            )

        prompt_list = PromptList("chat", knowledge_base, root_dir=xtmpdir)
        titles = prompt_list.get_title_id_tuples()
        assert titles == [
            ("A in the Alphabet", "uuid-alphabet"),
            ("Test0", "uuid-0"),
            ("Test1", "uuid-1"),
            ("Test2", "uuid-2"),
        ]


def test_get_should_return_prompt_data():
    with tempfile.TemporaryDirectory() as xtmpdir:
        tmpdir = create_base_prompts_directory(xtmpdir)
        knowledge_base = create_knowledge_base(tmpdir)
        create_some_prompt_files(tmpdir, 3)

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        prompt = prompt_list.get("uuid-1")
        assert prompt.metadata["title"] == "Test1"


def test_create_template():
    with tempfile.TemporaryDirectory() as tmpdir:
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        knowledge_base = create_knowledge_base(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write("---\nidentifier: uuid-x\ntitle: Test\n---\nContent")

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        template = prompt_list.create_template("uuid-x")
        assert template.template == "Content"


def test_create_and_render_template():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write("---\nidentifier: uuid-x\ntitle: Test\n---\nContent {user_input}")

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        template, rendered = prompt_list.create_and_render_template(
            "uuid-x", {"user_input": "Some User Input"}
        )
        assert template.template == "Content {user_input}"
        assert rendered == "Content Some User Input"


def test_create_and_render_template_use_knowledge_base():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write(
                "---\nidentifier: uuid-x\ntitle: Test\n---\nContent: {user_input} | Business: {business}"
            )

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        _, rendered = prompt_list.create_and_render_template(
            "uuid-x", {"user_input": "Some User Input"}
        )
        assert rendered == "Content: Some User Input | Business: business knowledge"


def test_create_and_render_template_overwrite_knowledge_base():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write(
                "---\nidentifier: uuid-x\ntitle: Test\n---\nContent: {user_input} | Business: {business}"
            )

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        _, rendered = prompt_list.create_and_render_template(
            "uuid-x",
            {"user_input": "Some User Input", "business": "Overwritten Business"},
        )
        assert rendered == "Content: Some User Input | Business: Overwritten Business"


def test_filter_should_filter_by_one_category():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test1.md"), "w") as f:
            f.write("""---
title: 'Some title 1'
categories: ['architecture']
---
Content {user_input}
                    """)
        with open(os.path.join(tmpdir, "test2.md"), "w") as f:
            f.write("""---
title: 'Some title 2'
categories: ['coding']
---
Content {user_input}
                    """)

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        prompt_list.filter(["architecture"])
        assert len(prompt_list.prompts) == 1


def test_filter_should_filter_by_multiple_categories():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test1.md"), "w") as f:
            f.write("""---
title: 'Some title 1'
categories: ['architecture']
---
Content {user_input}
                    """)
        with open(os.path.join(chat_prompts_dir, "test2.md"), "w") as f:
            f.write("""---
title: 'Some title 2'
categories: ['coding']
---
Content {user_input}
                    """)
        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        prompt_list.filter(["architecture", "coding"])
        assert len(prompt_list.prompts) == 2


def test_filter_should_always_include_all_without_categories():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write("""---
title: 'Some title 1'
---
Content {user_input}
                    """)

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        prompt_list.filter(["architecture"])
        assert len(prompt_list.prompts) == 1


def test_render_prompt_with_business_context():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)

        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write(
                "---\nidentifier: uuid-x\ntitle: Test\n---\nContent {user_input} {business}"
            )

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        rendered = prompt_list.render_prompt("uuid-x", "Some User Input")
        assert rendered == "Content Some User Input business knowledge"


def test_render_prompt_with_architecture_context():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write(
                "---\nidentifier: uuid-x\ntitle: Test\n---\nContent {user_input} {architecture}"
            )

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        rendered = prompt_list.render_prompt("uuid-x", "Some User Input")
        assert rendered == "Content Some User Input architecture knowledge"


def test_render_prompt_with_additional_vars():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write(
                "---\nidentifier: uuid-x\ntitle: Test\n---\nContent {user_input} {business} {additional}"
            )

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        rendered = prompt_list.render_prompt(
            "uuid-x", "Some User Input", {"additional": "Additional Var"}
        )
        assert rendered == "Content Some User Input business knowledge Additional Var"


def test_render_prompt_without_prompt_choice():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        create_base_prompts_directory(tmpdir)
        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        rendered = prompt_list.render_prompt(None, "Some User Input")
        assert rendered == ""


def test_render_help_markdown():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write(
                "---\nidentifier: uuid-x\ntitle: Test\nhelp_user_input: User input description \nhelp_prompt_description: Prompt description\n---\nContent {business}"
            )

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        help, knowledge = prompt_list.render_help_markdown("uuid-x")
        assert (
            help
            == "## Test\n**Description:** Prompt description\n\n**User input:** User input description\n\n"
        )
        assert knowledge == "**Knowledge used:** Business Knowledge"


def test_render_help_markdown_when_values_are_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test.md"), "w") as f:
            f.write("---\nidentifier: uuid-x\ntitle: Test\n---\nContent")

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        help, knowledge = prompt_list.render_help_markdown("uuid-x")
        assert help == "## Test\n\n\n\n\n"
        assert knowledge == ""


def test_create_markdown_summary():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "prompt1.md"), "w") as f:
            f.write(
                "---\ntitle: Prompt 1\nhelp_user_input: User input description 1\nhelp_prompt_description: Prompt description 1\n---\nContent 1"
            )
        with open(os.path.join(chat_prompts_dir, "prompt2.md"), "w") as f:
            f.write(
                "---\ntitle: Prompt 2\nhelp_user_input: User input description 2\nhelp_prompt_description: Prompt description 2\n---\nContent 2"
            )

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        markdown_summary = prompt_list.render_prompts_summary_markdown()

        expected_summary = (
            "- **Prompt 1**: Prompt description 1\n"
            "- **Prompt 2**: Prompt description 2\n"
        )

        assert markdown_summary == expected_summary


def test_get_knowledge_used():
    with tempfile.TemporaryDirectory() as tmpdir:
        knowledge_base = create_knowledge_base(tmpdir)
        chat_prompts_dir = create_base_prompts_directory(tmpdir)
        with open(os.path.join(chat_prompts_dir, "test1.md"), "w") as f:
            f.write("""---
identifier: 'test1'
title: 'Some title 1'
categories: ['architecture']
---
Content {user_input}
                    {business}
                    {architecture}
                    """)

        prompt_list = PromptList("chat", knowledge_base, root_dir=tmpdir)
        vars = prompt_list.get_knowledge_used("test1")
        assert len(vars) == 2
        assert {"key": "business", "title": "Business Knowledge"} in vars
        assert {"key": "architecture", "title": "Architecture Knowledge"} in vars
