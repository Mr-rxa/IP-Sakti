from pydantic import BaseModel, Field
from typing import List

class TKDLMatch(BaseModel):
    formulation_keyword: str
    classification: str
    matched_note: str
    is_illustrative: bool = True

class TKDLLookupResponse(BaseModel):
    matches: List[TKDLMatch] = Field(default_factory=list)
