# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import glob
import os
import subprocess
import sys


# sets up the environment (run once)
def app_init():
    command = """
    cd app && \
    poetry install --no-root && \
    cd .. && \
    cd ui && \
    yarn install
    """
    subprocess.run(command, shell=True)


def app_build():
    command = """
    cd ui && \
    yarn run build && \
    cp -rf out ../app/resources/static/
    """
    subprocess.run(command, shell=True)


# runs the application
def app_run():
    command = """
    cd app && \
    poetry run python main.py
    """
    subprocess.run(command, shell=True)


# runs tests
def app_test():
    command = """
    cd app && \
    poetry run pytest -m 'not integration'
    """
    subprocess.run(command, shell=True)


def app_coverage():
    command = """
    cd app && \
    poetry run pytest --cov=. --cov-report=term  -m 'not integration'
    """
    subprocess.run(command, shell=True)


# builds local docker image
def build_docker_base_image():
    command = """
    docker build -t haiven-base:local .
    """
    subprocess.run(command, shell=True)


def cli_init():
    command = """
    cd cli && \
    poetry install
    """
    subprocess.run(command, shell=True)


def cli_build():
    build_whl_command = """
    cd cli && \
    poetry install && \
    poetry build
    """
    subprocess.run(build_whl_command, shell=True)

    whl_files = glob.glob("cli/dist/*.whl")
    whl_file = whl_files[0] if whl_files else None
    if not whl_file:
        raise ValueError("poetry failed to build the whl file")

    formatted_whl_file_path = os.path.abspath(whl_file)
    with open("haiven_wheel_path.txt", "w") as f:
        f.write(formatted_whl_file_path)


def cli_run():
    arg = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1]

    command = ["poetry", "run", "python", "main.py"]

    if arg:
        command.append(arg)

    current_dir = os.getcwd()
    try:
        os.chdir(os.path.join(current_dir, "cli", "haiven_cli"))
        subprocess.run(command, check=True)
    finally:
        os.chdir(current_dir)


def cli_test():
    command = """
    cd cli && \
    poetry run pytest -vv
    """
    subprocess.run(command, shell=True)


def cli_coverage():
    command = """
    cd cli && \
    poetry run pytest --cov=. --cov-report=term  -m 'not integration'
    """
    subprocess.run(command, shell=True)


def cli_update_docs():
    cli_docs_start_key = "# `haiven-cli`"
    cli_docs_path = "cli_docs.md"
    command = f"""
    poetry install --directory=cli
    poetry run typer haiven_cli.main utils docs --output {cli_docs_path} --name haiven-cli
    """
    subprocess.run(command, shell=True)
    readme_path = "cli/README.md"
    create_cli_readme(readme_path, f"{cli_docs_path}", cli_docs_start_key)
    print(f"Removing {cli_docs_path}")
    os.remove(f"{cli_docs_path}")


def create_cli_readme(
    readme_path: str, docs_content_path: str, cli_docs_start_key: str
):
    with open(readme_path, "r") as f:
        readme_content = f.read()
    with open(docs_content_path, "r") as f:
        docs_content = f.read()

    start_index = readme_content.find(cli_docs_start_key)

    if start_index == -1:
        raise ValueError(
            f"cli docs start key {cli_docs_start_key} not found in README.md"
        )

    new_readme_content = f"{readme_content[: start_index]}{docs_content}"
    with open(readme_path, "w") as f:
        f.write(new_readme_content)
