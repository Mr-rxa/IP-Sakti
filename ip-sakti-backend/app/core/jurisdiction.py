from enum import Enum
from typing import Dict, Any

class JurisdictionEnum(str, Enum):
    INDIA = "India"
    INTERNATIONAL = "International"

def get_jurisdiction_filter(jurisdiction: JurisdictionEnum) -> Dict[str, Any]:
    """
    Returns retrieval metadata filter to enforce strict legal boundary separation.
    Never mixes India and International corpus text.
    """
    return {"jurisdiction": jurisdiction.value}
