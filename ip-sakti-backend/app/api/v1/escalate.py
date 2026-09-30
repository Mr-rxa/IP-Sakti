from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_database_session, get_optional_current_user
from app.schemas.escalate import EscalateRequest, EscalateResponse
from app.services.escalation_service import EscalationService
from app.models.user import UserModel

router = APIRouter(tags=["Escalation"])

@router.post("/escalate", response_model=EscalateResponse, status_code=200)
def escalate_to_facilitator(
    payload: EscalateRequest,
    db: Session = Depends(get_database_session),
    current_user: UserModel = Depends(get_optional_current_user),
):
    """
    Log an escalation request to a human IP facilitator for low-confidence or specialized queries.
    """
    return EscalationService.log_escalation(
        db,
        payload,
        current_user.id if current_user else None,
    )
