from pydantic import BaseModel, Field
from typing import List, Optional

class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    target_language: str = Field(default="hi", min_length=2, max_length=16)
    source_language: str = Field(default="en", min_length=2, max_length=16)
    disclaimer: Optional[str] = Field(default=None, max_length=1000)
    citations: List[dict] = Field(default_factory=list, max_length=50)

class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str
    disclaimer: Optional[str] = None
    citations: List[dict] = Field(default_factory=list)
