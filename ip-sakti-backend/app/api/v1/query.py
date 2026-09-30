from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_database_session, get_optional_current_user
from app.models.user import UserModel
from app.schemas.query import QueryRequest, QueryResponse
from app.services.rag_orchestrator import rag_orchestrator
from app.security.input_validation import sanitize_text_input

router = APIRouter(tags=["Query & RAG"])

@router.post("/query", response_model=QueryResponse, status_code=200)
def submit_query(
    payload: QueryRequest,
    db: Session = Depends(get_database_session),
    current_user: UserModel = Depends(get_optional_current_user),
):
    """
    Main Q&A endpoint — answers natural language questions with source citations,
    grounded strictly in the curated legal corpus.
    """
    payload.query_text = sanitize_text_input(payload.query_text)
    return rag_orchestrator.process_query(
        db=db,
        request=payload,
        user_id=current_user.id if current_user else None,
    )
