import hashlib

from app.confidence_model import score_confidence
from app.query_understanding import analyze_query, generate_hyde_passage
from app.self_correction import answer_with_self_correction
from app.config import CORPUS_ONLY, MIN_RETRIEVAL_RESULTS, normalize_jurisdiction


CLASSIFICATION_REGIME_HINTS = {
    "Classical/Generic Medicine": ["Patents", "TK", "ABS"],
    "Patent-or-Proprietary Medicine": ["Patents", "Trademarks", "DrugRegulation"],
    "New/Non-classical Drug": ["Patents", "DrugRegulation", "ABS"],
    "Phytopharmaceutical": ["Patents", "DrugRegulation", "ABS"],
    "Ayurveda-Aahar/Nutraceutical": ["Food", "Advertising", "DrugRegulation"],
    "Cosmetic": ["Trademarks", "Designs", "Advertising"],
}

_CACHE: dict[str, dict] = {}

LEGAL_DISCLAIMER = (
    "This is legal information, not legal advice. Please verify with the official statute, "
    "rule, treaty, or a qualified legal/IP professional before taking action."
)

DOMAIN_TERMS = {
    # Core AYUSH & Traditional Knowledge
    "ayurveda",
    "ayurvedic",
    "ayush",
    "siddha",
    "unani",
    "sowa-rigpa",
    "traditional knowledge",
    "traditional medicine",
    "traditional",
    "tkdl",
    "classical",
    "proprietary",
    "prior art",
    "charaka",
    "sushruta",
    "first schedule",

    # Biological Resources & Plants & Biodiversity (ABS)
    "plant",
    "plants",
    "herb",
    "herbs",
    "herbal",
    "botanical",
    "botanics",
    "biological resource",
    "biological resources",
    "genetic resource",
    "genetic resources",
    "biodiversity",
    "benefit sharing",
    "abs",
    "nba",
    "sbb",
    "bmc",
    "nagoya",
    "cbd",
    "access and benefit sharing",
    "cultivation",
    "cultivator",
    "wild harvest",
    "raw material",
    "species",
    "flora",
    "fauna",

    # IPR Regimes
    "ipr",
    "intellectual property",
    "patent",
    "patents",
    "patentability",
    "section 3",
    "3(p)",
    "3(d)",
    "3(c)",
    "3(e)",
    "novel",
    "inventive step",
    "synergy",
    "synergistic",
    "efficacy",
    "enhanced efficacy",
    "evergreening",
    "copyright",
    "trademark",
    "trade mark",
    "brand",
    "logo",
    "geographical indication",
    "gi tag",
    "design",
    "designs",
    "design right",
    "plant variety",
    "ppv",

    # Product & Regulatory Regimes
    "product",
    "formulation",
    "formulations",
    "medicine",
    "medicines",
    "drug",
    "drugs",
    "drug regulation",
    "phytopharmaceutical",
    "nutraceutical",
    "ayurveda aahar",
    "aahar",
    "aahara",
    "food",
    "fssai",
    "cosmetic",
    "cosmetics",
    "clinical",
    "gmp",
    "licensing",
    "license",
    "magic remedy",
    "advertisement",
    "advertising",
    "claim",
    "compliance",

    # International Systems
    "trips",
    "wipo",
    "gratk",
    "pct",
    "madrid",
    "hague",
    "budapest",
    "budapest treaty",
    "madrid system",
    "hague system",
    "export",
    "exporting",
    "import",
}



