"""Run the labeled query set and write a compact, repeatable evaluation report."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def load_cases(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    data = json.loads(raw)
    if isinstance(data, dict):
        data = data.get("queries", data.get("cases", []))
    if not isinstance(data, list):
        raise ValueError("labeled query file must contain a list or a queries/cases list")
    return data


def evaluate(cases: list[dict]) -> dict:
    if not cases:
        return {
            "report_version": 1,
            "case_count": 0,
            "abstention_accuracy": None,
            "jurisdiction_accuracy": None,
            "answer_accuracy": None,
            "citation_accuracy": None,
            "abstained_count": 0,
            "citation_coverage": None,
            "metric_notes": {
                "empty_dataset": "Metrics are null when labeled_queries.json contains no cases.",
                "labels": "Answer and citation accuracy use only cases declaring expected_answer_contains or expected_citation_source_title.",
            },
            "results": [],
        }

    from app.orchestrator import full_pipeline
    results = []
    for case in cases:
        query = case.get("query_text", case.get("query", ""))
        jurisdiction = case.get("jurisdiction", "India")
        actual = full_pipeline(query, jurisdiction=jurisdiction, classification_context=case.get("classification_context"))
        expected_abstained = case.get("expected_abstained", case.get("abstained"))
        abstention_match = expected_abstained is None or bool(actual["abstained"]) == bool(expected_abstained)
        expected_jurisdiction = case.get("expected_jurisdiction", jurisdiction)
        jurisdiction_match = (
            expected_jurisdiction is None
            or actual.get("jurisdiction") == expected_jurisdiction
        )
        answer_labelled = "expected_answer_contains" in case
        expected_text = [str(value).lower() for value in case.get("expected_answer_contains", [])]
        answer_match = (
            not answer_labelled
            or not expected_text
            or all(value in actual.get("answer_text", "").lower() for value in expected_text)
        )
        expected_source = case.get("expected_citation_source_title")
        citation_labelled = expected_source is not None
        citation_match = (
            expected_source is None
            or any(item.get("source_title") == expected_source for item in actual.get("citations", []))
        )
        results.append({
            "query": query,
            "expected_abstained": expected_abstained,
            "expected_jurisdiction": expected_jurisdiction,
            "actual": actual,
            "abstention_match": abstention_match,
            "jurisdiction_match": jurisdiction_match,
            "answer_match": answer_match,
            "citation_match": citation_match,
            "answer_labelled": answer_labelled,
            "citation_labelled": citation_labelled,
        })

    count = len(results)
    answer_labeled = [item for item in results if item["answer_labelled"]]
    citation_labeled = [item for item in results if item["citation_labelled"]]
    return {
        "report_version": 1,
        "case_count": count,
        "abstention_accuracy": (sum(item["abstention_match"] for item in results) / count if count else None),
        "jurisdiction_accuracy": (sum(item["jurisdiction_match"] for item in results) / count if count else None),
        "answer_accuracy": (sum(item["answer_match"] for item in answer_labeled) / len(answer_labeled) if answer_labeled else None),
        "citation_accuracy": (sum(item["citation_match"] for item in citation_labeled) / len(citation_labeled) if citation_labeled else None),
        "abstained_count": sum(item["actual"]["abstained"] for item in results),
        "citation_coverage": (sum(bool(item["actual"]["citations"]) for item in results) / count if count else None),
        "metric_notes": {
            "empty_dataset": "Metrics are null when labeled_queries.json contains no cases.",
            "labels": "Answer and citation accuracy use only cases declaring expected_answer_contains or expected_citation_source_title.",
        },
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate IP-SAKTI labeled queries.")
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("labeled_queries.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("evaluation_report.json"))
    args = parser.parse_args()
    report = evaluate(load_cases(args.input))
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Evaluated {report['case_count']} labeled queries; report written to {args.output}")


if __name__ == "__main__":
    main()