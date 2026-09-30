from datetime import datetime, timedelta, timezone
import logging

import pytest
from pydantic import ValidationError

from app.schemas.query import QueryRequest
from app.schemas.translate import TranslateRequest
from app.security.rate_limit import InMemoryRateLimiter
from app.services.paid_source_service import PaidSourceService
from app.utils.logging import SensitiveValueRedactionFilter

def test_query_and_translation_payloads_have_explicit_limits():
    with pytest.raises(ValidationError):
        QueryRequest(query_text="x" * 2001)
    with pytest.raises(ValidationError):
        TranslateRequest(text="x" * 20001)

def test_rate_limiter_denies_after_configured_window_limit():
    limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
    assert limiter.is_allowed("198.51.100.10")
    assert not limiter.is_allowed("198.51.100.10")
    assert limiter.is_allowed("198.51.100.11")

def test_sensitive_values_are_redacted_without_breaking_format_arguments(caplog):
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "api_key=%s status=%d", ("secret-value", 200), None)
    SensitiveValueRedactionFilter().filter(record)
    assert record.args == (200,)
    assert record.getMessage() == "api_key=[REDACTED] status=200"

def test_paid_source_consent_is_denied_by_default(db_session):
    service = PaidSourceService()
    assert not service.has_active_consent(db_session, "missing-user", "provider-x")
    with pytest.raises(PermissionError):
        service.require_consent(db_session, "missing-user", "provider-x")

def test_paid_source_consent_expiry_is_enforced(db_session):
    service = PaidSourceService()
    from app.schemas.paid_source import PaidSourceConsentRequest
    consent = service.grant_consent(
        db_session,
        "user-1",
        PaidSourceConsentRequest(
            provider="provider-x",
            purpose="research",
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1),
        ),
    )
    assert consent.consent_id
    assert not service.has_active_consent(db_session, "user-1", "provider-x")