import re

from app.ingestion import tokenize
from app.llm_client import generate_json, gemini_available


GENERATION_SYSTEM_PROMPT = """You are IP-SAKTI Sahayak, an authoritative, plain-language legal guidance assistant for the Ayurveda, AYUSH, and traditional medicine community (practitioners, startups, researchers, MSMEs, and cultivators).

Your goal: Explain complex intellectual property (IPR) and regulatory law in SIMPLE, CLEAR, PRACTICAL terms so any normal person can easily understand it, while remaining 100% legally grounded and accurate.

Strict rules:
1. Grounding: Rely strictly on the provided context passages. Do not invent laws or provisions.
2. Structure your "answer" in clean, beautiful Markdown with these clear sections:
   ### 📌 Bottom Line
   Give a direct, plain-language answer in 1-2 sentences (e.g., "No, you cannot patent a traditional Ayurvedic turmeric formulation as-is in India...").

   ### 📖 Plain-Language Explanation
   Explain the rationale simply and clearly without confusing legalese. Why does this rule exist? What does the law say in everyday terms?

   ### 💡 What You CAN Do (Practical Pathways)
   Provide concrete, actionable alternatives and pathways (e.g., brand protection via Trademark, patenting novel synergistic combinations with clinical proof of enhanced efficacy, obtaining ABS approval from NBA/SBB, or classical drug manufacturing licensing).

   ### ⚖️ Applicable Legal Provisions
   List the key statutes, sections, and authorities cited from the context (e.g., Section 3(p) of the Patents Act, 1970; Traditional Knowledge Digital Library - TKDL; Biological Diversity Act).

   ### ⚠️ Legal Disclaimer
   Always conclude with: "This is legal information, not legal advice. Please verify with official statutes or a qualified IP professional."

3. Citation Claims:
   Provide an array of distinct factual claims in "claims". Each claim must have a "claim_text" (a clear, concise factual statement) and "supporting_passage_numbers" (integers referencing the [1], [2], etc. passage numbers that support that claim).

4. Jurisdiction:
   Stay strictly inside the requested jurisdiction (India or International).

5. If the context does not have enough information to answer, set "can_answer" to false.

Output only valid JSON with format:
{
  "can_answer": true,
  "answer": "markdown formatted answer with the sections above",
  "claims": [
    {"claim_text": "factual statement", "supporting_passage_numbers": [1]}
  ]
}"""


def generate_grounded_answer(query: str, reranked_chunks: list[dict]) -> dict:
    if not reranked_chunks:
        return {"can_answer": False, "answer": "", "claims": [], "_chunks_used": []}
    if gemini_available():
        try:
            return llm_generate_grounded_answer(query, reranked_chunks)
        except Exception as e:
            print(f"[generate_grounded_answer] LLM generation error ({e}), falling back to extractive.")
    return extractive_grounded_answer(query, reranked_chunks)


def llm_generate_grounded_answer(query: str, reranked_chunks: list[dict]) -> dict:
    numbered_context = "\n\n".join(
        f"[{idx + 1}] ({chunk['metadata']['source_title']} - "
        f"{chunk['metadata']['section_or_article']})\n{chunk['text']}"
        for idx, chunk in enumerate(reranked_chunks)
    )
    result = generate_json(
        f"CONTEXT PASSAGES:\n{numbered_context}\n\nQUESTION: {query}",
        system_instruction=GENERATION_SYSTEM_PROMPT,
        temperature=0.1,
    )
    result.setdefault("claims", [])
    result["_chunks_used"] = reranked_chunks
    return result


def extractive_grounded_answer(query: str, reranked_chunks: list[dict]) -> dict:
    query_tokens = set(tokenize(query))
    selected_claims = []
    answer_parts = []

    for passage_number, chunk in enumerate(reranked_chunks[:3], start=1):
        sentence = best_sentence(chunk.get("text", ""), query_tokens)
        if not sentence:
            continue
        citation = citation_label(chunk)
        answer_parts.append(f"**{citation}**: {sentence}")
        selected_claims.append(
            {
                "claim_text": sentence,
                "supporting_passage_numbers": [passage_number],
            }
        )

    if not answer_parts:
        return {
            "can_answer": False,
            "answer": "I do not have enough grounded source material in the approved corpus to answer this question confidently. This is legal information, not legal advice. Please provide more details or consult a human IP facilitator.",
            "claims": [],
            "_chunks_used": reranked_chunks,
        }

    answer = (
        "### 📌 Summary from Official Legal Corpus\n\n"
        + "\n\n".join([f"• {part}" for part in answer_parts])
        + "\n\n### ⚠️ Legal Disclaimer\n*This is legal information, not legal advice. Please verify with the relevant statute or a qualified legal/IP professional before acting.*"
    )
    return {
        "can_answer": True,
        "answer": answer,
        "claims": selected_claims,
        "_chunks_used": reranked_chunks,
    }


def best_sentence(text: str, query_tokens: set[str]) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ""
    if not query_tokens:
        return sentences[0]

    scored = []
    query_text = " ".join(query_tokens)
    for sentence in sentences:
        tokens = set(tokenize(sentence))
        shared = tokens & query_tokens
        score = len(shared) / max(len(query_tokens), 1)
        lowered = sentence.lower()
        if "not patentable" in lowered:
            score += 0.35
        if "traditional knowledge" in lowered:
            score += 0.2
        if "enhancement" in lowered or "enhanced efficacy" in lowered:
            score += 0.18
        if "3(p)" in query_text and "3(p)" in lowered:
            score += 0.35
        if "3(d)" in query_text and "3(d)" in lowered:
            score += 0.35
        if lowered.startswith("significance:"):
            score -= 0.1
        scored.append((score, sentence))
    scored.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
    return scored[0][1]


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return []
    cleaned = cleaned.replace("e.g.", "e_g_").replace("i.e.", "i_e_")
    pieces = re.split(r"(?<=[.!?])\s+", cleaned)
    restored = [piece.replace("e_g_", "e.g.").replace("i_e_", "i.e.") for piece in pieces]
    return [piece.strip() for piece in restored if len(piece.strip()) > 25]


def citation_label(chunk: dict) -> str:
    metadata = chunk.get("metadata", {})
    title = metadata.get("source_title") or "Source"
    section = metadata.get("section_or_article") or "retrieved passage"
    return f"{title} ({section})"
