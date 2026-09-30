import json
import time
from pathlib import Path
from pinecone import Pinecone

from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME

INDEX_NAME = PINECONE_INDEX_NAME

def ingest_to_pinecone():
    if not PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY is not configured")

    corpus_file = Path(__file__).resolve().parent.parent / "data" / "corpus" / "corpus.json"
    if not corpus_file.exists():
        raise FileNotFoundError(f"Corpus not found at {corpus_file}")

    with open(corpus_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loading {len(chunks)} chunks from {corpus_file}...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)

    records = []
    for c in chunks:
        # Construct record for Pinecone integrated embedding index
        rec = {
            "_id": c["chunk_id"],
            "text": c.get("text", "")[:2000],
            "source_title": str(c.get("source_title", "")),
            "section_or_article": str(c.get("section_or_article", "")),
            "jurisdiction": str(c.get("jurisdiction", "")),
            "regime": str(c.get("regime", "")),
            "effective_date": str(c.get("effective_date", "")),
            "doc_version": str(c.get("doc_version", "")),
            "source_url": str(c.get("source_url", "")),
            "source_file": str(c.get("source_file", "")),
        }
        records.append(rec)

    # Upsert in batches of 40 (Pinecone record limit is typically 96/batch)
    batch_size = 40
    total_upserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        print(f"Upserting batch {i // batch_size + 1} ({len(batch)} records)...")
        res = index.upsert_records(namespace="default", records=batch)
        total_upserted += getattr(res, "record_count", len(batch))
        time.sleep(0.5)

    print(f"Successfully upserted {total_upserted} chunks into Pinecone index '{INDEX_NAME}' namespace 'default'!")
    stats = index.describe_index_stats()
    print("Updated Pinecone Stats:", stats)

if __name__ == "__main__":
    ingest_to_pinecone()