def full_pipeline(
    query: str,
    jurisdiction: str = "India",
    classification_context: str | None = None,
) -> dict:
    normalized_jurisdiction = normalize_jurisdiction(jurisdiction)
    cache_key = make_cache_key(query, normalized_jurisdiction, classification_context)
    if cache_key in _CACHE:
        return dict(_CACHE[cache_key])

    analysis = analyze_query(query)
    effective_query = analysis.get("rewritten_query") or query
    if classification_context:
        effective_query = (
            f"{effective_query}\nClassification context: {classification_context}. "
            f"Relevant legal regimes: {', '.join(CLASSIFICATION_REGIME_HINTS.get(classification_context, []))}."
        )

    if not valid_jurisdiction_intent(query, normalized_jurisdiction):
        payload = abstention_payload(
            analysis,
            result={"_final_chunks": [], "verified_claims": []},
            confidence={"score": 0.0, "label": "Low"},
            message=(
                "I can answer only one jurisdiction at a time. Please select either India or International "
                "and ask the question again."
            ),
        )
        payload["jurisdiction"] = normalized_jurisdiction
        payload["disclaimer"] = LEGAL_DISCLAIMER
        _CACHE[cache_key] = payload
        return dict(payload)

    has_domain_term = any(term in query.lower() for term in DOMAIN_TERMS)
    has_regimes = bool(analysis.get("likely_regimes"))
    if CORPUS_ONLY and not (has_domain_term or has_regimes or classification_context):
        payload = abstention_payload(
            analysis,
            message="I can answer only Ayurveda IPR and regulatory questions covered by the approved corpus.",
        )
        payload["jurisdiction"] = normalized_jurisdiction
        payload["disclaimer"] = LEGAL_DISCLAIMER
        _CACHE[cache_key] = payload
        return dict(payload)

    # HyDE is helpful for dense retrieval; in BM25-only mode it simply returns the query.
    hyde = generate_hyde_passage(effective_query)
    retrieval_query = f"{effective_query}\n{hyde}" if hyde != effective_query else effective_query

    regime_filter = choose_regime_filter(analysis, classification_context)
    result = answer_with_self_correction(
        effective_query,
        normalized_jurisdiction,
        max_retries=1,
        regime_filter=regime_filter,
        retrieval_query=retrieval_query,
    )

    if CORPUS_ONLY and len(result.get("_final_chunks", [])) < MIN_RETRIEVAL_RESULTS:
        payload = abstention_payload(
            analysis,
            result,
            message="I could not find enough relevant material in the approved corpus to answer this confidently.",
        )
        payload["jurisdiction"] = normalized_jurisdiction
        payload["disclaimer"] = LEGAL_DISCLAIMER
        _CACHE[cache_key] = payload
        return dict(payload)

    if not result.get("can_answer"):
        payload = abstention_payload(analysis, result, message="Not enough grounded source material to answer this confidently.")
        payload["jurisdiction"] = normalized_jurisdiction
        payload["disclaimer"] = LEGAL_DISCLAIMER
        _CACHE[cache_key] = payload
        return dict(payload)

    confidence = score_confidence(result)
    if confidence.get("abstain"):
        payload = abstention_payload(analysis, result, confidence, message="The retrieved source base is too weak or incomplete for a reliable legal answer.")
        payload["jurisdiction"] = normalized_jurisdiction
        payload["disclaimer"] = LEGAL_DISCLAIMER
        _CACHE[cache_key] = payload
        return dict(payload)

    if len(_CACHE) > 500:
        _CACHE.clear()

    payload = {
        "jurisdiction": normalized_jurisdiction,
        "answer_text": result.get("answer", ""),
        "citations": collect_citations(result),
        "confidence_score": confidence["score"],
        "confidence_label": confidence["label"],
        "abstained": False,
        "escalation_suggested": False,
        "query_analysis": analysis,
        "retrieved_chunk_ids": [
            chunk.get("chunk_id", "") for chunk in result.get("_final_chunks", [])
        ],
        "claim_verification_detail": result.get("verified_claims", []),
        "classification_context": classification_context,
        "disclaimer": LEGAL_DISCLAIMER,
    }
    _CACHE[cache_key] = payload
    return dict(payload)


def choose_regime_filter(
    analysis: dict,
    classification_context: str | None = None,
) -> list[str] | None:
    regimes = set(analysis.get("likely_regimes") or [])
    if classification_context:
        regimes.update(CLASSIFICATION_REGIME_HINTS.get(classification_context, []))
    if not regimes:
        return None
    # Keep filtering broad enough to avoid hiding supporting law from adjacent regimes.
    return sorted(regimes) if len(regimes) <= 4 else None


def collect_citations(result: dict) -> list[dict]:
    chunks = result.get("_final_chunks", [])
    cited_indexes: list[int] = []
    for claim in result.get("verified_claims", []):
        if not claim.get("verified"):
            continue
        for passage_number in claim.get("supporting_passage_numbers", []):
            try:
                index = int(passage_number) - 1
                if 0 <= index < len(chunks):
                    cited_indexes.append(index)
            except (ValueError, TypeError):
                continue

    if not cited_indexes:
        for claim in result.get("claims", []):
            for passage_number in claim.get("supporting_passage_numbers", []):
                try:
                    index = int(passage_number) - 1
                    if 0 <= index < len(chunks):
                        cited_indexes.append(index)
                except (ValueError, TypeError):
                    continue

    if not cited_indexes:
        cited_indexes = list(range(min(3, len(chunks))))

    citations = []
    seen: set[str] = set()
    for index in cited_indexes:
        chunk = chunks[index]
        metadata = chunk.get("metadata", {})
        chunk_id = chunk.get("chunk_id", "")
        key = chunk_id or f"{metadata.get('source_title')}::{metadata.get('section_or_article')}"
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            {
                "chunk_id": chunk_id,
                "source_title": metadata.get("source_title", ""),
                "section_or_article": metadata.get("section_or_article", ""),
                "jurisdiction": metadata.get("jurisdiction", ""),
                "regime": metadata.get("regime", ""),
                "source_url": metadata.get("source_url", ""),
            }
        )
    return citations


def abstention_payload(
    analysis: dict,
    result: dict | None = None,
    confidence: dict | None = None,
    message: str | None = None,
    classification_context: str | None = None,
) -> dict:
    result = result or {}
    confidence = confidence or {"score": 0.0, "label": "Low"}
    return {
        "answer_text": message or "I do not have enough grounded information in my sources to answer this confidently.",
        "citations": [],
        "confidence_score": confidence["score"],
        "confidence_label": confidence["label"],
        "abstained": True,
        "escalation_suggested": True,
        "query_analysis": analysis,
        "retrieved_chunk_ids": [
            chunk.get("chunk_id", "") for chunk in result.get("_final_chunks", [])
        ],
        "claim_verification_detail": result.get("verified_claims", []),
        "classification_context": classification_context,
        "disclaimer": LEGAL_DISCLAIMER,
    }


def valid_jurisdiction_intent(query: str, jurisdiction: str) -> bool:
    if not jurisdiction:
        return False
    normalized = jurisdiction.strip().lower()
    return normalized in {"india", "international"}


def make_cache_key(
    query: str,
    jurisdiction: str,
    classification_context: str | None,
) -> str:
    raw = f"{query}|{jurisdiction}|{classification_context or ''}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()
