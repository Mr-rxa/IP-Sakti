from app.models.user import UserModel
from app.schemas.auth import UserLoginRequest, UserRegisterRequest
from app.services import auth_service as auth_module


def test_login_requires_matching_role(db_session, monkeypatch):
    monkeypatch.setattr(auth_module, "_supabase_client", None)
    auth_module.auth_service.register(
        db_session,
        UserRegisterRequest(
            email="role-check@example.com",
            password="password123",
            role="Legal Researcher",
            full_name="Role Check",
        ),
    )

    try:
        auth_module.auth_service.login(
            db_session,
            UserLoginRequest(
                email="role-check@example.com",
                password="password123",
                role="AYUSH Practitioner",
            ),
        )
        assert False, "A role mismatch must be rejected"
    except Exception as exc:
        assert getattr(exc, "error_code", None) == "ROLE_MISMATCH"


def test_login_returns_verified_role(db_session, monkeypatch):
    monkeypatch.setattr(auth_module, "_supabase_client", None)
    auth_module.auth_service.register(
        db_session,
        UserRegisterRequest(
            email="verified-role@example.com",
            password="password123",
            role="IP Consultant",
        ),
    )
    response = auth_module.auth_service.login(
        db_session,
        UserLoginRequest(
            email="verified-role@example.com",
            password="password123",
            role="IP Consultant",
        ),
    )
    assert response.user.role == "IP Consultant"
    assert response.access_token