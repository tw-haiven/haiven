from typing import Optional
from pydantic import BaseModel


class ExploreRequest(BaseModel):
    userMessage: str
    item: str
    originalInput: str = ""
    chatSessionId: Optional[str] = None
