from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_database_session
from app.schemas.classification import (
    ClassificationStartRequest,
    ClassificationAnswerRequest,
    ClassificationResponse,
    ClassificationQuestionResponse,
    ClassificationFinalResultResponse
)
from app.services.classification_service import ClassificationService

router = APIRouter(prefix="/classification", tags=["Classification"])

@router.post("/start", response_model=ClassificationQuestionResponse, status_code=200)
def start_classification(
    payload: ClassificationStartRequest,
    db: Session = Depends(get_database_session)
):
    """
    Begin the guided formulation classification flow.
    """
    return ClassificationService.start_flow(db, payload.session_id)

@router.post("/answer", response_model=ClassificationResponse, status_code=200)
def answer_classification(
    payload: ClassificationAnswerRequest,
    db: Session = Depends(get_database_session)
):
    """
    Submit an answer in the classification flow; returns next question or final classification result.
    """
    return ClassificationService.answer_question(
        db=db,
        session_id=payload.session_id,
        question_id=payload.question_id,
        answer=payload.answer
    )
