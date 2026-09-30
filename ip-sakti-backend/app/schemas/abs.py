from pydantic import BaseModel, Field
from typing import List

class ABSChecklistResponse(BaseModel):
    classification: str
    checklist: List[str] = Field(default_factory=list)
