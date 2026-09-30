import pickle
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

from app.config import CONFIDENCE_MODEL_PATH


FEATURE_NAMES = [
    "top_rrf_score",
    "top_rerank_score",
    "claims_verified_ratio",
    "num_chunks_retrieved",
]


def extract_features(result: dict) -> list[float]:
    chunks = result.get("_final_chunks", [])
    top_rrf = chunks[0].get("rrf_score", 0.0) if chunks else 0.0
    top_rerank = chunks[0].get("relevance_score", 0.0) if chunks else 0.0
    claims = result.get("verified_claims", [])
    verified_ratio = (
        sum(1 for claim in claims if claim.get("verified")) / len(claims)
        if claims
        else 0.0
    )
    return [float(top_rrf), float(top_rerank), float(verified_ratio), float(len(chunks))]


def train_confidence_model(
    labeled_data: list[dict],
    save_path: Path = CONFIDENCE_MODEL_PATH,
):
    x = np.array([extract_features(item["result"]) for item in labeled_data])
    y = np.array([int(item["human_judged_correct"]) for item in labeled_data])
    model = LogisticRegression()
    model.fit(x, y)

    save_path.parent.mkdir(parents=True, exist_ok=True)
    with save_path.open("wb") as f:
        pickle.dump(model, f)
    return model


import functools


@functools.lru_cache(maxsize=1)
def load_trained_model(model_path_str: str):
    p = Path(model_path_str)
    if p.exists() and p.stat().st_size > 0:
        try:
            with p.open("rb") as f:
                return pickle.load(f)
        except Exception:
            return None
    return None


def score_confidence(
    result: dict,
    model_path: Path = CONFIDENCE_MODEL_PATH,
) -> dict:
    can_answer = bool(result.get("can_answer", True))
    model = load_trained_model(str(model_path))
    if model is not None:
        try:
            features = np.array([extract_features(result)])
            probs = model.predict_proba(features)[0]
            probability = float(probs[1]) if len(probs) > 1 else float(probs[0])
            return confidence_payload(probability, can_answer=can_answer)
        except Exception:
            pass
    return heuristic_confidence(result)


def heuristic_confidence(result: dict) -> dict:
    chunks = result.get("_final_chunks", [])
    top_rerank = chunks[0].get("relevance_score", 0.0) if chunks else 0.0
    claims = result.get("verified_claims", [])
    can_answer = bool(result.get("can_answer", False))

    if claims:
        verified_ratio = sum(1 for claim in claims if claim.get("verified")) / len(claims)
    elif can_answer and chunks:
        verified_ratio = 0.8
    else:
        verified_ratio = 0.0

    retrieval_divisor = 10.0 if top_rerank > 4.0 else 3.5
    retrieval_score = max(0.0, min(1.0, float(top_rerank) / retrieval_divisor))
    breadth_bonus = min(len(chunks), 5) * 0.04
    probability = (0.50 * retrieval_score) + (0.35 * verified_ratio) + breadth_bonus

    if can_answer and chunks:
        probability = max(0.48, probability)

    if not can_answer:
        probability = min(probability, 0.20)
    elif not result.get("all_claims_verified"):
        probability = min(probability, 0.65)

    return confidence_payload(probability, can_answer=can_answer)


def confidence_payload(probability: float, can_answer: bool = True) -> dict:
    probability = max(0.0, min(1.0, float(probability)))
    if probability >= 0.75:
        label = "High"
    elif probability >= 0.45:
        label = "Medium"
    else:
        label = "Low"
    return {
        "score": round(probability, 3),
        "label": label,
        "abstain": (probability < 0.35) or (not can_answer),
    }

