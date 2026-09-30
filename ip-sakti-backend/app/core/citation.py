import re
from typing import Dict, Any, Optional


def canonical_source_title(title: str) -> str:
    """Normalize harmless title variation while retaining the legal source identity."""
    normalized = " ".join((title or "").split()).strip()
    if normalized.lower().startswith("the "):
        normalized = normalized[4:]
    return normalized


def canonical_section(section: str) -> str:
    normalized = " ".join((section or "").split()).strip()
    match = re.match(r"^(Section|Article|Rule|Regulation)\s+[A-Za-z0-9()./-]+", normalized, re.IGNORECASE)
    return match.group(0) if match else normalized

def format_citation(chunk_metadata: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Extracts citation details from retrieved corpus chunk metadata.
    """
    return {
        "source_title": canonical_source_title(chunk_metadata.get("source_title", "Unknown Source")),
        "section_or_article": canonical_section(chunk_metadata.get("section_or_article", "N/A")),
        "jurisdiction": chunk_metadata.get("jurisdiction", "India"),
        "source_url": chunk_metadata.get("source_url", "")
    }
