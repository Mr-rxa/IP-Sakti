from typing import Dict, Any, Union
from sqlalchemy.orm import Session
from app.models.session import SessionModel
from app.schemas.classification import (
    ClassificationQuestionResponse,
    ClassificationFinalResultResponse
)
from app.core.exceptions import SessionNotFoundError, ClassificationFlowError

# Complete decision tree questions
QUESTIONS: Dict[str, Dict[str, Any]] = {
    "q1": {
        "text": "Is your formulation drawn directly from a First-Schedule authoritative Ayurvedic text (e.g., Charaka Samhita, Sushruta Samhita) without modification in composition or processing?",
        "options": ["Yes", "No", "Not sure"]
    },
    "q2_non_classical": {
        "text": "Is the intended primary use of the product for systemic therapeutic disease treatment, external topical/beauty care, or general wellness dietary nutrition?",
        "options": ["Therapeutic Treatment", "Dietary / Wellness Food", "External Beauty / Skin Care"]
    },
    "q3_therapeutic": {
        "text": "Does the therapeutic formulation involve a purified, standardized botanical extract fraction (phytopharmaceutical) or an innovative synergistic/modified proprietary drug?",
        "options": ["Standardized Botanical Fraction", "Proprietary / Modified Formulation", "Completely Novel Unlisted Compound"]
    }
}

# Mapping outcomes
RESULTS: Dict[str, Dict[str, Any]] = {
    "classical": {
        "classification_result": "Classical/Generic Medicine",
        "explanation": "Because this formulation is drawn from a First-Schedule authoritative text, it is treated as public domain Traditional Knowledge (TK) and faces the statutory Section 3(p) patent bar under the Indian Patents Act, 1970. It is protected defensively via the Traditional Knowledge Digital Library (TKDL).",
        "relevant_regimes": ["Patents", "TK", "ABS", "DrugRegulation"],
        "required_ip_checks": [
            "Verify presence in TKDL to establish prior art status",
            "Patent bar under Section 3(p) applies to identical compositions",
            "Trademarks can be registered for unique brand names (not generic terms)",
            "Ensure packaging designs do not infringe existing design registrations"
        ],
        "required_regulatory_checks": [
            "Manufacturing license under Drugs and Cosmetics Act (Schedule T - GMP)",
            "Proof of reference in authoritative treatises listed in First Schedule",
            "Intimation to State Biodiversity Board (SBB) for commercial bio-resource procurement"
        ]
    },
    "proprietary": {
        "classification_result": "Patent-or-Proprietary Medicine",
        "explanation": "This is a modified formulation or proprietary blend containing Ayurvedic ingredients. It is eligible for patenting only if non-obvious synergistic efficacy is proven beyond Section 3(p) and 3(e) hurdles, alongside mandatory NBA clearance under Section 6 of Biological Diversity Act.",
        "relevant_regimes": ["Patents", "ABS", "Trademarks", "DrugRegulation"],
        "required_ip_checks": [
            "NBA Form III approval prior to patent application grant",
            "Establish synergistic bio-activity data to overcome Section 3(e) mere admixture bar",
            "Freedom-to-operate search across patent databases and TKDL",
            "Trademark filing for proprietary formulation name"
        ],
        "required_regulatory_checks": [
            "Proprietary Ayurvedic medicine license from State Licensing Authority",
            "Safety and efficacy pilot clinical data",
            "Benefit sharing agreement with National/State Biodiversity authorities"
        ]
    },
    "phytopharmaceutical": {
        "classification_result": "Phytopharmaceutical",
        "explanation": "Phytopharmaceuticals are purified, standardized fractions of botanical resources with defined minimum active markers. They undergo CDSCO New Drug approval pathways and require strict provenance traceability and ABS benefit-sharing.",
        "relevant_regimes": ["Patents", "ABS", "DrugRegulation"],
        "required_ip_checks": [
            "Patentability of novel extraction methods, isolated fractions, or specific synergistic combinations",
            "Mandatory NBA Section 6 approval prior to filing domestic/international patent applications",
            "Global patent filings via PCT with origin disclosure per WIPO 2024 treaty"
        ],
        "required_regulatory_checks": [
            "CDSCO New Drug approval (Form 44 / Schedule Y / New Drugs Rules 2019)",
            "Phase I-IV clinical trial requirements",
            "SBB/NBA benefit-sharing execution"
        ]
    },
    "new_drug": {
        "classification_result": "New/Non-classical Drug",
        "explanation": "Formulations incorporating novel active chemical entities or drastically modified herbal derivatives are treated under the full New Drug regulatory regime, requiring comprehensive preclinical and clinical dossiers.",
        "relevant_regimes": ["Patents", "ABS", "DrugRegulation"],
        "required_ip_checks": [
            "Full patent examination under Indian Patents Act / TRIPS baseline",
            "Prior art search in global databases (WIPO, USPTO, EPO, InPASS)",
            "NBA access and benefit sharing approvals"
        ],
        "required_regulatory_checks": [
            "CDSCO Investigational New Drug (IND) approval and trial registry (CTRI)",
            "Strict non-clinical toxicological safety dossiers"
        ]
    },
    "aahar": {
        "classification_result": "Ayurveda-Aahar/Nutraceutical",
        "explanation": "Categorized under FSSAI (Ayurveda Aahar) Regulations, 2022. Not considered a drug; therapeutic claims are restricted, but trademark and trade dress protections are primary.",
        "relevant_regimes": ["Food", "Trademarks", "ABS", "Advertising"],
        "required_ip_checks": [
            "Brand name trademark registration under Nice Class 5 / 30",
            "Packaging and trade dress design protection under Designs Act, 2000",
            "Check that recipe or branding does not infringe protected Geographical Indications (GI)"
        ],
        "required_regulatory_checks": [
            "FSSAI Ayurveda-Aahar license and compliance with Schedule A food lists",
            "Strict compliance with non-medicinal marketing & prohibition of misleading disease cure claims",
            "State Biodiversity Board (SBB) notification for commercial utilization"
        ]
    },
    "cosmetic": {
        "classification_result": "Cosmetic",
        "explanation": "Governed by Cosmetics Rules, 2020. Protectable primarily via Trademarks, Industrial Designs, and process patents for novel cosmetic carriers.",
        "relevant_regimes": ["Cosmetics", "Trademarks", "Designs", "ABS", "Advertising"],
        "required_ip_checks": [
            "Trademark protection under Nice Class 3 (cosmetics and cleaning preparations)",
            "Industrial design registration for innovative bottle, jar, or dispenser packaging",
            "Process patent eligibility for unique stable cosmetic formulation carriers"
        ],
        "required_regulatory_checks": [
            "Cosmetic manufacturing license under Drugs and Cosmetics Act",
            "Compliance with Schedule S (Bureau of Indian Standards safety standards for cosmetics)",
            "Compliance with Drugs and Magic Remedies Act regarding beauty/aging claims"
        ]
    }
}

