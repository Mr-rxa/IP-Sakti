from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.config import normalize_jurisdiction
from app.orchestrator import full_pipeline


app = FastAPI(title="IP-SAKTI Sahayak RAG API", version="0.1.0")

SESSIONS: dict[str, dict] = {}
CLASSIFICATION_STATE: dict[str, dict] = {}
ESCALATIONS: dict[str, dict] = {}


class JurisdictionRequest(BaseModel):
    jurisdiction: str = Field(..., examples=["India"])


class SessionRequest(BaseModel):
    session_id: str


class ClassificationAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class QueryRequest(BaseModel):
    session_id: str | None = None
    query_text: str
    jurisdiction: str | None = None
    classification_context: str | None = None


class EscalationRequest(BaseModel):
    session_id: str
    query_id: str | None = None
    user_contact_optional: str | None = None


class TranslateRequest(BaseModel):
    text: str
    target_language: str = Field(..., examples=["hi"])


QUESTIONS = {
    "q1": {
        "question_id": "q1",
        "question_text": "Is your formulation drawn directly from a First-Schedule authoritative Ayurveda text without modification?",
        "options": ["Yes", "No", "Not sure"],
    },
    "q2": {
        "question_id": "q2",
        "question_text": "Is the product intended as food or nutraceutical without disease-cure or treatment claims?",
        "options": ["Yes", "No", "Not sure"],
    },
    "q3": {
        "question_id": "q3",
        "question_text": "Is it a standardized plant extract or botanical therapeutic product needing drug-style approval?",
        "options": ["Yes", "No", "Not sure"],
    },
    "q4": {
        "question_id": "q4",
        "question_text": "Does it contain a genuinely new formulation, process, dosage form, or technical improvement?",
        "options": ["Yes", "No", "Not sure"],
    },
}

FINAL_CLASSIFICATIONS = {
    "Classical/Generic Medicine": {
        "classification_result": "Classical/Generic Medicine",
        "explanation": "The product appears to come directly from authoritative traditional knowledge, so patentability questions should focus on the Patents Act traditional-knowledge bar and TKDL/prior-art risk.",
        "relevant_regimes": ["Patents", "TK", "ABS"],
    },
    "Ayurveda-Aahar/Nutraceutical": {
        "classification_result": "Ayurveda-Aahar/Nutraceutical",
        "explanation": "The product appears closer to an Ayurveda-Aahar or food/nutraceutical pathway, where FSSAI rules and advertising limits are central.",
        "relevant_regimes": ["Food", "Advertising", "DrugRegulation"],
    },
    "Phytopharmaceutical": {
        "classification_result": "Phytopharmaceutical",
        "explanation": "The product appears to involve a botanical or plant-extract therapeutic pathway, so drug regulation, patents, and biodiversity access compliance matter.",
        "relevant_regimes": ["DrugRegulation", "Patents", "ABS"],
    },
    "New/Non-classical Drug": {
        "classification_result": "New/Non-classical Drug",
        "explanation": "The product appears non-classical or technically modified, so patentability, drug approval, and biodiversity access questions should be checked together.",
        "relevant_regimes": ["Patents", "DrugRegulation", "ABS"],
    },
    "Patent-or-Proprietary Medicine": {
        "classification_result": "Patent-or-Proprietary Medicine",
        "explanation": "The product appears proprietary but not clearly novel enough from this short flow, so patent, trademark, and drug-labeling issues should be reviewed carefully.",
        "relevant_regimes": ["Patents", "Trademarks", "DrugRegulation"],
    },
}

TKDL_DEMO_RECORDS = [
    {
        "formulation_keyword": "turmeric",
        "classification": "Classical",
        "matched_note": "Illustrative TKDL-style prior-art risk: turmeric medicinal uses are a well-known traditional-knowledge example.",
        "is_illustrative": True,
    },
    {
        "formulation_keyword": "ashwagandha",
        "classification": "Classical",
        "matched_note": "Illustrative TKDL-style prior-art risk: classical Ayurveda formulations may face a Section 3(p) traditional-knowledge issue.",
        "is_illustrative": True,
    },
    {
        "formulation_keyword": "neem",
        "classification": "Classical",
        "matched_note": "Illustrative TKDL-style prior-art risk: known plant uses can be relevant prior art for patent examination.",
        "is_illustrative": True,
    },
]


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "ip-sakti-rag"}


