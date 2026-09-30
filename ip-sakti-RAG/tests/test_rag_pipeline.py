from app.query_understanding import analyze_query, fallback_analysis
from app.reranker import rerank
from app.nli_verifier import verify_all_claims, lexical_verify_claim
from app.confidence_model import heuristic_confidence, score_confidence
from app.orchestrator import full_pipeline


def test_query_analysis():
    res = analyze_query("Can I patent a classical turmeric formulation?")
    assert "Patents" in res.get("likely_regimes", []) or "TK" in res.get("likely_regimes", [])


def test_reranker():
    candidates = [
        {
            "chunk_id": "c1",
            "text": "Section 3(p) excludes traditional knowledge from patentability.",
            "metadata": {"source_title": "Patents Act", "section_or_article": "Section 3(p)", "regime": "Patents"},
        }
    ]
    ranked = rerank("patent traditional knowledge", candidates, top_k=1)
    assert len(ranked) == 1
    assert ranked[0]["chunk_id"] == "c1"


def test_nli_verifier_extractive():
    gen_result = {
        "can_answer": True,
        "answer": "Turmeric formulation is not patentable.",
        "claims": [
            {
                "claim_text": "Section 3(p) excludes traditional knowledge.",
                "supporting_passage_numbers": [1],
            }
        ],
        "_chunks_used": [
            {
                "text": "Section 3(p) explicitly excludes traditional knowledge from being patentable subject matter.",
                "metadata": {},
            }
        ],
    }
    verified = verify_all_claims(gen_result)
    assert verified["all_claims_verified"] is True
    assert len(verified["verified_claims"]) == 1
    assert verified["verified_claims"][0]["verified"] is True


def test_confidence_scoring():
    result = {
        "can_answer": True,
        "all_claims_verified": True,
        "_final_chunks": [
            {"relevance_score": 8.5, "rrf_score": 0.05}
        ],
        "verified_claims": [{"verified": True}],
    }
    conf = heuristic_confidence(result)
    assert conf["score"] >= 0.70
    assert conf["abstain"] is False


def test_full_pipeline_answering():
    res = full_pipeline("Can I patent a classical turmeric formulation in India?", jurisdiction="India")
    assert res["abstained"] is False
    assert len(res["answer_text"]) > 100
    assert len(res["citations"]) > 0
