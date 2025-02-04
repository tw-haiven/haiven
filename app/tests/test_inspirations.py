# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from prompts.inspirations import InspirationsManager


class TestInspirationsManager(unittest.TestCase):
    def test_load_inspirations(self):
        manager = InspirationsManager()
        inspirations = manager.get_inspirations()

        self.assertIsInstance(inspirations, list)
        self.assertTrue(len(inspirations) > 0)

        first_item = inspirations[0]
        self.assertIn("title", first_item)
        self.assertIn("description", first_item)
        self.assertIn("category", first_item)
        self.assertIn("prompt_template", first_item)

        # Verify the prompt template is a non-empty string
        self.assertIsInstance(first_item["prompt_template"], str)
        self.assertTrue(len(first_item["prompt_template"]) > 0)
