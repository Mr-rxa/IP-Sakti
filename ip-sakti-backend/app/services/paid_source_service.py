from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.paid_source import PaidSourceConsentModel
from app.schemas.paid_source import PaidSourceConsentRequest

class PaidSourceService:
    def grant_consent(self, db: Session, user_id: str, request: PaidSourceConsentRequest):
        consent = PaidSourceConsentModel(user_id=user_id, **request.model_dump())
        db.add(consent)
        db.commit()
        db.refresh(consent)
        return consent

    def has_active_consent(self, db: Session, user_id: str, provider: str) -> bool:
        consent = db.query(PaidSourceConsentModel).filter(
            PaidSourceConsentModel.user_id == user_id,
            PaidSourceConsentModel.provider == provider,
            PaidSourceConsentModel.is_granted.is_(True),
            PaidSourceConsentModel.revoked_at.is_(None),
        ).order_by(PaidSourceConsentModel.granted_at.desc()).first()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return bool(consent and (consent.expires_at is None or consent.expires_at > now))

    def require_consent(self, db: Session, user_id: str, provider: str):
        if not self.has_active_consent(db, user_id, provider):
            raise PermissionError("Active consent is required before accessing a paid source")

paid_source_service = PaidSourceService()