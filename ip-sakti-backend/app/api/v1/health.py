from fastapi import APIRouter
import httpx
from sqlalchemy import text

from app.config import settings
from app.db.database import engine

router = APIRouter(tags=["System & Health"])

@router.get("/health", status_code=200)
def health_check():
    """
    Service liveness and readiness probe.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV,
        "version": settings.CORPUS_VERSION
    }


def _database_check() -> dict:
    if not settings.DATABASE_URL:
        return {"status": "degraded", "configured": False, "detail": "not_configured"}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready", "configured": True}
    except Exception:
        return {"status": "degraded", "configured": True, "detail": "connection_failed"}


def _rag_check() -> dict:
    if not settings.RAG_SERVICE_URL:
        return {"status": "degraded", "configured": False, "detail": "not_configured"}
    try:
        response = httpx.get(f"{settings.RAG_SERVICE_URL.rstrip('/')}/health", timeout=1.0)
        if response.is_success:
            return {"status": "ready", "configured": True, "reachable": True}
    except httpx.HTTPError:
        pass
    return {"status": "degraded", "configured": True, "reachable": False, "detail": "unreachable"}


def _provider_check() -> dict:
    model_configured = settings.LLM_PROVIDER == "mock" or bool(
        settings.OPENAI_API_KEY or settings.GEMINI_API_KEY
    )
    vector_configured = settings.VECTOR_DB_TYPE in {"chroma", "in-memory"} or bool(settings.PINECONE_API_KEY)
    return {
        "status": "ready" if model_configured and vector_configured else "degraded",
        "model": {"provider": settings.LLM_PROVIDER, "configured": model_configured},
        "vector_store": {"type": settings.VECTOR_DB_TYPE, "configured": vector_configured},
    }


@router.get("/ready", status_code=200)
def readiness_check():
    """Return safe dependency readiness details; degraded dependencies do not fail the probe."""
    checks = {
        "database": _database_check(),
        "rag_service": _rag_check(),
        "providers": _provider_check(),
    }
    degraded = any(check["status"] != "ready" for check in checks.values())
    return {
        "status": "degraded" if degraded else "ready",
        "service": settings.PROJECT_NAME,
        "checks": checks,
        "secrets_included": False,
    }

@router.get("/corpus/version", status_code=200)
def corpus_version():
    """
    Returns current corpus version, legal amendments tracked, and last verification stamp.
    """
    return {
        "corpus_version": settings.CORPUS_VERSION,
        "latest_amendments_indexed": [
            "Patents (Amendment) Rules, 2024",
            "Biological Diversity (Amendment) Act, 2023 & BD Rules 2024",
            "WIPO Genetic Resources and Associated TK Treaty (2024)",
            "FSSAI (Ayurveda Aahar) Regulations, 2022"
        ],
        "jurisdictions_supported": ["India", "International"],
        "status": "active"
    }
