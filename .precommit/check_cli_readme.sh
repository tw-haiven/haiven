#!/bin/bash

if [["$(git diff --quiet cli/teamai_cli/main.py)" != "0"] && ["$(git diff --quiet cli/README.md)" == "0"] ]; then
    cd cli && \
    poetry run typer teamai_cli.main utils docs --output README.md --name teamai-cli
    if ["$(git diff --quiet cli/README.md)" != "0"]; then
        echo "please commit cli/teamai-cli/README.md"
        exit 1
    fi
fi
