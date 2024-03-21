# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

from unittest.mock import call, patch, MagicMock, PropertyMock
from services.client import Client


class TestClient:
    @patch("services.client.BeautifulSoup")
    @patch("services.client.requests")
    def test_get_pages(self, mock_request, mock_beautifulsoup):
        first_url = "a url"
        second_url = "another url"
        urls = [first_url, second_url]

        first_response_text = "Some text"
        first_response_soup = MagicMock()
        second_response_text = "Some other text"
        second_response_soup = MagicMock()

        first_response = MagicMock()
        type(first_response).status_code = PropertyMock(return_value=200)
        type(first_response).text = PropertyMock(return_value=first_response_text)
        second_response = MagicMock()
        type(second_response).status_code = PropertyMock(return_value=200)
        type(second_response).text = PropertyMock(return_value=second_response_text)

        mock_request.get.side_effect = [first_response, second_response]
        mock_beautifulsoup.side_effect = [first_response_soup, second_response_soup]

        client = Client()
        pages, failures = client.get_pages(urls)

        mock_request.get.assert_has_calls([call(first_url), call(second_url)])
        mock_beautifulsoup.assert_has_calls(
            [
                call(first_response_text, "html.parser"),
                call(second_response_text, "html.parser"),
            ]
        )
        assert len(failures) == 0
        assert len(pages) == 2

        first_page = pages[0]
        second_page = pages[1]
        assert first_page.content == first_response_soup
        assert first_page.url == first_url
        assert first_page.status_code == 200
        assert first_page.failure is None
        assert second_page.content == second_response_soup
        assert second_page.url == second_url
        assert second_page.status_code == 200
        assert second_page.failure is None

    @patch("services.client.BeautifulSoup")
    @patch("services.client.requests")
    def test_get_pages_with_failure(self, mock_request, mock_beautifulsoup):
        first_url = "a url"
        second_url = "another url"
        urls = [first_url, second_url]

        response_status_code = 404
        response_text = "Not found"
        response = MagicMock()
        type(response).status_code = PropertyMock(return_value=response_status_code)
        type(response).text = PropertyMock(return_value=response_text)
        mock_request.get.return_value = response

        client = Client()
        pages, failures = client.get_pages(urls)

        mock_request.get.assert_any_call(first_url)
        mock_request.get.assert_any_call(second_url)
        assert len(pages) == 0
        assert failures[0].url == first_url
        assert failures[0].status_code == response_status_code
        assert failures[0].failure == response_text
        assert failures[1].url == second_url
        assert failures[1].status_code == response_status_code
        assert failures[1].failure == response_text
