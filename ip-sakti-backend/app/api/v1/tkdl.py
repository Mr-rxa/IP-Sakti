from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies import get_database_session
from app.schemas.tkdl import TKDLLookupResponse
from app.services.tkdl_service import TKDLService

router = APIRouter(prefix="/tkdl", tags=["TKDL / Prior Art"])

@router.get("/lookup", response_model=TKDLLookupResponse, status_code=200)
def lookup_tkdl(
    keyword: str = Query(..., description="Formulation keyword or botanical name"),
    db: Session = Depends(get_database_session)
):
    """
    Static/illustrative demo prior-art lookup against TKDL taxonomy records.
    """
    return TKDLService.lookup(db, keyword)
