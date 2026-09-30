from typing import Tuple
from app.config import settings

def evaluate_confidence(score: float) -> Tuple[str, bool, bool]:
    """
    Evaluates similarity/grounding score.
    Returns: (label: str, abstained: bool, escalation_suggested: bool)
    """
    if score >= settings.CONFIDENCE_THRESHOLD_HIGH:
        return "High", False, False
    elif score >= settings.CONFIDENCE_THRESHOLD_LOW:
        return "Medium", False, False
    else:
        return "Low", True, True
