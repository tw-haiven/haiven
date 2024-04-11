# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from teamai_cli.services.client import Client
from teamai_cli.models.html_filter import HtmlFilter
from teamai_cli.services.page_helper import PageHelper


class WebPageService:
    def __init__(self, client: Client, page_helper: PageHelper):
        self.client = client
        self.page_helper = page_helper

    def get_single_page(self, url: str, html_filter: HtmlFilter):
        page_data_list, failures = self.client.get_pages([url])
        if len(failures) > 0:
            raise ValueError(f"Failed to get page content error: {failures[0].failure}")
        return self.page_helper.get_article(page_data_list[0], html_filter)
