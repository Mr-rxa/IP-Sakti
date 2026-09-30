import json
from pathlib import Path
from typing import Dict, List
from app.schemas.abs import ABSChecklistResponse

class ABSService:
    _rules: Dict[str, List[str]] = {}

    @classmethod
    def _load_rules(cls):
        if not cls._rules:
            rules_path = Path(__file__).resolve().parent.parent.parent / "corpus" / "seed_data" / "abs_rules.json"
            if rules_path.exists():
                with open(rules_path, "r", encoding="utf-8") as f:
                    cls._rules = json.load(f)

    @classmethod
    def get_checklist(cls, classification: str) -> ABSChecklistResponse:
        cls._load_rules()
        
        # Match nearest classification key using normalized alphanumeric comparison
        norm_query = "".join(c.lower() for c in classification if c.isalnum())
        matched_items = []

        for key, items in cls._rules.items():
            norm_key = "".join(c.lower() for c in key if c.isalnum())
            if norm_query in norm_key or norm_key in norm_query:
                matched_items = items
                break

        if not matched_items:
            # Fallback to classical/generic rules as safe default
            matched_items = cls._rules.get("Classical/Generic Medicine", [
                "Verify if raw herbs or biological resources are sourced from local cultivators or forest areas within India.",
                "Indian entities utilizing classical biological resources for commercial utilization must give prior intimation to the State Biodiversity Board (SBB) under Section 7 of Biological Diversity Act (BDA), 2002.",
                "Check exemption eligibility under Biological Diversity (Amendment) Act, 2023.",
                "Ensure compliance with National Biodiversity Authority (NBA) guidelines."
            ])

        return ABSChecklistResponse(
            classification=classification,
            checklist=matched_items
        )
