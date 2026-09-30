import json
import re
from functools import lru_cache
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import ENABLE_LLM, GEMINI_API_KEY, GEMINI_MODEL

try:
    from google import genai
    from google.genai import types
except Exception:  # pragma: no cover - import depends on local environment
    genai = None
    types = None


def gemini_available() -> bool:
    return bool(ENABLE_LLM and GEMINI_API_KEY and genai and types)


@lru_cache(maxsize=1)
def get_client():
    if not gemini_available():
        return None
    return genai.Client(api_key=GEMINI_API_KEY)


FALLBACK_MODELS = ["gemini-3.1-flash-lite-preview", "gemini-flash-latest", "gemini-3.5-flash"]


def _generate_content(
    *,
    contents: str,
    system_instruction: str | None = None,
    temperature: float = 0.0,
    response_mime_type: str | None = None,
    model: str = GEMINI_MODEL,
):
    client = get_client()
    if client is None or types is None:
        raise RuntimeError("Gemini is not configured")

    config_kwargs: dict[str, Any] = {"temperature": temperature}
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
    if response_mime_type:
        config_kwargs["response_mime_type"] = response_mime_type

    candidate_models = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_err = None
    for cand in candidate_models:
        try:
            return client.models.generate_content(
                model=cand,
                contents=contents,
                config=types.GenerateContentConfig(**config_kwargs),
            )
        except Exception as exc:
            last_err = exc
            continue
    raise last_err or RuntimeError("All candidate models failed")


def generate_text(
    contents: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.0,
    model: str = GEMINI_MODEL,
) -> str:
    response = _generate_content(
        contents=contents,
        system_instruction=system_instruction,
        temperature=temperature,
        model=model,
    )
    return response.text or ""


def generate_json(
    contents: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.0,
    model: str = GEMINI_MODEL,
) -> dict:
    response = _generate_content(
        contents=contents,
        system_instruction=system_instruction,
        temperature=temperature,
        response_mime_type="application/json",
        model=model,
    )
    return parse_json_text(response.text or "")


def parse_json_text(text: str) -> dict:
    cleaned = text.strip()
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, flags=re.IGNORECASE)
        if match:
            cleaned = match.group(1).strip()

    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Extract outermost JSON object {...}
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(cleaned[first_brace : last_brace + 1])
        except Exception:
            pass

    # Use raw_decode to parse the first valid object
    try:
        idx = cleaned.find("{")
        if idx != -1:
            obj, _ = json.JSONDecoder().raw_decode(cleaned[idx:])
            if isinstance(obj, dict):
                return obj
    except Exception:
        pass

    return {"can_answer": False, "answer": text}
