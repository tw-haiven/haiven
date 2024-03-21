# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

from services.page_helper import PageHelper
from models.page_data import PageData
from unittest.mock import MagicMock


class TestPageHelper:
    def test_get_title(self):
        title = "title"

        title_header = MagicMock()
        title_header.get_text.return_value = title

        page_content = MagicMock()
        page_content.find.return_value = title_header

        page_data = PageData(url="url", content=page_content)
        page_helper = PageHelper()

        returned_title = page_helper.find_title(page_data)

        page_content.find.assert_called_with("h1")
        title_header.get_text.assert_called_with(strip=True)
        assert returned_title == title

    def test_get_title_returns_none_if_title_not_found(self):
        page_content = MagicMock()
        page_content.find.return_value = None

        page_data = PageData(url="url", content=page_content)
        page_helper = PageHelper()

        returned_title = page_helper.find_title(page_data)

        page_content.find.assert_called_with("h1")
        assert returned_title == ""

    def test_find_text(self):
        page_content = MagicMock()
        html_filter = "p"
        section1 = MagicMock()
        section2 = MagicMock()
        section1.get_text.return_value = "text1"
        section2.get_text.return_value = "text2"
        page_content.find_all.return_value = [section1, section2]

        page_data = PageData(url="url", content=page_content)
        page_helper = PageHelper()

        returned_text = page_helper.find_text(page_data, html_filter)

        page_content.find_all.assert_called_with(html_filter)
        assert returned_text == "text1 text2"
