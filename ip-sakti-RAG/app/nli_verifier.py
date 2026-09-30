from app.ingestion import tokenize
from app.llm_client import generate_json, gemini_available


NLI_PROMPT = """You are a strict fact-verification system. Given a passage and a claim,
return JSON with:
{"relationship": "entailment" | "contradiction" | "neutral", "reasoning": "one sentence"}

Use entailment only when the passage directly supports the claim."""


NEGATION_WORDS = {"not", "no", "never", "without", "prohibited", "cannot", "exempt", "exemption"}


def verify_claim(claim_text: str, passage_text: str) -> dict:
    if gemini_available():
        try:
            res = generate_json(
                f"PASSAGE:\n{passage_text[:1200]}\n\nCLAIM:\n{claim_text}",
                system_instruction=NLI_PROMPT,
                temperature=0.0,
            )
            if res and isinstance(res, dict) and "relationship" in res:
                return res
        except Exception as e:
            print(f"[verify_claim] LLM NLI error ({e}), falling back to lexical.")
    return lexical_verify_claim(claim_text, passage_text)


def lexical_verify_claim(claim_text: str, passage_text: str) -> dict:
    claim_tokens = meaningful_tokens(claim_text)
    passage_tokens = meaningful_tokens(passage_text)
    if not claim_tokens:
        return {"relationship": "neutral", "reasoning": "No meaningful claim tokens."}

    claim_neg = bool(claim_tokens & NEGATION_WORDS)
    passage_neg = bool(passage_tokens & NEGATION_WORDS)

    ratio = len(claim_tokens & passage_tokens) / len(claim_tokens)
    
    if ratio >= 0.35:
        if claim_neg != passage_neg and (claim_tokens & NEGATION_WORDS or passage_tokens & NEGATION_WORDS):
            relationship = "contradiction"
        else:
            relationship = "entailment"
    else:
        relationship = "neutral"

    return {
        "relationship": relationship,
        "reasoning": f"Lexical support ratio {ratio:.2f} (polarities aligned: {claim_neg == passage_neg}).",
    }


def verify_all_claims(generation_result: dict) -> dict:
    chunks = generation_result.get("_chunks_used", [])
    verified_claims = []
    has_contradiction = False

    claims = generation_result.get("claims", [])

    for claim in claims:
        passage_nums = claim.get("supporting_passage_numbers") or []
        claim_ok = False
        best_check = None
        for passage_number in passage_nums:
            try:
                p_num = int(passage_number)
            except (ValueError, TypeError):
                continue
            if p_num < 1 or p_num > len(chunks):
                continue
            passage_text = chunks[p_num - 1].get("text", "")
            check = verify_claim(claim.get("claim_text", ""), passage_text)
            best_check = check
            if check.get("relationship") == "entailment":
                claim_ok = True
                break
            elif check.get("relationship") == "contradiction":
                has_contradiction = True
        verified_claims.append(
            {**claim, "verification": best_check, "verified": claim_ok}
        )

    verified_count = sum(1 for c in verified_claims if c.get("verified"))
    if not claims:
        all_ok = bool(chunks and generation_result.get("can_answer"))
    elif has_contradiction:
        all_ok = False
    else:
        all_ok = (verified_count >= max(1, len(verified_claims) // 2))

    generation_result["verified_claims"] = verified_claims
    generation_result["all_claims_verified"] = all_ok
    return generation_result


def meaningful_tokens(text: str) -> set[str]:
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "for",
        "from",
        "by",
        "with",
        "as",
        "is",
        "are",
        "be",
        "this",
        "that",
        "it",
    }
    return {token for token in tokenize(text) if token not in stop_words and len(token) > 2}

