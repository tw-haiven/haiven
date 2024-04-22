# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
import subprocess
import sys


# sets up the environment (run once)
def app_init():
    command = """
    cd app && \
    poetry install --no-root
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
def build_docker_image():
    command = """
    cd app && \
    docker build -t team-ai-base:local .
    cd demo-knowledge-pack && \
    docker build --build-arg REGISTRY_URL= --build-arg TAG=local -t team-ai-demo:local .
    """
    subprocess.run(command, shell=True)


# runs local docker image
def run_docker_image():
    command = """
    docker inspect --type=image team-ai-demo:local && \
    cd app && \
    docker run --env-file .env -e TEAM_CONTENT_PATH=teams -p 8080:8080 team-ai-demo:local
    """
    subprocess.run(command, shell=True)


def run_docker_prod_image():
    command = """
    cd app && \
    docker run --env-file .env -e TEAM_CONTENT_PATH=teams -p 8080:8080 us-central1-docker.pkg.dev/team-ai-7a96/team-ai/team-ai-demo:main
    """
    subprocess.run(command, shell=True)


# retrieve secrets (requires gcloud to be logged in team-ai-7a96)
def get_secret():
    command = f"""
    gcloud secrets versions access latest --secret={sys.argv[1]}
    """
    subprocess.run(command, shell=True)


def cli_init():
    command = """
    cd cli && \
    poetry install
    """
    subprocess.run(command, shell=True)


def cli_install():
    command = """
    cd cli && \
    poetry install && \
    poetry build && \
    pip install dist/teamai_cli-0.1.0-py3-none-any.whl --force-reinstall
    """
    subprocess.run(command, shell=True)


def cli_run():
    arg = ""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    command = f"""
    cd cli/teamai_cli && \
    poetry run python main.py {arg}
    """
    subprocess.run(command, shell=True)


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
    cli_docs_start_key = "# `teamai-cli`"
    cli_docs_path = "cli_docs.md"
    command = f"""
    poetry install --directory=cli
    poetry run typer teamai_cli.main utils docs --output {cli_docs_path} --name teamai-cli
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
