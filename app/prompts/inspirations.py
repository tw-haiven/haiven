# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from typing import List, Dict, Optional
import yaml


class InspirationsManager:
    def __init__(self):
        self._inspirations_list = None
        self._inspirations_dict = {}
        self._load_inspirations()

    def _load_inspirations(self):
        """Load inspirations from the YAML file."""
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "resources", "inspirations.yaml"
        )
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            self._inspirations_list = data["inspirations"]
            self._inspirations_dict = {
                insp["id"]: insp for insp in self._inspirations_list
            }

    def get_inspirations(self) -> List[Dict]:
        """Return the cached inspirations list."""
        return self._inspirations_list

    def get_inspiration_by_id(self, inspiration_id: str) -> Optional[Dict]:
        """Return a specific inspiration by its ID, or None if not found."""
        return self._inspirations_dict.get(inspiration_id)
