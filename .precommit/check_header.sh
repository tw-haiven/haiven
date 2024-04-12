#!/bin/bash

for file in "$@"; do
    if [[ ! -s "$file" ]]; then
        continue
    fi

    if ! head -n 1 "$file" | grep -q "^# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions."; then
        echo "Missing license header in file: $file"
        echo "# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions." > "$file.tmp"
        cat "$file" >> "$file.tmp"
        mv "$file.tmp" "$file"
        exit 1
    fi
done
