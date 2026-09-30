import re

from app.llm_client import generate_json, generate_text, gemini_available


REGIME_KEYWORDS = {
    "Patents": [
        "patent",
        "section 3",
        "3(p)",
        "3(d)",
        "novel",
        "inventive",
        "pct",
        "budapest",
    ],
    "GI": ["geographical indication", "gi", "origin", "community name"],
    "Trademarks": ["trademark", "trade mark", "brand", "logo", "madrid"],
    "Designs": ["design", "shape", "packaging design", "hague"],
    "Copyright": ["copyright", "literary", "artistic", "label artwork"],
    "PlantVariety": ["plant variety", "seed", "farmer", "ppv", "variety"],
    "ABS": [
        "biodiversity",
        "biological resource",
        "abs",
        "nba",
        "sbb",
        "bmc",
        "benefit sharing",
        "nagoya",
        "plant",
        "plants",
        "herb",
        "herbs",
        "botanical",
        "species",
        "cultivat",
        "raw material",
        "forest",
    ],
    "DrugRegulation": [
        "drug",
        "ayush",
        "phytopharmaceutical",
        "botanical",
        "clinical",
        "medicine",
        "medicines",
        "product",
        "formulation",
        "formulations",
        "gmp",
        "licensing",
        "license",
    ],
    "Advertising": ["advertisement", "claim", "cure", "magic remedy"],
    "Food": ["food", "aahara", "aahar", "nutraceutical", "fssai"],
    "TK": ["traditional knowledge", "tkdl", "classical", "ayurveda text", "prior art"],
}

QUERY_ANALYSIS_PROMPT = """You are a query analysis module for a legal retrieval system
covering Ayurveda IPR and regulatory law.

Given a user's question, output a JSON object with:
- "rewritten_query": a clearer, more specific restatement of the question, optimized for retrieval
- "sub_questions": a list of 1-4 distinct sub-questions
- "likely_regimes": likely regimes from ["Patents", "GI", "Trademarks", "Designs",
  "Copyright", "PlantVariety", "ABS", "DrugRegulation", "Advertising", "Food", "TK"]
- "is_multi_step": true if the answer requires more than one regime or classification category

Output only valid JSON."""

HYDE_PROMPT = """You are a legal retrieval assistant for Indian and international Ayurveda
IPR and regulatory law. Write a short hypothetical legal-style passage that would be
useful for retrieving sources for the user's question. Do not present it as truth."""


def analyze_query(query: str) -> dict:
    if gemini_available():
        try:
            res = generate_json(query, system_instruction=QUERY_ANALYSIS_PROMPT)
            if res and isinstance(res, dict):
                return normalize_analysis(query, res)
        except Exception as e:
            print(f"[analyze_query] LLM analysis error ({e}), using fallback.")
    return fallback_analysis(query)


def generate_hyde_passage(query: str) -> str:
    if gemini_available():
        try:
            passage = generate_text(query, system_instruction=HYDE_PROMPT)
            if passage and passage.strip():
                return passage.strip()
        except Exception as e:
            print(f"[generate_hyde_passage] LLM HyDE error ({e}), using raw query.")
    return query


def fallback_analysis(query: str) -> dict:
    lowered = query.lower()
    regimes = [
        regime
        for regime, keywords in REGIME_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]
    if not regimes:
        regimes = ["Patents", "TK"] if "ayur" in lowered else []

    sub_questions = split_sub_questions(query)
    rewritten = expand_query(query.strip(), regimes)
    if regimes:
        rewritten = f"{rewritten} Relevant regimes: {', '.join(regimes)}."

    multi_step_markers = ["modify", "changed", "export", "and", "also", "compare", "versus"]
    return {
        "rewritten_query": rewritten,
        "sub_questions": sub_questions,
        "likely_regimes": regimes,
        "is_multi_step": len(regimes) > 1 or any(marker in lowered for marker in multi_step_markers),
    }


def expand_query(query: str, regimes: list[str]) -> str:
    lowered = query.lower()
    expansions: list[str] = []

    if any(term in lowered for term in ["classical", "traditional", "grandmother", "turmeric", "neem", "ashwagandha"]):
        expansions.append("traditional knowledge Section 3(p) TKDL prior art")
    if any(term in lowered for term in ["modified", "modify", "changed", "change", "ratio", "new form", "new use"]):
        expansions.append("Section 3(d) known substance evergreening enhanced efficacy")
    if any(term in lowered for term in ["biological resource", "plant", "herb", "genetic resource"]):
        expansions.append("access and benefit sharing National Biodiversity Authority")
    if "Patents" in regimes and "patent" not in lowered:
        expansions.append("patentability invention inventive step")

    if not expansions:
        return query
    return f"{query}. {' '.join(expansions)}"


def normalize_analysis(original_query: str, result: dict) -> dict:
    regimes = result.get("likely_regimes") or []
    if isinstance(regimes, str):
        regimes = [regimes]
    regimes = [str(regime) for regime in regimes if str(regime) in REGIME_KEYWORDS]

    sub_questions = result.get("sub_questions") or [result.get("rewritten_query") or original_query]
    if isinstance(sub_questions, str):
        sub_questions = [sub_questions]
    sub_questions = [str(item).strip() for item in sub_questions if str(item).strip()]

    return {
        "rewritten_query": str(result.get("rewritten_query") or original_query).strip(),
        "sub_questions": sub_questions[:4] or [original_query],
        "likely_regimes": regimes,
        "is_multi_step": bool(result.get("is_multi_step", len(regimes) > 1)),
    }


def split_sub_questions(query: str) -> list[str]:
    pieces = re.split(r"\?\s+|;\s+", query)
    cleaned = [piece.strip(" ?.") for piece in pieces if piece.strip(" ?.")]
    if len(cleaned) <= 1:
        return [query.strip()]
    return cleaned[:4]
