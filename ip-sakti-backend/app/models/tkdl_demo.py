import uuid
from sqlalchemy import Column, String, Boolean, Text
from app.db.database import Base

class TKDLDemoModel(Base):
    __tablename__ = "tkdl_demo_records"

    record_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    formulation_keyword = Column(String(200), nullable=False, index=True)
    classification = Column(String(100), nullable=False)
    matched_note = Column(Text, nullable=False)
    is_illustrative = Column(Boolean, default=True)
