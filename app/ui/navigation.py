# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from ui.url import Url


class NavigationManager:
    def __init__(self):
        self.path = Url()
        self.navigation = {
            "items": [
                {
                    "title": "Analysis",
                    "path": self.path.PATH_ANALYSIS,
                    "videos": [],
                },
                {
                    "title": "Coding and Architecture",
                    "path": self.path.PATH_CODING,
                    "videos": [],
                },
                {
                    "title": "Testing",
                    "path": self.path.PATH_TESTING,
                    "videos": [],
                },
                {"title": "Team Knowledge", "path": self.path.PATH_KNOWLEDGE},
                {"title": "About Haiven", "path": self.path.PATH_ABOUT},
            ]
        }

    def get_general_navigation(self):
        return self._get_navigation(self.path.PATH_GENERAL_DEPRECATED)

    def get_analysis_navigation(self):
        return self._get_navigation(self.path.PATH_ANALYSIS)

    def get_testing_navigation(self):
        return self._get_navigation(self.path.PATH_TESTING)

    def get_coding_navigation(self):
        return self._get_navigation(self.path.PATH_CODING)

    def get_knowledge_navigation(self):
        return self._get_navigation(self.path.PATH_KNOWLEDGE)

    def get_about_navigation(self):
        return self._get_navigation(self.path.PATH_ABOUT)

    def get_general_path(self):
        return self.path.general()

    def get_analysis_path(self):
        return self.path.analysis()

    def get_testing_path(self):
        return self.path.testing()

    def get_coding_path(self):
        return self.path.coding()

    def get_knowledge_path(self):
        return self.path.knowledge()

    def get_about_path(self):
        return self.path.about()

    def get_chat_path(self):
        return self.path.chat()

    def _get_navigation(self, path):
        navigation = self.navigation
        navigation["selected"] = path
        category_item = None
        for item in navigation["items"]:
            if item["path"] == path:
                category_item = item

        return navigation, category_item