class ClassificationService:
    @staticmethod
    def start_flow(db: Session, session_id: str) -> ClassificationQuestionResponse:
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)
        
        session.current_question_id = "q1"
        db.commit()

        q1 = QUESTIONS["q1"]
        return ClassificationQuestionResponse(
            question_id="q1",
            question_text=q1["text"],
            options=q1["options"]
        )

    @staticmethod
    def answer_question(
        db: Session,
        session_id: str,
        question_id: str,
        answer: str
    ) -> Union[ClassificationQuestionResponse, ClassificationFinalResultResponse]:
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not session:
            raise SessionNotFoundError(session_id)

        clean_answer = answer.strip().lower()

        # State transition logic
        if question_id == "q1":
            if clean_answer in ["yes"]:
                res = RESULTS["classical"]
                session.classification_result = res["classification_result"]
                session.current_question_id = None
                db.commit()
                return ClassificationFinalResultResponse(**res)
            else:
                session.current_question_id = "q2_non_classical"
                db.commit()
                q2 = QUESTIONS["q2_non_classical"]
                return ClassificationQuestionResponse(
                    next_question_id="q2_non_classical",
                    question_text=q2["text"],
                    options=q2["options"]
                )

        elif question_id == "q2_non_classical":
            if "beauty" in clean_answer or "skin" in clean_answer or "cosmetic" in clean_answer:
                res = RESULTS["cosmetic"]
                session.classification_result = res["classification_result"]
                session.current_question_id = None
                db.commit()
                return ClassificationFinalResultResponse(**res)
            elif "food" in clean_answer or "dietary" in clean_answer or "wellness" in clean_answer:
                res = RESULTS["aahar"]
                session.classification_result = res["classification_result"]
                session.current_question_id = None
                db.commit()
                return ClassificationFinalResultResponse(**res)
            else:
                session.current_question_id = "q3_therapeutic"
                db.commit()
                q3 = QUESTIONS["q3_therapeutic"]
                return ClassificationQuestionResponse(
                    next_question_id="q3_therapeutic",
                    question_text=q3["text"],
                    options=q3["options"]
                )

        elif question_id == "q3_therapeutic":
            if "botanical" in clean_answer or "fraction" in clean_answer:
                res = RESULTS["phytopharmaceutical"]
            elif "novel" in clean_answer or "unlisted" in clean_answer:
                res = RESULTS["new_drug"]
            else:
                res = RESULTS["proprietary"]

            session.classification_result = res["classification_result"]
            session.current_question_id = None
            db.commit()
            return ClassificationFinalResultResponse(**res)

        else:
            raise ClassificationFlowError(f"Unknown question_id: {question_id}")
