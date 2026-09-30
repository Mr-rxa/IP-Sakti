from fastapi import APIRouter, HTTPException
from app.schemas.translate import TranslateRequest, TranslateResponse
from app.services.translate_service import TranslateService, TranslationUnavailable

router = APIRouter(tags=["Multilingual"])

@router.post("/translate", response_model=TranslateResponse, status_code=200)
def translate_text(payload: TranslateRequest):
    """Translate text through the explicitly configured provider, if available."""
    try:
        return TranslateService.translate(payload)
    except TranslationUnavailable as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