@app.post("/api/v1/session")
def create_session():
    session_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    SESSIONS[session_id] = {
        "session_id": session_id,
        "created_at": created_at,
        "jurisdiction": "India",
        "classification_result": None,
    }
    return {"session_id": session_id, "created_at": created_at}


@app.patch("/api/v1/session/{session_id}/jurisdiction")
def set_jurisdiction(session_id: str, request: JurisdictionRequest):
    session = require_session(session_id)
    try:
        jurisdiction = normalize_jurisdiction(request.jurisdiction)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    session["jurisdiction"] = jurisdiction
    return {"session_id": session_id, "jurisdiction": jurisdiction}


@app.post("/api/v1/classification/start")
def start_classification(request: SessionRequest):
    require_session(request.session_id)
    CLASSIFICATION_STATE[request.session_id] = {"current_question_id": "q1", "answers": {}}
    return QUESTIONS["q1"]


@app.post("/api/v1/classification/answer")
def answer_classification(request: ClassificationAnswerRequest):
    session = require_session(request.session_id)
    state = CLASSIFICATION_STATE.setdefault(
        request.session_id,
        {"current_question_id": "q1", "answers": {}},
    )
    if request.question_id not in QUESTIONS:
        raise HTTPException(status_code=400, detail="unknown question_id")

    normalized_answer = request.answer.strip().lower()
    state["answers"][request.question_id] = request.answer

    result = next_classification_step(request.question_id, normalized_answer)
    if "classification_result" in result:
        session["classification_result"] = result["classification_result"]
        state["final"] = result
    return result


@app.post("/api/v1/query")
def query_endpoint(request: QueryRequest):
    session = None
    if request.session_id:
        session = require_session(request.session_id)

    jurisdiction = request.jurisdiction or (session or {}).get("jurisdiction") or "India"
    try:
        jurisdiction = normalize_jurisdiction(jurisdiction)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    classification_context = request.classification_context or (session or {}).get(
        "classification_result"
    )
    payload = full_pipeline(
        request.query_text,
        jurisdiction=jurisdiction,
        classification_context=classification_context,
    )
    payload["query_id"] = str(uuid4())
    return payload


@app.get("/api/v1/tkdl/lookup")
def tkdl_lookup(keyword: str = Query(..., min_length=1)):
    raise HTTPException(status_code=501, detail="TKDL lookup connector is not configured.")


@app.get("/api/v1/abs/checklist")
def abs_checklist(classification: str = Query(..., min_length=1)):
    raise HTTPException(status_code=501, detail="ABS checklist rules are not configured in the RAG service.")


@app.post("/api/v1/escalate")
def escalate(request: EscalationRequest):
    require_session(request.session_id)
    escalation_id = str(uuid4())
    ESCALATIONS[escalation_id] = {
        "escalation_id": escalation_id,
        "session_id": request.session_id,
        "query_id": request.query_id,
        "user_contact_optional": request.user_contact_optional,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"status": "logged", "escalation_id": escalation_id}


@app.post("/api/v1/translate")
def translate(request: TranslateRequest):
    raise HTTPException(status_code=501, detail="Translation provider integration is not configured.")


def next_classification_step(question_id: str, answer: str) -> dict:
    yes = answer.startswith("y")
    no = answer.startswith("n")

    if question_id == "q1" and yes:
        return FINAL_CLASSIFICATIONS["Classical/Generic Medicine"]
    if question_id == "q1":
        return next_question("q2")

    if question_id == "q2" and yes:
        return FINAL_CLASSIFICATIONS["Ayurveda-Aahar/Nutraceutical"]
    if question_id == "q2":
        return next_question("q3")

    if question_id == "q3" and yes:
        return FINAL_CLASSIFICATIONS["Phytopharmaceutical"]
    if question_id == "q3":
        return next_question("q4")

    if question_id == "q4" and yes:
        return FINAL_CLASSIFICATIONS["New/Non-classical Drug"]
    if question_id == "q4" and no:
        return FINAL_CLASSIFICATIONS["Patent-or-Proprietary Medicine"]
    return FINAL_CLASSIFICATIONS["New/Non-classical Drug"]


def next_question(question_id: str) -> dict:
    question = QUESTIONS[question_id]
    return {
        "next_question_id": question["question_id"],
        "question_text": question["question_text"],
        "options": question["options"],
    }


def require_session(session_id: str) -> dict:
    session = SESSIONS.get(session_id)
    if not session:
        session = {
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "jurisdiction": "India",
            "classification_result": None,
        }
        SESSIONS[session_id] = session
    return session

