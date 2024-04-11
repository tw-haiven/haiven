# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import pytest
from teamai_cli.services.web_page_service import WebPageService
from teamai_cli.models.page_data import PageData
from unittest.mock import MagicMock


class TestWebPageService:
    def test_get_single_page_fails_if_client_returns_failure(self):
        url = "some url"
        client = MagicMock()
        page_helper = MagicMock()
        html_filter = MagicMock()
        web_page_service = WebPageService(client, page_helper)
        client.get_pages.return_value = ([], [PageData(url, None, 404, "Not Found")])

        with pytest.raises(ValueError) as e:
            web_page_service.get_single_page(url, html_filter)
        assert str(e.value) == "Failed to get page content error: Not Found"

    def test_get_single_page_returns_article(self):
        url = "some url"
        client = MagicMock()
        page_helper = MagicMock()
        html_filter = MagicMock()
        web_page_service = WebPageService(client, page_helper)
        page_data = PageData(url, "content", 200, None)
        client.get_pages.return_value = ([page_data], [])

        result = web_page_service.get_single_page(url, html_filter)

        page_helper.get_article.assert_called_with(page_data, html_filter)
        assert result == page_helper.get_article.return_value
