# sets up the environment (run once)
init:
    cd app && \
    poetry install --no-root

# runs the application
run:
    cd app && \
    poetry run python main.py

# runs tests
test:
    cd app && \
    poetry run pytest -m 'not integration'

# builds local docker image
build-docker-image:
    cd app && \
    docker build -t team-ai-base:local .
    cd demo-knowledge-pack && \
    docker build --build-arg REGISTRY_URL= --build-arg TAG=local -t team-ai-demo:local .

# runs local docker image
run-docker-image:
    docker inspect --type=image team-ai-demo:local && \
    cd app && \
    docker run --env-file .env -e TEAM_CONTENT_PATH=teams -p 8080:8080 team-ai-demo:local

run-docker-prod-image:
    cd app && \
    docker run --env-file .env -e TEAM_CONTENT_PATH=teams -p 8080:8080 us-central1-docker.pkg.dev/team-ai-7a96/team-ai/team-ai-demo:main

# retrieve secrets (requires gcloud to be logged in team-ai-7a96)
get-secret +secret='':
    gcloud secrets versions access latest --secret={{secret}}

cli-init:
    cd cli && \
    poetry install

cli-install:
    cd cli && \
    poetry install && \
    poetry build && \
    pip install dist/teamai_cli-0.1.0-py3-none-any.whl --force-reinstall


cli-run +command='':
    cd cli/teamai_cli && \
    poetry run python main.py {{command}}

cli-test:
    cd cli && \
    poetry run pytest -vv

cli-update-docs:
    cd cli && \
    poetry run typer teamai_cli.main utils docs --output README.md --name teamai-cli

extract:
    cd app && \
    source ./venv/bin/activate && \
    python knowledge_scripts/mfcom/extract.py

index:
    cd app && \
    source ./venv/bin/activate && \
    python knowledge_scripts/mfcom/index.py