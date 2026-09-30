import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from app.db.database import Base

class EscalationModel(Base):
    __tablename__ = "escalations"

    escalation_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), nullable=False)
    query_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=True, index=True)
    assigned_expert_id = Column(String(36), nullable=True)
    user_contact_optional = Column(String(200), nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(50), default="queued")
    timestamp = Column(DateTime, default=datetime.utcnow)
