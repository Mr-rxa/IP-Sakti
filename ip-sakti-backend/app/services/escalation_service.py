import uuid
from sqlalchemy.orm import Session
from app.models.escalation import EscalationModel
from app.schemas.escalate import EscalateRequest, EscalateResponse

class EscalationService:
    @staticmethod
    def log_escalation(db: Session, req: EscalateRequest, user_id: str = None) -> EscalateResponse:
        esc_id = str(uuid.uuid4())
        record = EscalationModel(
            escalation_id=esc_id,
            session_id=req.session_id,
            query_id=req.query_id,
            user_id=user_id,
            user_contact_optional=req.user_contact_optional,
            reason=req.reason,
            status="queued"
        )
        db.add(record)
        try:
            db.commit()
        except Exception:
            db.rollback()

        return EscalateResponse(
            status="queued",
            escalation_id=esc_id,
            expert_assigned=False,
            message="Your request was recorded. No human expert is currently assigned.",
        )
