from pydantic import BaseModel
from typing import Optional

class EscalateRequest(BaseModel):
    session_id: str
    query_id: Optional[str] = None
    user_contact_optional: Optional[str] = None
    reason: Optional[str] = None

class EscalateResponse(BaseModel):
    status: str = "queued"
    escalation_id: str
    expert_assigned: bool = False
    message: str = "Your request was recorded. No human expert is currently assigned."
