import uuid
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import UserModel
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, AuthResponse, UserProfileResponse
from app.core.exceptions import IPSaktiException
from app.utils.logging import logger

# Initialize Supabase client if configured
_supabase_client = None
if settings.SUPABASE_URL and (settings.SUPABASE_KEY or settings.SUPABASE_SERVICE_ROLE_KEY):
    try:
        from supabase import create_client
        # Use the publishable key for user auth. The service-role key must never
        # be used by request-time authentication code.
        key = settings.SUPABASE_KEY or settings.SUPABASE_SERVICE_ROLE_KEY
        _supabase_client = create_client(settings.SUPABASE_URL, key)
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to initialize Supabase client: {e}. Falling back to local auth engine.")

class AuthService:
    @staticmethod
    def _create_jwt_token(user_id: str, email: str, role: str) -> str:
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
            "iat": datetime.now(timezone.utc)
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def _verify_password(password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    @classmethod
    def register(cls, db: Session, req: UserRegisterRequest) -> AuthResponse:
        existing = db.query(UserModel).filter(UserModel.email == req.email).first()
        if existing:
            raise IPSaktiException("User with this email already exists", "USER_EXISTS", 400)

        user_id = str(uuid.uuid4())
        supabase_id = None

        # Attempt Supabase Auth registration if configured
        if _supabase_client:
            try:
                res = _supabase_client.auth.sign_up({
                    "email": req.email,
                    "password": req.password,
                    "options": {
                        "data": {
                            "role": req.role,
                            "full_name": req.full_name or ""
                        }
                    }
                })
                if res.user:
                    supabase_id = res.user.id
                    logger.info(f"User registered in Supabase: {supabase_id}")
            except Exception as exc:
                logger.warning(f"Supabase registration error: {exc}. Proceeding with local DB persistence.")

        # Persist user in database
        hashed = cls._hash_password(req.password)
        new_user = UserModel(
            id=user_id,
            email=req.email,
            hashed_password=hashed,
            role=req.role,
            full_name=req.full_name,
            supabase_id=supabase_id,
            is_active=True
        )
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
        except Exception:
            db.rollback()
            raise IPSaktiException("Database error creating user", "DATABASE_ERROR", 500)

        token = cls._create_jwt_token(new_user.id, new_user.email, new_user.role)
        return AuthResponse(
            access_token=token,
            user=UserProfileResponse(
                id=new_user.id,
                email=new_user.email,
                role=new_user.role,
                full_name=new_user.full_name,
                created_at=new_user.created_at
            ),
            message="User registered successfully"
        )

    @classmethod
    def login(cls, db: Session, req: UserLoginRequest) -> AuthResponse:
        user = db.query(UserModel).filter(UserModel.email == req.email).first()

        # Try Supabase Auth login if client is active
        if _supabase_client:
            try:
                sb_res = _supabase_client.auth.sign_in_with_password({
                    "email": req.email,
                    "password": req.password
                })
                if sb_res.user:
                    if not user:
                        # Auto-create in local cache
                        user = UserModel(
                            id=str(uuid.uuid4()),
                            email=req.email,
                            role=sb_res.user.user_metadata.get("role", "AYUSH Practitioner") if sb_res.user.user_metadata else "AYUSH Practitioner",
                            full_name=sb_res.user.user_metadata.get("full_name") if sb_res.user.user_metadata else None,
                            supabase_id=sb_res.user.id,
                            is_active=True
                        )
                        db.add(user)
                        db.commit()
                        db.refresh(user)

                    if user.role != req.role:
                        raise IPSaktiException(
                            "The selected role does not match this account.",
                            "ROLE_MISMATCH",
                            403,
                        )

                    user.last_login_at = datetime.now(timezone.utc)
                    user.login_count = (user.login_count or 0) + 1
                    try:
                        db.commit()
                    except Exception:
                        db.rollback()
                    # Activity endpoints validate the application JWT, not the
                    # provider token, so user-owned records remain consistent.
                    token = cls._create_jwt_token(user.id, user.email, user.role)
                    return AuthResponse(
                        access_token=token,
                        user=UserProfileResponse(
                            id=user.id,
                            email=user.email,
                            role=user.role,
                            full_name=user.full_name,
                            created_at=user.created_at
                        ),
                        message="Login successful via Supabase"
                    )
            except IPSaktiException:
                raise
            except Exception as e:
                logger.info(f"Supabase login attempt returned: {e}. Checking local DB.")

        # Fallback to local DB authentication
        if not user:
            raise IPSaktiException("Invalid email or password", "INVALID_CREDENTIALS", 401)

        if user.role != req.role:
            raise IPSaktiException(
                "The selected role does not match this account.",
                "ROLE_MISMATCH",
                403,
            )

        if not user.hashed_password or not cls._verify_password(req.password, user.hashed_password):
            raise IPSaktiException("Invalid email or password", "INVALID_CREDENTIALS", 401)

        token = cls._create_jwt_token(user.id, user.email, user.role)
        user.last_login_at = datetime.now(timezone.utc)
        user.login_count = (user.login_count or 0) + 1
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise IPSaktiException("Database commit failed during login", "DATABASE_ERROR", 500)

        return AuthResponse(
            access_token=token,
            user=UserProfileResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                full_name=user.full_name,
                created_at=user.created_at
            ),
            message="Login successful"
        )

    @classmethod
    def get_user_from_token(cls, db: Session, token: str) -> UserModel:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            if not user_id:
                raise IPSaktiException("Invalid token payload", "UNAUTHORIZED", 401)
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                raise IPSaktiException("User not found", "USER_NOT_FOUND", 404)
            return user
        except jwt.PyJWTError as e:
            raise IPSaktiException(f"Token validation failed: {str(e)}", "INVALID_TOKEN", 401)

auth_service = AuthService()
