import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.db.database import Base

class SessionModel(Base):
    __tablename__ = "sessions"

    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    jurisdiction_selected = Column(String(30), default="India", nullable=False)
    classification_result = Column(String(100), nullable=True)
    current_question_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
