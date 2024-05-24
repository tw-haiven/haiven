#!/bin/bash

for file in "$@"; do
    file_extension=${file##*.}
    
    commit_prefix="#"
    if [[ "$file_extension" == "js" ]]; then
        commit_prefix="//"
    fi

    if [[ ! -s "$file" ]]; then
        continue
    fi

    if ! head -n 1 "$file" | grep -q "© 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions."; then
        echo "Missing license header in file: $file"
        echo "$commit_prefix © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions." > "$file.tmp"
        cat "$file" >> "$file.tmp"
        mv "$file.tmp" "$file"
        exit 1
    fi
done
