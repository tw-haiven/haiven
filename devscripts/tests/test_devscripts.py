import os
from devscripts.main import create_cli_readme


def test_create_cli_readme():
    cli_docs_start_key = "# start key"
    readme_path = "test_README.md"
    readme_content = f"""
    # Team AI CLI

    {cli_docs_start_key}
    """
    with open(readme_path, "w") as f:
        f.write(readme_content)

    docs_content_path = "test_docs_content.md"
    cli_docs_content = f"""{cli_docs_start_key}

    poetry run mkdocs build
    """
    with open(docs_content_path, "w") as f:
        f.write(cli_docs_content)

    create_cli_readme(readme_path, docs_content_path, cli_docs_start_key)

    expected_readme_content = f"""
    # Team AI CLI

    {cli_docs_start_key}

    poetry run mkdocs build
    """

    with open(readme_path, "r") as f:
        assert f.read() == expected_readme_content

    os.remove(readme_path)
    os.remove(docs_content_path)
