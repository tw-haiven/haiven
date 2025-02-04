# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import os
from typing import List, Dict


class InspirationsManager:
    def __init__(self):
        self._inspirations = None
        self._load_inspirations()

    def _load_inspirations(self):
        """Load inspirations from the JSON file."""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "resources", "inspirations.json"
        )
        with open(file_path, "r") as f:
            data = json.load(f)
            self._inspirations = data["inspirations"]

    def get_inspirations(self) -> List[Dict]:
        """Return the cached inspirations list."""
        return self._inspirations
