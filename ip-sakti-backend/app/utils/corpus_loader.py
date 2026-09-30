import json
import uuid
from pathlib import Path
from typing import List, Dict, Any

def create_corpus_chunk(
    source_title: str,
    section_or_article: str,
    jurisdiction: str,
    regime: str,
    effective_date: str,
    doc_version: str,
    source_url: str,
    text: str
) -> Dict[str, Any]:
    """
    Creates a metadata-rich chunk adhering strictly to the Doc 04 schema.
    """
    return {
        "chunk_id": str(uuid.uuid4()),
        "source_title": source_title,
        "section_or_article": section_or_article,
        "jurisdiction": jurisdiction,
        "regime": regime,
        "effective_date": effective_date,
        "doc_version": doc_version,
        "source_url": source_url,
        "text": text.strip()
    }

def load_chunks_from_file(filepath: Path) -> List[Dict[str, Any]]:
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
