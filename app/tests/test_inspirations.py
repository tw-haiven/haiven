# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import unittest
from prompts.inspirations import InspirationsManager


class TestInspirationsManager(unittest.TestCase):
    def setUp(self):
        self.manager = InspirationsManager()

    def test_get_inspirations_returns_all_inspirations(self):
        inspirations = self.manager.get_inspirations()
        self.assertIsInstance(inspirations, list)
        self.assertTrue(len(inspirations) > 0)

        first_item = inspirations[0]
        self.assertEqual(first_item["id"], "retrospective-facilitator")
        self.assertEqual(
            first_item["title"],
            "Get suggestions for retrospective formats and help analyzing team feedback patterns",
        )

    def test_get_inspiration_by_id_returns_correct_inspiration(self):
        inspiration = self.manager.get_inspiration_by_id("retrospective-facilitator")
        self.assertIsNotNone(inspiration)
        self.assertEqual(
            inspiration["title"],
            "Get suggestions for retrospective formats and help analyzing team feedback patterns",
        )
        self.assertEqual(inspiration["category"], "delivery")

    def test_get_inspiration_by_id_returns_none_for_invalid_id(self):
        inspiration = self.manager.get_inspiration_by_id("non-existent")
        self.assertIsNone(inspiration)

    def test_load_inspirations_validates_required_fields(self):
        inspirations = self.manager.get_inspirations()
        self.assertIsInstance(inspirations, list)
        self.assertTrue(len(inspirations) > 0)

        first_item = inspirations[0]
        required_fields = ["id", "title", "category", "prompt_template"]
        for field in required_fields:
            self.assertIn(field, first_item, f"Field {field} should be present")
            self.assertIsNotNone(first_item[field], f"Field {field} should not be None")
            self.assertNotEqual(
                first_item[field], "", f"Field {field} should not be empty"
            )
