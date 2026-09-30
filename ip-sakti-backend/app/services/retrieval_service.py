import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.jurisdiction import JurisdictionEnum

class RetrievalService:
    def __init__(self):
        self._chunks: List[Dict[str, Any]] = []
        self._load_corpus()

    def _load_corpus(self):
        seed_path = Path(__file__).resolve().parent.parent.parent / "corpus" / "seed_data" / "sample_corpus_chunks.json"
        if seed_path.exists():
            with open(seed_path, "r", encoding="utf-8") as f:
                self._chunks = json.load(f)
        else:
            self._chunks = []

    def retrieve(
        self,
        query: str,
        jurisdiction: JurisdictionEnum = JurisdictionEnum.INDIA,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieves relevant legal chunks strictly filtered by jurisdiction.
        Calculates similarity scores based on keyword and contextual relevance.
        """
        query_tokens = set(query.lower().split())
        scored_chunks = []

        # Strict jurisdiction filtering - NEVER mix jurisdictions
        jurisdiction_str = jurisdiction.value.lower()

        for chunk in self._chunks:
            if chunk.get("jurisdiction", "").lower() != jurisdiction_str:
                continue

            # Calculate match score based on token overlap in text + source_title + section
            chunk_text = (chunk.get("text", "") + " " + chunk.get("source_title", "") + " " + chunk.get("section_or_article", "")).lower()
            
            # Simple keyword relevance calculation for MVP retrieval
            overlap_count = sum(1 for token in query_tokens if len(token) > 2 and token in chunk_text)
            
            # Baseline similarity
            if overlap_count > 0:
                similarity = min(0.95, 0.45 + (overlap_count * 0.12))
            else:
                similarity = 0.20

            scored_chunks.append({
                "chunk": chunk,
                "score": similarity
            })

        # Sort by relevance score descending
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

retrieval_service = RetrievalService()
