import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, JSON
from app.db.database import Base

class QueryLogModel(Base):
    __tablename__ = "query_logs"

    query_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    retrieved_chunk_ids = Column(JSON, default=list)
    confidence_score = Column(Float, nullable=False)
    abstained = Column(Boolean, default=False)
    answer_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
