from app.generation import generate_grounded_answer
from app.hybrid_retrieval import hybrid_retrieve
from app.nli_verifier import verify_all_claims
from app.reranker import rerank


def answer_with_self_correction(
    query: str,
    jurisdiction: str,
    max_retries: int = 1,
    regime_filter: list[str] | None = None,
    retrieval_query: str | None = None,
) -> dict:
    attempt = 0
    feedback = ""
    last_result: dict = {
        "can_answer": False,
        "answer": "",
        "verified_claims": [],
        "all_claims_verified": False,
        "_final_chunks": [],
    }

    while attempt <= max_retries:
        search_query = retrieval_query or query
        if feedback:
            search_query = f"{search_query} Retrieval focus: {feedback}"

        candidates = hybrid_retrieve(
            search_query,
            jurisdiction,
            top_k=20,
            regime_filter=regime_filter,
        )
        reranked = rerank(query, candidates, top_k=5)

        if not reranked:
            return last_result

        generated = generate_grounded_answer(query, reranked)
        generated["_final_chunks"] = reranked

        if not generated.get("can_answer"):
            return generated

        verified = verify_all_claims(generated)
        verified["_final_chunks"] = reranked
        last_result = verified

        if verified.get("all_claims_verified"):
            return verified

        failed_claims = [
            claim.get("claim_text", "")
            for claim in verified.get("verified_claims", [])
            if not claim.get("verified")
        ]
        feedback = "; ".join(failed_claims[:2])
        attempt += 1

    return last_result
