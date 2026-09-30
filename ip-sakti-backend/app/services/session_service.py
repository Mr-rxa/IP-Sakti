import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.session import SessionModel
from app.schemas.session import SessionResponse, JurisdictionUpdateResponse
from app.core.jurisdiction import JurisdictionEnum
from app.core.exceptions import SessionNotFoundError

class SessionService:
    @staticmethod
    def create_session(db: Session, user_id: Optional[str] = None) -> SessionResponse:
        session_id = str(uuid.uuid4())
        session = SessionModel(
            session_id=session_id,
            user_id=user_id,
            jurisdiction_selected=JurisdictionEnum.INDIA.value
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return SessionResponse(
            session_id=session.session_id,
            created_at=session.created_at,
            jurisdiction_selected=JurisdictionEnum(session.jurisdiction_selected)
        )

    @staticmethod
    def get_session(db: Session, session_id: str) -> SessionModel:
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)
        return session

    @staticmethod
    def update_jurisdiction(db: Session, session_id: str, jurisdiction: JurisdictionEnum) -> JurisdictionUpdateResponse:
        session = SessionService.get_session(db, session_id)
        session.jurisdiction_selected = jurisdiction.value
        db.commit()
        db.refresh(session)
        return JurisdictionUpdateResponse(
            session_id=session.session_id,
            jurisdiction=JurisdictionEnum(session.jurisdiction_selected)
        )

    @staticmethod
    def update_classification_result(db: Session, session_id: str, result: str) -> None:
        session = SessionService.get_session(db, session_id)
        session.classification_result = result
        db.commit()
