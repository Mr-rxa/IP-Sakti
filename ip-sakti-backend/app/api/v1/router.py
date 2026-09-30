from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.session import router as session_router
from app.api.v1.classification import router as classification_router
from app.api.v1.query import router as query_router
from app.api.v1.tkdl import router as tkdl_router
from app.api.v1.abs import router as abs_router
from app.api.v1.escalate import router as escalate_router
from app.api.v1.translate import router as translate_router
from app.api.v1.health import router as health_router
from app.api.v1.paid_sources import router as paid_sources_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(session_router)
api_v1_router.include_router(classification_router)
api_v1_router.include_router(query_router)
api_v1_router.include_router(tkdl_router)
api_v1_router.include_router(abs_router)
api_v1_router.include_router(escalate_router)
api_v1_router.include_router(translate_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(paid_sources_router)


@api_v1_router.get("/corpus/version", tags=["Corpus"])
def get_corpus_version():
    return {
        "corpus_version": "2026.1",
        "latest_amendments_indexed": [
            "Biological Diversity (Amendment) Act 2023 & 2024 Rules",
            "Indian Patents (Amendment) Rules 2024",
            "FSSAI (Ayurveda Aahar) Regulations 2022",
            "WIPO Diplomatic Conference Treaty on Genetic Resources 2024",
            "Drugs and Cosmetics ASU Rules (Rule 158-B Gazette)"
        ],
        "total_documents": 91,
        "indexed_regimes": ["Patents", "ABS", "TKDL", "DrugRegulation", "Food", "Trademarks", "Designs", "GI"]
    }
