from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_database_session, get_optional_current_user
from app.schemas.session import (
    SessionResponse,
    JurisdictionUpdateRequest,
    JurisdictionUpdateResponse
)
from app.services.session_service import SessionService
from app.models.user import UserModel

router = APIRouter(tags=["Session"])

@router.post("/session", response_model=SessionResponse, status_code=200)
def create_session(
    db: Session = Depends(get_database_session),
    current_user: UserModel = Depends(get_optional_current_user),
):
    """
    Create a new user session.
    """
    return SessionService.create_session(db, current_user.id if current_user else None)

@router.patch("/session/{session_id}/jurisdiction", response_model=JurisdictionUpdateResponse, status_code=200)
def set_jurisdiction(
    session_id: str,
    payload: JurisdictionUpdateRequest,
    db: Session = Depends(get_database_session)
):
    """
    Set or change the jurisdiction toggle for a session (India or International).
    """
    return SessionService.update_jurisdiction(db, session_id, payload.jurisdiction)
