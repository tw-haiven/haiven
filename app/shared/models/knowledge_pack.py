# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List


class Domain:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            path=data.get("path"),
        )


class KnowledgePack:
    def __init__(self, path: str, domains: List[Domain]):
        self.path = path
        self.domains = domains

    @classmethod
    def from_dict(cls, data):
        return cls(
            path=data.get("path"),
            domains=[Domain.from_dict(domain) for domain in data.get("domains")],
        )
