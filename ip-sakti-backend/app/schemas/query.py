from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.jurisdiction import JurisdictionEnum

class Citation(BaseModel):
    source_title: str
    section_or_article: str
    jurisdiction: str
    regime: Optional[str] = None
    chunk_id: Optional[str] = None
    source_url: Optional[str] = ""

class QueryRequest(BaseModel):
    session_id: Optional[str] = None
    query_text: str = Field(..., min_length=1, max_length=2000)
    jurisdiction: Optional[JurisdictionEnum] = JurisdictionEnum.INDIA
    classification_context: Optional[str] = Field(default=None, max_length=4000)
    language: Optional[str] = Field(default="en", min_length=2, max_length=16)

class QueryResponse(BaseModel):
    query_id: str
    answer_text: str
    citations: List[Citation] = Field(default_factory=list)
    confidence_score: float
    confidence_label: str
    abstained: bool = False
    escalation_suggested: bool = False
    disclaimer: Optional[str] = None
