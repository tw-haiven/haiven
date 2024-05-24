# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import Optional
from pydantic import BaseModel


class ExploreRequest(BaseModel):
    userMessage: str
    item: str
    originalInput: str = ""
    chatSessionId: Optional[str] = None
