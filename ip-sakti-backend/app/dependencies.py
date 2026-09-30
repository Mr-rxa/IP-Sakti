from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models.user import UserModel
from app.services.auth_service import auth_service
from app.core.exceptions import IPSaktiException

security = HTTPBearer(auto_error=False)

def get_database_session(db: Session = Depends(get_db)) -> Session:
    return db

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_database_session)
) -> UserModel:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required"
        )
    try:
        return auth_service.get_user_from_token(db, credentials.credentials)
    except IPSaktiException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_database_session)
) -> Optional[UserModel]:
    if not credentials or not credentials.credentials:
        return None
    try:
        return auth_service.get_user_from_token(db, credentials.credentials)
    except Exception:
        return None
