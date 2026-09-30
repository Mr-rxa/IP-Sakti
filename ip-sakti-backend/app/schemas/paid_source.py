from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class PaidSourceConsentRequest(BaseModel):
    provider: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=1, max_length=500)
    scope: Dict[str, Any] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None

class PaidSourceConsentResponse(BaseModel):
    consent_id: str
    provider: str
    purpose: str
    scope: Dict[str, Any]
    granted_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool