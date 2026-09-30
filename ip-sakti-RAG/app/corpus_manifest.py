"""Build and validate the versioned manifest for the approved corpus."""

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from app.config import CORPUS_PATH

ALLOWED_JURISDICTIONS = {"India", "International"}
REQUIRED_CHUNK_FIELDS = {
    "chunk_id", "source_title", "section_or_article", "jurisdiction",
    "regime", "effective_date", "doc_version", "source_url", "source_file", "text",
}


def _source_id(source_title: str, jurisdiction: str, source_url: str) -> str:
    value = f"{jurisdiction}|{source_title}|{source_url}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:16]


def _source_checksum(chunks: list[dict[str, Any]]) -> str:
    content = "\n".join(
        f"{chunk['chunk_id']}\n{chunk['text']}" for chunk in sorted(chunks, key=lambda item: item["chunk_id"])
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_manifest(chunks: list[dict[str, Any]], generated_on: str | None = None) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for chunk in chunks:
        key = (chunk["source_title"], chunk["jurisdiction"], chunk["source_url"])
        grouped[key].append(chunk)

    sources = []
    for (title, jurisdiction, source_url), source_chunks in sorted(grouped.items()):
        effective_dates = sorted({str(item["effective_date"]) for item in source_chunks if item["effective_date"]})
        versions = sorted({str(item["doc_version"]) for item in source_chunks if item["doc_version"]})
        sources.append(
            {
                "source_id": _source_id(title, jurisdiction, source_url),
                "title": title,
                "jurisdiction": jurisdiction,
                "regimes": sorted({item["regime"] for item in source_chunks}),
                "authority_url": source_url,
                "effective_dates": effective_dates,
                "versions": versions,
                "checksum": _source_checksum(source_chunks),
                "reviewer": None,
                "review_date": None,
                "chunk_count": len(source_chunks),
                "chunk_ids": sorted(item["chunk_id"] for item in source_chunks),
            }
        )

    return {
        "manifest_version": 1,
        "generated_on": generated_on or date.today().isoformat(),
        "corpus_path": "data/corpus/corpus.json",
        "chunk_count": len(chunks),
        "source_count": len(sources),
        "sources": sources,
    }


def validate_corpus(chunks: list[dict[str, Any]], manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    chunk_ids = [chunk.get("chunk_id") for chunk in chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        errors.append("duplicate chunk_id values")
    for index, chunk in enumerate(chunks):
        missing = sorted(REQUIRED_CHUNK_FIELDS - chunk.keys())
        if missing:
            errors.append(f"chunk {index} missing fields: {', '.join(missing)}")
        if chunk.get("jurisdiction") not in ALLOWED_JURISDICTIONS:
            errors.append(f"chunk {index} has unsupported jurisdiction")
        if not str(chunk.get("text", "")).strip():
            errors.append(f"chunk {index} has empty text")

    manifest_ids = [source.get("source_id") for source in manifest.get("sources", [])]
    if len(manifest_ids) != len(set(manifest_ids)):
        errors.append("duplicate source_id values")
    if manifest.get("chunk_count") != len(chunks):
        errors.append("manifest chunk_count does not match corpus")
    if manifest.get("source_count") != len(manifest.get("sources", [])):
        errors.append("manifest source_count does not match sources")

    expected = build_manifest(chunks, generated_on=manifest.get("generated_on"))
    expected_sources = {source["source_id"]: source for source in expected["sources"]}
    actual_sources = {source.get("source_id"): source for source in manifest.get("sources", [])}
    if set(expected_sources) != set(actual_sources):
        errors.append("manifest sources do not match corpus")
    for source_id, expected_source in expected_sources.items():
        actual = actual_sources.get(source_id)
        if actual and (
            actual.get("checksum") != expected_source["checksum"]
            or actual.get("chunk_ids") != expected_source["chunk_ids"]
        ):
            errors.append(f"manifest checksum or chunk IDs do not match source {source_id}")
    return errors


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or validate the IP-SAKTI corpus manifest.")
    parser.add_argument("--corpus", type=Path, default=CORPUS_PATH)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    manifest_path = args.manifest or args.corpus.with_name("corpus_manifest.json")
    chunks = load_json(args.corpus)
    if not isinstance(chunks, list):
        raise ValueError("corpus must be a JSON list")
    if args.validate:
        manifest = load_json(manifest_path)
        errors = validate_corpus(chunks, manifest)
        if errors:
            raise SystemExit("Corpus validation failed:\n- " + "\n- ".join(errors))
        print(f"Validated {len(chunks)} chunks across {len(manifest['sources'])} sources")
        return
    manifest_path.write_text(json.dumps(build_manifest(chunks), indent=2), encoding="utf-8")
    print(f"Wrote manifest for {len(chunks)} chunks to {manifest_path}")


if __name__ == "__main__":
    main()