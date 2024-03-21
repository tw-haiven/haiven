# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import Dict


class KnowledgePack:
    def __init__(self, path: str, domain: Dict[str, str]):
        self.path = path
        self.domain = domain

    @classmethod
    def from_dict(cls, data):
        return cls(
            path=data.get("path", "teams"),
            domain=data.get("domain"),
        )


class Domain:
    def __init__(self, name: Dict[str, str]):
        self.name = name

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
        )
