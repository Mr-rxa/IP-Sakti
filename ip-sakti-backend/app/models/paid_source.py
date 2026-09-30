import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, JSON, String
from app.db.database import Base

class PaidSourceConsentModel(Base):
    __tablename__ = "paid_source_consents"

    consent_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    purpose = Column(String(500), nullable=False)
    scope = Column(JSON, nullable=False, default=dict)
    granted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    is_granted = Column(Boolean, nullable=False, default=True)