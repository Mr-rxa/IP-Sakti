import httpx
from typing import Protocol
from app.config import settings
from app.schemas.translate import TranslateRequest, TranslateResponse

class TranslationProvider(Protocol):
    def translate(self, request: TranslateRequest) -> str: ...

class TranslationUnavailable(Exception):
    pass

class HttpTranslationProvider:
    def __init__(self, url: str, api_key: str | None = None):
        self.url = url
        self.api_key = api_key

    def translate(self, request: TranslateRequest) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = httpx.post(
            self.url,
            json={"text": request.text, "source_language": request.source_language, "target_language": request.target_language},
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
        translated_text = response.json().get("translated_text")
        if not isinstance(translated_text, str) or not translated_text.strip():
            raise TranslationUnavailable("Translation provider returned no translated text")
        return translated_text

def get_translation_provider() -> TranslationProvider:
    if settings.TRANSLATION_PROVIDER.lower() == "http" and settings.TRANSLATION_PROVIDER_URL:
        return HttpTranslationProvider(settings.TRANSLATION_PROVIDER_URL, settings.TRANSLATION_PROVIDER_API_KEY)
    raise TranslationUnavailable("Translation provider integration is not configured.")

class TranslateService:
    @staticmethod
    def translate(req: TranslateRequest) -> TranslateResponse:
        provider = get_translation_provider()
        try:
            translated_text = provider.translate(req)
        except (httpx.HTTPError, TranslationUnavailable) as exc:
            raise TranslationUnavailable(str(exc)) from exc
        return TranslateResponse(
            translated_text=translated_text,
            target_language=req.target_language,
            disclaimer=req.disclaimer,
            citations=req.citations,
        )
