from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ActivityItem(BaseModel):
    id: str
    kind: str
    title: str
    summary: str
    detail: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime


class ActivityResponse(BaseModel):
    items: List[ActivityItem]
