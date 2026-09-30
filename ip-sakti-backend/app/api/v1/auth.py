from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_database_session, get_current_user
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, AuthResponse, UserProfileResponse
from app.services.auth_service import auth_service
from app.models.user import UserModel
from app.models.query_log import QueryLogModel
from app.models.escalation import EscalationModel
from app.schemas.activity import ActivityItem, ActivityResponse

router = APIRouter(prefix="/auth", tags=["Authentication & User Management"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_database_session)
):
    """
    Register a new user in Supabase (with fallback to local store) and issue JWT token.
    """
    return auth_service.register(db, payload)

@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_database_session)
):
    """
    Authenticate user via Supabase credentials or local DB, and return JWT session token.
    """
    return auth_service.login(db, payload)

@router.get("/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def get_current_user_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get the authenticated user's profile information.
    """
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        full_name=current_user.full_name,
        created_at=current_user.created_at
    )

@router.get("/activity", response_model=ActivityResponse, status_code=status.HTTP_200_OK)
def get_activity(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_database_session),
):
    """Return the authenticated user's persisted questions and escalations."""
    query_items = (
        db.query(QueryLogModel)
        .filter(QueryLogModel.user_id == current_user.id)
        .order_by(QueryLogModel.created_at.desc())
        .limit(50)
        .all()
    )
    escalation_items = (
        db.query(EscalationModel)
        .filter(EscalationModel.user_id == current_user.id)
        .order_by(EscalationModel.created_at.desc())
        .limit(50)
        .all()
    )
    items = [
        ActivityItem(
            id=item.query_id,
            kind="query",
            title="IPR question",
            summary=item.answer_text,
            detail=item.query_text,
            status="abstained" if item.abstained else "answered",
            created_at=item.timestamp,
        )
        for item in query_items
    ]
    items.extend(
        ActivityItem(
            id=item.escalation_id,
            kind="escalation",
            title="Human review request",
            summary="Request recorded; no human expert is currently assigned.",
            detail=item.reason,
            status=item.status,
            created_at=item.timestamp,
        )
        for item in escalation_items
    )
    items.sort(key=lambda item: item.created_at, reverse=True)
    return ActivityResponse(items=items)
