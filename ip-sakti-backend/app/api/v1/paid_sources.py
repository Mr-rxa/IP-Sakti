from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_database_session
from app.models.user import UserModel
from app.schemas.paid_source import PaidSourceConsentRequest, PaidSourceConsentResponse
from app.services.paid_source_service import paid_source_service

router = APIRouter(prefix="/paid-sources", tags=["Paid Source Consent"])

@router.post("/consents", response_model=PaidSourceConsentResponse, status_code=status.HTTP_201_CREATED)
def grant_paid_source_consent(
    payload: PaidSourceConsentRequest,
    db: Session = Depends(get_database_session),
    current_user: UserModel = Depends(get_current_user),
):
    consent = paid_source_service.grant_consent(db, str(current_user.id), payload)
    
    # Ensure timezone-aware comparison
    is_active = True
    if consent.expires_at is not None:
        exp = consent.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        is_active = exp > datetime.now(timezone.utc)

    return {
        "consent_id": consent.consent_id,
        "provider": consent.provider,
        "purpose": consent.purpose,
        "scope": consent.scope,
        "granted_at": consent.granted_at,
        "expires_at": consent.expires_at,
        "is_active": is_active,
    }