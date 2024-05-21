# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import Optional
from pydantic import BaseModel


class ExploreRequest(BaseModel):
    userMessage: str
    item: str
    originalInput: str = ""
    chatSessionId: Optional[str] = None
