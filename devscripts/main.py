# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
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
    command = """
    cd cli && \
    poetry run typer teamai_cli.main utils docs --output README.md --name teamai-cli
    """
    subprocess.run(command, shell=True)