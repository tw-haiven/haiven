#!/bin/bash

if [["$(git diff --quiet cli/haiven_cli/main.py)" != "0"] && ["$(git diff --quiet cli/README.md)" == "0"] ]; then
    cd cli && \
    poetry run typer haiven_cli.main utils docs --output README.md --name haiven-cli
    if ["$(git diff --quiet cli/README.md)" != "0"]; then
        echo "please commit cli/README.md"
        exit 1
    fi
fi
