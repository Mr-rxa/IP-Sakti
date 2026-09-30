from fastapi import APIRouter, HTTPException, Query
from app.schemas.abs import ABSChecklistResponse
from app.services.abs_service import ABSService

router = APIRouter(prefix="/abs", tags=["ABS / Biodiversity"])

@router.get("/checklist", response_model=ABSChecklistResponse, status_code=200)
def get_abs_checklist(
    classification: str = Query(..., description="Formulation category (e.g. Classical, New Drug, etc.)")
):
    """
    Rule-based ABS compliance checklist tied to formulation classification.
    """
    try:
        return ABSService.get_checklist(classification)
    except ValueError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
