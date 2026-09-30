import argparse
import json
import os
import pickle
import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi

from app.config import (
    BM25_PATH,
    CHROMA_DIR,
    CORPUS_PATH,
    ENABLE_DENSE,
    ENABLE_PINECONE,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_ENVIRONMENT,
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
)


def tokenize(text: str | None) -> list[str]:
    """Tokenize legal text while preserving section references like 3(p)."""
    text = text or ""
    text = text.lower()
    return re.findall(r"[a-z0-9]+(?:\([a-z0-9]+\))?", text)


def load_corpus(corpus_path: Path = CORPUS_PATH) -> list[dict]:
    if not corpus_path.exists() or corpus_path.stat().st_size == 0:
        raise FileNotFoundError(
            f"Corpus is missing or empty at {corpus_path}. "
            "Run: python -m app.corpus_builder"
        )
    chunks = json.loads(corpus_path.read_text(encoding="utf-8"))
    if not chunks:
        raise ValueError(
            f"Corpus at {corpus_path} has no chunks. Run: python -m app.corpus_builder"
        )
    required_fields = {"chunk_id", "text", "source_title", "jurisdiction", "regime"}
    invalid = [
        index for index, chunk in enumerate(chunks)
        if not isinstance(chunk, dict) or not required_fields.issubset(chunk)
    ]
    if invalid:
        raise ValueError(
            f"Corpus contains invalid chunks at indexes {invalid[:5]}. "
            f"Required fields: {sorted(required_fields)}"
        )
    return chunks


def metadata_for_chunk(chunk: dict) -> dict:
    fields = [
        "source_title",
        "section_or_article",
        "jurisdiction",
        "regime",
        "effective_date",
        "doc_version",
        "source_url",
        "source_file",
    ]
    meta = {field: str(chunk.get(field, "")) for field in fields}
    meta["text"] = str(chunk.get("text", ""))[:1000]  # truncate for Pinecone metadata limit
    return meta


def build_sparse_index(chunks: list[dict], bm25_path: Path = BM25_PATH) -> BM25Okapi:
    tokenized_corpus = [
        tokenize(
            " ".join(
                [
                    c.get("source_title", ""),
                    c.get("section_or_article", ""),
                    c.get("regime", ""),
                    c.get("text", ""),
                ]
            )
        )
        for c in chunks
    ]
    bm25 = BM25Okapi(tokenized_corpus)

    bm25_path.parent.mkdir(parents=True, exist_ok=True)
    with bm25_path.open("wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)

    return bm25


def build_dense_index(
    chunks: list[dict],
    vector_dir: Path = CHROMA_DIR,
    force: bool | None = None,
):
    should_build = ENABLE_DENSE if force is None else force
    if not should_build or not GEMINI_API_KEY:
        return None

    vector_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(vector_dir))
    gemini_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=GEMINI_API_KEY,
        model_name=GEMINI_EMBEDDING_MODEL,
    )

    collection = client.get_or_create_collection(
        name="ip_sakti_corpus",
        embedding_function=gemini_ef,
    )
    collection.upsert(
        ids=[c["chunk_id"] for c in chunks],
        documents=[c.get("text", "") for c in chunks],
        metadatas=[metadata_for_chunk(c) for c in chunks],
    )
    return collection


def build_pinecone_index(
    chunks: list[dict],
    index_name: str = PINECONE_INDEX_NAME,
):
    if not PINECONE_API_KEY or not GEMINI_API_KEY:
        return "skipped: missing PINECONE_API_KEY or GEMINI_API_KEY"

    try:
        from pinecone import Pinecone, ServerlessSpec
        pc = Pinecone(api_key=PINECONE_API_KEY)

        # Ensure index exists
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        if index_name not in existing_indexes:
            print(f"Creating Pinecone index '{index_name}'...")
            pc.create_index(
                name=index_name,
                dimension=768,  # gemini-embedding-001 dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT),
            )

        index = pc.Index(index_name)
        gemini_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=GEMINI_API_KEY,
            model_name=GEMINI_EMBEDDING_MODEL,
        )

        batch_size = 50
        total = len(chunks)
        print(f"Upserting {total} chunks to Pinecone index '{index_name}' in batches of {batch_size}...")

        for i in range(0, total, batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.get("text", "") for c in batch]
            embeddings = gemini_ef(texts)
            
            vectors = []
            for j, c in enumerate(batch):
                vectors.append({
                    "id": c["chunk_id"],
                    "values": embeddings[j],
                    "metadata": metadata_for_chunk(c),
                })
            index.upsert(vectors=vectors)

        return f"built ({total} vectors upserted)"
    except Exception as exc:
        return f"failed: {exc.__class__.__name__}: {exc}"


def build_indexes(
    corpus_path: Path = CORPUS_PATH,
    vector_dir: Path = CHROMA_DIR,
    bm25_path: Path = BM25_PATH,
    dense: bool | None = None,
    pinecone: bool | None = None,
) -> dict:
    chunks = load_corpus(corpus_path)
    bm25 = build_sparse_index(chunks, bm25_path=bm25_path)

    dense_status = "skipped"
    try:
        collection = build_dense_index(chunks, vector_dir=vector_dir, force=dense)
        if collection is not None:
            dense_status = "built"
    except Exception as exc:
        dense_status = f"failed: {exc.__class__.__name__}: {exc}"

    pinecone_status = "skipped"
    if pinecone or (pinecone is None and ENABLE_PINECONE):
        pinecone_status = build_pinecone_index(chunks)

    print(
        f"Built sparse BM25 index for {len(chunks)} chunks at {bm25_path}.\n"
        f"Chroma dense index: {dense_status}.\n"
        f"Pinecone vector index: {pinecone_status}."
    )
    return {
        "chunks": chunks,
        "bm25": bm25,
        "dense_status": dense_status,
        "pinecone_status": pinecone_status,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build IP-SAKTI retrieval indexes.")
    parser.add_argument("--corpus", type=Path, default=CORPUS_PATH)
    parser.add_argument("--bm25-path", type=Path, default=BM25_PATH)
    parser.add_argument("--vector-dir", type=Path, default=CHROMA_DIR)
    parser.add_argument(
        "--dense",
        choices=["auto", "on", "off"],
        default=os.getenv("IP_SAKTI_DENSE_CLI", "auto"),
        help="Build Chroma/Gemini dense index. Defaults to auto.",
    )
    parser.add_argument(
        "--pinecone",
        action="store_true",
        help="Upsert embeddings to Pinecone vector DB.",
    )
    args = parser.parse_args()
    dense = None if args.dense == "auto" else args.dense == "on"
    build_indexes(
        corpus_path=args.corpus,
        vector_dir=args.vector_dir,
        bm25_path=args.bm25_path,
        dense=dense,
        pinecone=args.pinecone,
    )


if __name__ == "__main__":
    main()
