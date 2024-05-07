# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from shared.navigation import NavigationManager


def test_get_general_path():
    nav_manager = NavigationManager()
    expected_path = "/teamai"

    actual_path = nav_manager.get_general_path()

    assert actual_path == expected_path


def test_get_analysis_path():
    nav_manager = NavigationManager()
    expected_path = "/analysis"

    actual_path = nav_manager.get_analysis_path()

    assert actual_path == expected_path


def test_get_testing_path():
    nav_manager = NavigationManager()
    expected_path = "/testing"

    actual_path = nav_manager.get_testing_path()

    assert actual_path == expected_path


def test_get_coding_path():
    nav_manager = NavigationManager()
    expected_path = "/coding"

    actual_path = nav_manager.get_coding_path()

    assert actual_path == expected_path


def test_get_knowledge_path():
    nav_manager = NavigationManager()
    expected_path = "/knowledge"

    actual_path = nav_manager.get_knowledge_path()

    assert actual_path == expected_path


def test_get_about_path():
    nav_manager = NavigationManager()
    expected_path = "/about"

    actual_path = nav_manager.get_about_path()

    assert actual_path == expected_path


def test_chat_path():
    nav_manager = NavigationManager()
    expected_path = "/chat"

    actual_path = nav_manager.get_chat_path()

    assert actual_path == expected_path


def test_get_general_navigation():
    nav_manager = NavigationManager()
    expected_navigation = {
        "items": [
            {
                "title": "Analysis",
                "path": "analysis",
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
                "path": "coding",
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
            {"title": "Testing", "path": "testing", "videos": []},
            {"title": "Team Knowledge", "path": "knowledge"},
            {"title": "About Haiven", "path": "about"},
        ],
        "selected": "teamai",
    }

    actual_navigation, actual_category_item = nav_manager.get_general_navigation()

    assert actual_navigation == expected_navigation
    assert actual_category_item is None


def test_get_analysis_navigation():
    nav_manager = NavigationManager()
    expected_navigation = {
        "items": [
            {
                "title": "Analysis",
                "path": "analysis",
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
                "path": "coding",
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
                "path": "testing",
                "videos": [],
            },
            {"title": "Team Knowledge", "path": "knowledge"},
            {"title": "About Haiven", "path": "about"},
        ],
        "selected": "analysis",
    }
    expected_category_item = {
        "title": "Analysis",
        "path": "analysis",
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
    }

    actual_navigation, actual_category_item = nav_manager.get_analysis_navigation()

    assert actual_navigation == expected_navigation
    assert actual_category_item == expected_category_item


def test_get_testing_navigation():
    nav_manager = NavigationManager()
    expected_navigation = {
        "items": [
            {
                "title": "Analysis",
                "path": "analysis",
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
                "path": "coding",
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
                "path": "testing",
                "videos": [],
            },
            {"title": "Team Knowledge", "path": "knowledge"},
            {"title": "About Haiven", "path": "about"},
        ],
        "selected": "testing",
    }
    expected_category_item = {
        "title": "Testing",
        "path": "testing",
        "videos": [],
    }

    actual_navigation, actual_category_item = nav_manager.get_testing_navigation()

    assert actual_navigation == expected_navigation
    assert actual_category_item == expected_category_item


def test_get_coding_navigation():
    nav_manager = NavigationManager()
    expected_navigation = {
        "items": [
            {
                "title": "Analysis",
                "path": "analysis",
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
                "path": "coding",
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
                "path": "testing",
                "videos": [],
            },
            {"title": "Team Knowledge", "path": "knowledge"},
            {"title": "About Haiven", "path": "about"},
        ],
        "selected": "coding",
    }
    expected_category_item = {
        "title": "Coding and Architecture",
        "path": "coding",
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
    }

    actual_navigation, actual_category_item = nav_manager.get_coding_navigation()

    assert actual_navigation == expected_navigation
    assert actual_category_item == expected_category_item


def test_get_knowledge_navigation():
    nav_manager = NavigationManager()
    expected_navigation = {
        "items": [
            {
                "title": "Analysis",
                "path": "analysis",
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
                "path": "coding",
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
                "path": "testing",
                "videos": [],
            },
            {"title": "Team Knowledge", "path": "knowledge"},
            {"title": "About Haiven", "path": "about"},
        ],
        "selected": "knowledge",
    }
    expected_category_item = {"title": "Team Knowledge", "path": "knowledge"}

    actual_navigation, actual_category_item = nav_manager.get_knowledge_navigation()

    assert actual_navigation == expected_navigation
    assert actual_category_item == expected_category_item


def test_get_about_navigation():
    nav_manager = NavigationManager()
    expected_navigation = {
        "items": [
            {
                "title": "Analysis",
                "path": "analysis",
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
                "path": "coding",
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
                "path": "testing",
                "videos": [],
            },
            {"title": "Team Knowledge", "path": "knowledge"},
            {"title": "About Haiven", "path": "about"},
        ],
        "selected": "about",
    }
    expected_category_item = {"title": "About Haiven", "path": "about"}

    actual_navigation, actual_category_item = nav_manager.get_about_navigation()

    assert actual_navigation == expected_navigation
    assert actual_category_item == expected_category_item
