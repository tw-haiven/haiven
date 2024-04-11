# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

from bs4 import BeautifulSoup


class PageData:
    def __init__(
        self,
        url: str,
        content: BeautifulSoup,
        status_code: int = 200,
        failure: str = None,
    ):
        self.url = url
        self.content = content
        self.status_code = status_code
        self.failure = failure
