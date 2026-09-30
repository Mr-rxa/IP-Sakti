"""Provenance-only corpus graph export; this is not a reasoning engine."""

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import CORPUS_PATH, DATA_DIR

GRAPH_SCHEMA_VERSION = "1.0.0"


def _id(kind: str, value: str) -> str:
    return f"{kind}:{value}"


def build_graph(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str], dict[str, Any]] = {}

    def add_node(node_id: str, kind: str, label: str, provenance: list[str]) -> None:
        existing = nodes.get(node_id)
        if existing:
            existing["provenance"]["source_chunk_ids"] = sorted(
                set(existing["provenance"]["source_chunk_ids"]) | set(provenance)
            )
            return
        nodes[node_id] = {
            "id": node_id,
            "kind": kind,
            "label": label,
            "provenance": {"source_chunk_ids": sorted(set(provenance))},
        }

    def add_edge(source: str, target: str, relation: str, chunk_id: str) -> None:
        key = (source, target, relation)
        if key not in edges:
            edges[key] = {
                "source": source,
                "target": target,
                "relation": relation,
                "provenance": {"source_chunk_ids": []},
            }
        edges[key]["provenance"]["source_chunk_ids"].append(chunk_id)

    for chunk in chunks:
        chunk_id = str(chunk["chunk_id"])
        source_id = _id("source", f"{chunk['source_title']}|{chunk['jurisdiction']}|{chunk['source_url']}")
        jurisdiction_id = _id("jurisdiction", chunk["jurisdiction"])
        regime_id = _id("regime", chunk["regime"])
        section_id = _id("section", f"{chunk['source_title']}|{chunk['section_or_article']}")
        chunk_node_id = _id("chunk", chunk_id)
        provenance = [chunk_id]
        add_node(chunk_node_id, "source_chunk", chunk_id, provenance)
        add_node(source_id, "source", chunk["source_title"], provenance)
        add_node(jurisdiction_id, "jurisdiction", chunk["jurisdiction"], provenance)
        add_node(regime_id, "regime", chunk["regime"], provenance)
        add_node(section_id, "section", chunk["section_or_article"], provenance)
        add_edge(chunk_node_id, source_id, "part_of_source", chunk_id)
        add_edge(chunk_node_id, jurisdiction_id, "has_jurisdiction", chunk_id)
        add_edge(chunk_node_id, regime_id, "classified_as_regime", chunk_id)
        add_edge(chunk_node_id, section_id, "has_section", chunk_id)

    for edge in edges.values():
        edge["provenance"]["source_chunk_ids"] = sorted(set(edge["provenance"]["source_chunk_ids"]))
    return {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "graph_type": "corpus_provenance_foundation",
        "generated_from": "data/corpus/corpus.json",
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": sorted(edges.values(), key=lambda item: (item["source"], item["target"])),
        "limitations": ["Relationships are derived only from corpus metadata; no legal inference or agentic reasoning is implemented."],
    }


def write_sqlite(graph: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS graph_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS graph_nodes (id TEXT PRIMARY KEY, kind TEXT NOT NULL, label TEXT NOT NULL, provenance_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS graph_edges (source TEXT NOT NULL, target TEXT NOT NULL, relation TEXT NOT NULL, provenance_json TEXT NOT NULL, PRIMARY KEY (source, target, relation));
        """)
        connection.execute("DELETE FROM graph_metadata")
        connection.execute("DELETE FROM graph_nodes")
        connection.execute("DELETE FROM graph_edges")
        connection.executemany("INSERT INTO graph_metadata VALUES (?, ?)", [("schema_version", graph["schema_version"]), ("graph_type", graph["graph_type"])])
        connection.executemany("INSERT INTO graph_nodes VALUES (?, ?, ?, ?)", [(n["id"], n["kind"], n["label"], json.dumps(n["provenance"])) for n in graph["nodes"]])
        connection.executemany("INSERT INTO graph_edges VALUES (?, ?, ?, ?)", [(e["source"], e["target"], e["relation"], json.dumps(e["provenance"])) for e in graph["edges"]])


def export(corpus_path: Path = CORPUS_PATH, output_path: Path | None = None, sqlite_path: Path | None = None) -> dict[str, Any]:
    graph = build_graph(json.loads(corpus_path.read_text(encoding="utf-8")))
    output_path = output_path or DATA_DIR / "graph" / "corpus_graph.json"
    sqlite_path = sqlite_path or DATA_DIR / "graph" / "corpus_graph.sqlite3"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    write_sqlite(graph, sqlite_path)
    return graph


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a provenance-only corpus graph artifact.")
    parser.add_argument("--corpus", type=Path, default=CORPUS_PATH)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--sqlite", type=Path, default=None)
    args = parser.parse_args()
    graph = export(args.corpus, args.output, args.sqlite)
    print(f"Exported {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")


if __name__ == "__main__":
    main()