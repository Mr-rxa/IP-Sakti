import json

from app.knowledge_graph import build_graph
from eval.run_evaluation import evaluate


def test_empty_evaluation_is_sparse_safe():
    report = evaluate([])
    assert report["case_count"] == 0
    assert report["citation_accuracy"] is None
    assert report["results"] == []


def test_graph_records_provenance_on_every_node_and_edge():
    graph = build_graph([{
        "chunk_id": "chunk-1",
        "source_title": "Example Act",
        "source_url": "https://example.test/act",
        "jurisdiction": "India",
        "regime": "Patents",
        "section_or_article": "Section 3",
    }])
    assert graph["schema_version"] == "1.0.0"
    assert graph["nodes"]
    assert graph["edges"]
    assert all(node["provenance"]["source_chunk_ids"] for node in graph["nodes"])
    assert all(edge["provenance"]["source_chunk_ids"] for edge in graph["edges"])