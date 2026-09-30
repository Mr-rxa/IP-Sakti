from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.core.jurisdiction import JurisdictionEnum

class SessionCreateRequest(BaseModel):
    pass

class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    jurisdiction_selected: Optional[JurisdictionEnum] = JurisdictionEnum.INDIA

class JurisdictionUpdateRequest(BaseModel):
    jurisdiction: JurisdictionEnum

class JurisdictionUpdateResponse(BaseModel):
    session_id: str
    jurisdiction: JurisdictionEnum
