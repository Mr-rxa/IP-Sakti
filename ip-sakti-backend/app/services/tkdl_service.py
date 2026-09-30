from typing import List
from sqlalchemy.orm import Session
from app.models.tkdl_demo import TKDLDemoModel
from app.schemas.tkdl import TKDLMatch, TKDLLookupResponse

class TKDLService:
    @staticmethod
    def lookup(db: Session, keyword: str) -> TKDLLookupResponse:
        clean_kw = keyword.strip().lower()
        records = db.query(TKDLDemoModel).all()
        
        matches: List[TKDLMatch] = []
        for r in records:
            if clean_kw in r.formulation_keyword.lower() or any(term in r.matched_note.lower() for term in clean_kw.split()):
                matches.append(
                    TKDLMatch(
                        formulation_keyword=r.formulation_keyword,
                        classification=r.classification,
                        matched_note=r.matched_note,
                        is_illustrative=True
                    )
                )

        return TKDLLookupResponse(matches=matches)
