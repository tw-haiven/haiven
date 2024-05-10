from typing import Optional
from pydantic import BaseModel

class ExploreRequest(BaseModel):
    input: str
    context: str
    chatSessionId: Optional[str] = None