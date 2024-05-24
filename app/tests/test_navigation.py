# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
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

    actual_navigation, actual_category_item = nav_manager.get_general_navigation()

    assert actual_category_item is None

    assert isinstance(actual_navigation["items"], list)
    assert isinstance(actual_navigation["items"][0]["title"], str)
    assert isinstance(actual_navigation["items"][0]["path"], str)
    assert isinstance(actual_navigation["items"][0]["videos"], list)


def test_get_analysis_navigation():
    nav_manager = NavigationManager()

    actual_navigation, actual_category_item = nav_manager.get_analysis_navigation()

    assert isinstance(actual_navigation["items"], list)
    assert isinstance(actual_navigation["items"][0]["title"], str)
    assert isinstance(actual_navigation["items"][0]["path"], str)
    assert isinstance(actual_navigation["items"][0]["videos"], list)

    assert actual_category_item["title"] == "Analysis"
    assert actual_category_item["path"] == "analysis"


def test_get_testing_navigation():
    nav_manager = NavigationManager()

    actual_navigation, actual_category_item = nav_manager.get_testing_navigation()

    assert isinstance(actual_navigation["items"], list)
    assert isinstance(actual_navigation["items"][0]["title"], str)
    assert isinstance(actual_navigation["items"][0]["path"], str)
    assert isinstance(actual_navigation["items"][0]["videos"], list)

    assert actual_category_item["title"] == "Testing"
    assert actual_category_item["path"] == "testing"


def test_get_coding_navigation():
    nav_manager = NavigationManager()

    actual_navigation, actual_category_item = nav_manager.get_coding_navigation()

    assert isinstance(actual_navigation["items"], list)
    assert isinstance(actual_navigation["items"][0]["title"], str)
    assert isinstance(actual_navigation["items"][0]["path"], str)
    assert isinstance(actual_navigation["items"][0]["videos"], list)

    assert actual_category_item["title"] == "Coding and Architecture"
    assert actual_category_item["path"] == "coding"


def test_get_knowledge_navigation():
    nav_manager = NavigationManager()

    actual_navigation, actual_category_item = nav_manager.get_knowledge_navigation()

    assert isinstance(actual_navigation["items"], list)
    assert isinstance(actual_navigation["items"][0]["title"], str)
    assert isinstance(actual_navigation["items"][0]["path"], str)
    assert isinstance(actual_navigation["items"][0]["videos"], list)

    assert actual_category_item["title"] == "Team Knowledge"
    assert actual_category_item["path"] == "knowledge"


def test_get_about_navigation():
    nav_manager = NavigationManager()

    actual_navigation, actual_category_item = nav_manager.get_about_navigation()

    assert isinstance(actual_navigation["items"], list)
    assert isinstance(actual_navigation["items"][0]["title"], str)
    assert isinstance(actual_navigation["items"][0]["path"], str)
    assert isinstance(actual_navigation["items"][0]["videos"], list)

    assert actual_category_item["title"] == "About Haiven"
    assert actual_category_item["path"] == "about"
