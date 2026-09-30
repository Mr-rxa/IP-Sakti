from app.ingestion import tokenize
from app.llm_client import generate_json, gemini_available


RERANK_PROMPT = """You are a relevance judge for a legal retrieval system. Given a user
query and numbered candidate passages, score each passage from 0 to 10 for direct
usefulness in answering the query. Output only JSON mapping passage number strings to
integer scores, for example {"1": 8, "2": 2}."""


def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    if not candidates:
        return []
    if gemini_available():
        try:
            return llm_rerank(query, candidates, top_k=top_k)
        except Exception as e:
            print(f"[rerank] LLM rerank error ({e}), using lexical reranker.")
    return lexical_rerank(query, candidates, top_k=top_k)


def llm_rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    numbered = "\n\n".join(
        f"[{idx + 1}] ({candidate['metadata']['source_title']} - "
        f"{candidate['metadata']['section_or_article']})\n{candidate['text'][:900]}"
        for idx, candidate in enumerate(candidates)
    )
    scores = generate_json(
        f"QUERY: {query}\n\nCANDIDATE PASSAGES:\n{numbered}",
        system_instruction=RERANK_PROMPT,
        temperature=0.0,
    )

    scored_candidates = []
    for index_text, score in scores.items():
        try:
            index = int(index_text) - 1
            if 0 <= index < len(candidates):
                scored_candidates.append((candidates[index], float(score)))
        except (TypeError, ValueError):
            continue

    if not scored_candidates:
        return lexical_rerank(query, candidates, top_k=top_k)

    scored_candidates.sort(key=lambda item: item[1], reverse=True)
    return [
        {**candidate, "relevance_score": max(0.0, min(10.0, float(score)))}
        for candidate, score in scored_candidates[:top_k]
    ]


def lexical_rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        query_tokens = {query.lower()}

    scored = []
    for candidate in candidates:
        metadata = candidate.get("metadata", {})
        indexed_text = " ".join(
            [
                metadata.get("source_title", ""),
                metadata.get("section_or_article", ""),
                metadata.get("regime", ""),
                candidate.get("text", ""),
            ]
        )
        chunk_tokens = set(tokenize(indexed_text))
        shared = query_tokens & chunk_tokens
        coverage = len(shared) / max(len(query_tokens), 1)
        exact_section_boost = 0.0
        for token in query_tokens:
            if "(" in token and token in metadata.get("section_or_article", "").lower():
                exact_section_boost += 0.25
        bm25_boost = min(float(candidate.get("bm25_score", 0.0)) / 8.0, 0.25)
        score = min(10.0, (coverage + exact_section_boost + bm25_boost) * 10.0)
        scored.append((candidate, score))

    scored.sort(
        key=lambda item: (
            item[1],
            item[0].get("rrf_score", 0.0),
            item[0].get("bm25_score", 0.0),
        ),
        reverse=True,
    )
    return [
        {**candidate, "relevance_score": round(float(score), 3)}
        for candidate, score in scored[:top_k]
    ]

