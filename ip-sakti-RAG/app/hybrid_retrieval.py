import functools
import pickle
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from app.config import (
    BM25_PATH,
    CHROMA_DIR,
    ENABLE_DENSE,
    ENABLE_PINECONE,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    normalize_jurisdiction,
)
from app.ingestion import tokenize

_pinecone_index = None
_gemini_ef = None


@functools.lru_cache(maxsize=1)
def load_bm25(path_str: str = str(BM25_PATH)):
    path = Path(path_str)
    if not path.exists() or path.stat().st_size == 0:
        return None, []
    try:
        with path.open("rb") as f:
            data = pickle.load(f)
        return data.get("bm25"), data.get("chunks", [])
    except Exception:
        return None, []


from app.llm_client import get_client


def embed_query_text(query: str) -> list[float] | None:
    client = get_client()
    if client is None:
        return None
    try:
        model_name = GEMINI_EMBEDDING_MODEL
        if model_name.startswith("models/"):
            model_name = model_name[len("models/"):]
        res = client.models.embed_content(
            model=model_name,
            contents=query,
        )
        if hasattr(res, "embeddings") and res.embeddings:
            return list(res.embeddings[0].values)
        if hasattr(res, "embedding") and res.embedding:
            return list(res.embedding.values)
    except Exception as e:
        print(f"[embed_query_text] error: {e}")
        return None


def get_dense_collection(persist_dir: Path = CHROMA_DIR):
    if not ENABLE_DENSE or not GEMINI_API_KEY:
        return None
    try:
        client = chromadb.PersistentClient(path=str(persist_dir))
        gemini_ef = get_gemini_ef()
        return client.get_collection(name="ip_sakti_corpus", embedding_function=gemini_ef)
    except Exception:
        return None


def get_pinecone_index():
    global _pinecone_index
    if not ENABLE_PINECONE or not PINECONE_API_KEY:
        return None
    if _pinecone_index is not None:
        return _pinecone_index
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        _pinecone_index = pc.Index(PINECONE_INDEX_NAME)
        return _pinecone_index
    except Exception:
        return None


def chunk_to_result(chunk: dict, *, score: float | None = None) -> dict:
    result = {
        "chunk_id": chunk.get("chunk_id", ""),
        "text": chunk.get("text", ""),
        "metadata": {
            "source_title": chunk.get("source_title", ""),
            "section_or_article": chunk.get("section_or_article", ""),
            "jurisdiction": chunk.get("jurisdiction", ""),
            "regime": chunk.get("regime", ""),
            "effective_date": chunk.get("effective_date", ""),
            "doc_version": chunk.get("doc_version", ""),
            "source_url": chunk.get("source_url", ""),
            "source_file": chunk.get("source_file", ""),
        },
    }
    if score is not None:
        result["bm25_score"] = float(score)
    return result


def matches_filters(
    chunk: dict,
    jurisdiction: str,
    regime_filter: list[str] | None = None,
) -> bool:
    if chunk.get("jurisdiction") != jurisdiction:
        return False
    if regime_filter and chunk.get("regime") not in set(regime_filter):
        return False
    return True


def pinecone_search(
    query: str,
    jurisdiction: str,
    top_k: int = 15,
    regime_filter: list[str] | None = None,
) -> list[dict]:
    index = get_pinecone_index()
    if index is None:
        return []

    try:
        query_vector = embed_query_text(query)
        if not query_vector:
            return []

        filter_dict = {"jurisdiction": {"$eq": jurisdiction}}
        if regime_filter:
            if len(regime_filter) == 1:
                filter_dict["regime"] = {"$eq": regime_filter[0]}
            else:
                filter_dict["regime"] = {"$in": regime_filter}

        res = None
        try:
            res = index.query(
                vector=query_vector,
                top_k=top_k * 2,
                include_metadata=True,
                filter=filter_dict,
            )
        except Exception:
            # Fallback without server-side filter
            res = index.query(
                vector=query_vector,
                top_k=top_k * 2,
                include_metadata=True,
            )

        matches = []
        if res:
            if isinstance(res, dict):
                matches = res.get("matches", [])
            else:
                matches = getattr(res, "matches", []) or []

        items = []
        for match in matches:
            if isinstance(match, dict):
                match_id = match.get("id") or ""
                match_score = match.get("score") or 0.0
                meta = match.get("metadata") or {}
            else:
                match_id = getattr(match, "id", "") or getattr(match, "id_", "") or ""
                match_score = getattr(match, "score", 0.0) or getattr(match, "score_", 0.0) or 0.0
                meta = getattr(match, "metadata", {}) or getattr(match, "fields", {}) or {}

            if not isinstance(meta, dict):
                meta = dict(meta) if meta else {}

            if meta.get("jurisdiction") and meta.get("jurisdiction").lower() != jurisdiction.lower():
                continue
            if regime_filter and meta.get("regime") not in set(regime_filter):
                continue

            text = meta.get("text", "")
            items.append({
                "chunk_id": match_id,
                "text": text,
                "metadata": meta,
                "dense_distance": max(0.0, 1.0 - float(match_score)),
                "pinecone_score": float(match_score),
            })
            if len(items) >= top_k:
                break
        return items
    except Exception as e:
        print(f"[pinecone_search] Error: {e}")
        return []


