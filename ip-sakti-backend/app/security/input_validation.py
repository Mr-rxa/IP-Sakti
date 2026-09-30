import re
from app.core.exceptions import IPSaktiException

# Simple sanitization to prevent prompt injection and abusive payloads
def sanitize_text_input(text: str, max_length: int = 2000) -> str:
    if not text or not text.strip():
        raise IPSaktiException("Input text cannot be empty", "INVALID_INPUT", 400)
    
    cleaned = text.strip()
    if len(cleaned) > max_length:
        raise IPSaktiException(
            f"Input text exceeds the maximum length of {max_length} characters",
            "INPUT_TOO_LARGE",
            413,
        )
    
    # Strip null bytes and non-printable control characters
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", cleaned)
    return cleaned
