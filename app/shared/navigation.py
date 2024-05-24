# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from shared.url import Url


class NavigationManager:
    def __init__(self):
        self.path = Url()
        self.navigation = {
            "items": [
                {
                    "title": "Analysis",
                    "path": self.path.PATH_ANALYSIS,
                    "videos": [
                        {
                            "title": "[Chat] Break down an epic",
                            "url": "https://storage.cloud.google.com/genai-demo-large-files/teamai-recording-story-copilot.mp4",
                        },
                        {
                            "title": "[Brainstorming] Write a user story",
                            "url": "https://storage.cloud.google.com/genai-demo-large-files/teamai-recording-story-brainstorming.mp4",
                        },
                    ],
                },
                {
                    "title": "Coding and Architecture",
                    "path": self.path.PATH_CODING,
                    "videos": [
                        {
                            "title": "[Chat] Assist with Threat Modelling",
                            "url": "https://storage.cloud.google.com/genai-demo-large-files/teamai_threat_modelling.mp4",
                        },
                        {
                            "title": "[Brainstorming] Assist with an Architecture Decision Record",
                            "url": "https://storage.cloud.google.com/genai-demo-large-files/teamai_adr_brainstorming.mp4",
                        },
                        {
                            "title": "[Diagrams] Discussing an architecture diagram",
                            "url": "https://storage.cloud.google.com/genai-demo-large-files/teamai-diagram-discussion.mp4",
                        },
                    ],
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