def dense_search(
    query: str,
    jurisdiction: str,
    top_k: int = 15,
    regime_filter: list[str] | None = None,
) -> list[dict]:
    jurisdiction = normalize_jurisdiction(jurisdiction)

    # 1. Try Pinecone Vector DB first
    if ENABLE_PINECONE:
        pinecone_results = pinecone_search(query, jurisdiction, top_k=top_k, regime_filter=regime_filter)
        if pinecone_results:
            return pinecone_results

    # 2. Fall back to local ChromaDB
    try:
        collection = get_dense_collection()
        if collection is None:
            return []
        results = collection.query(
            query_texts=[query],
            n_results=max(top_k * 3, top_k),
            where={"jurisdiction": jurisdiction},
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        return []

    items: list[dict] = []
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for idx, chunk_id in enumerate(ids):
        metadata = metadatas[idx] or {}
        if regime_filter and metadata.get("regime") not in set(regime_filter):
            continue
        item = {
            "chunk_id": chunk_id,
            "text": documents[idx],
            "metadata": metadata,
            "dense_distance": float(distances[idx]) if idx < len(distances) else None,
        }
        items.append(item)
        if len(items) >= top_k:
            break
    return items


def sparse_search(
    query: str,
    jurisdiction: str,
    top_k: int = 15,
    regime_filter: list[str] | None = None,
) -> list[dict]:
    jurisdiction = normalize_jurisdiction(jurisdiction)
    bm25, chunks = load_bm25()
    if bm25 is None or not chunks:
        return []
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    scored = [
        (chunks[i], float(scores[i]) + exact_reference_boost(tokenized_query, chunks[i]))
        for i in range(len(chunks))
        if matches_filters(chunks[i], jurisdiction, regime_filter)
    ]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [chunk_to_result(chunk, score=score) for chunk, score in scored[:top_k]]


def exact_reference_boost(query_tokens: list[str], chunk: dict) -> float:
    section = str(chunk.get("section_or_article", "")).lower()
    source_title = str(chunk.get("source_title", "")).lower()
    boost = 0.0
    for token in query_tokens:
        if "(" in token and token in section:
            boost += 30.0
        elif token.isdigit() and f"section {token}" in section:
            boost += 10.0
        elif token in {"pct", "tkdl", "trips", "cbd"} and token in source_title:
            boost += 8.0
    return boost


def reciprocal_rank_fusion(
    dense_results: list[dict],
    sparse_results: list[dict],
    k: int = 60,
) -> list[dict]:
    scores: dict[str, float] = {}
    all_chunks: dict[str, dict] = {}

    for rank, item in enumerate(dense_results):
        chunk_id = item["chunk_id"]
        scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank + 1)
        all_chunks[chunk_id] = {**all_chunks.get(chunk_id, {}), **item}

    for rank, item in enumerate(sparse_results):
        chunk_id = item["chunk_id"]
        scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank + 1)
        all_chunks[chunk_id] = {**all_chunks.get(chunk_id, {}), **item}

    fused = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [{**all_chunks[chunk_id], "rrf_score": score} for chunk_id, score in fused]


def hybrid_retrieve(
    query: str,
    jurisdiction: str,
    top_k: int = 20,
    regime_filter: list[str] | None = None,
) -> list[dict]:
    dense = dense_search(query, jurisdiction, top_k=15, regime_filter=regime_filter)
    sparse = sparse_search(query, jurisdiction, top_k=20, regime_filter=regime_filter)
    fused = reciprocal_rank_fusion(dense, sparse)
    return fused[:top_k]
