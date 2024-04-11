# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

import requests

from typing import List, Tuple
from teamai_cli.models.page_data import PageData
from bs4 import BeautifulSoup


class Client:
    def get_pages(self, urls: List[str]) -> Tuple[List[PageData], List[PageData]]:
        pages = []
        failures = []
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                content = BeautifulSoup(response.text, "html.parser")
                page_data = PageData(
                    url=url,
                    content=content,
                    status_code=response.status_code,
                    failure=None,
                )
                pages.append(page_data)
            else:
                page_data = PageData(
                    url=url,
                    content=None,
                    status_code=response.status_code,
                    failure=response.text,
                )
                failures.append(page_data)

        return pages, failures
