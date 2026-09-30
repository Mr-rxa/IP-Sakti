import uuid
import sys
import json
import os
import subprocess
from pathlib import Path
import httpx
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List

from app.config import settings
from app.schemas.query import QueryRequest, QueryResponse, Citation
from app.models.query_log import QueryLogModel
from app.models.session import SessionModel
from app.core.disclaimer import DISCLAIMER_TEXT
from app.core.jurisdiction import JurisdictionEnum
from app.core.citation import canonical_section, canonical_source_title
from app.utils.logging import logger

# Add ip-sakti-RAG to sys.path for direct pipeline execution fallback
_rag_dir = Path(__file__).resolve().parent.parent.parent.parent / "ip-sakti-RAG"
if _rag_dir.exists() and str(_rag_dir) not in sys.path:
    sys.path.insert(0, str(_rag_dir))

class RAGOrchestrator:
    @staticmethod
    def _is_supported_query(query_text: str) -> bool:
        terms = (
            "ayurveda", "ayurvedic", "ipr", "patent", "copyright", "trademark",
            "trade mark", "geographical indication", "gi tag", "design right",
            "plant variety", "biodiversity", "biological resource", "benefit sharing",
            "traditional knowledge", "tkdl", "drug regulation", "phytopharmaceutical",
            "fssai", "ayush", "trips", "wipo", "nagoya", "budapest treaty",
            "madrid system", "hague system", "pct", "plant", "plants", "herb", "herbs",
            "herbal", "botanical", "medicine", "drug", "formulation", "cosmetic",
            "food", "aahar", "nutraceutical", "license", "licensing", "claim", "claims",
            "species", "extract", "extracts", "curcumin", "ashwagandha", "neem",
            "turmeric", "tulsi", "brahmi", "triphala", "form 25", "form 32", "form iii",
            "form 1", "nba", "sbb", "bmc", "cdsco", "ayush ministry"
        )
        return any(term in query_text.lower() for term in terms)

    @classmethod
    def _call_rag_service(cls, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to call the RAG microservice over HTTP."""
        if not settings.RAG_SERVICE_URL:
            return None
        try:
            url = f"{settings.RAG_SERVICE_URL.rstrip('/')}/query"
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    return res.json()
        except Exception as e:
            logger.info(f"RAG microservice at {settings.RAG_SERVICE_URL} not reachable ({e}). Using integrated in-process RAG pipeline.")
        return None

    @classmethod
    def _call_direct_pipeline(cls, query_text: str, jurisdiction: str, classification_context: Optional[str]) -> Dict[str, Any]:
        """Call the RAG pipeline in an isolated process to avoid package collisions."""
        try:
            rag_python = _rag_dir / "venv" / "Scripts" / "python.exe"
            if not rag_python.exists():
                rag_python = _rag_dir / "venv" / "bin" / "python"
            if not rag_python.exists():
                rag_python = Path(sys.executable)

            runner = (
                "import json, sys; "
                "from app.orchestrator import full_pipeline; "
                "print(json.dumps(full_pipeline(" 
                "query=sys.argv[1], jurisdiction=sys.argv[2], "
                "classification_context=json.loads(sys.argv[3])" 
                ")))"
            )
            completed = subprocess.run(
                [
                    str(rag_python),
                    "-c",
                    runner,
                    query_text,
                    jurisdiction,
                    json.dumps(classification_context),
                ],
                cwd=str(_rag_dir),
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                timeout=60,
                check=True,
            )
            output_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
            if not output_lines:
                raise RuntimeError("RAG subprocess returned no output")
            return json.loads(output_lines[-1])
        except Exception as e:
            logger.error(f"In-process RAG pipeline error: {e}", exc_info=True)
            return {
                "answer_text": "The RAG service is unavailable, so I cannot answer from the approved corpus right now.",
                "citations": [],
                "confidence_score": 0.0,
                "confidence_label": "Low",
                "abstained": True,
                "escalation_suggested": True,
                "retrieved_chunk_ids": [],
                "disclaimer": DISCLAIMER_TEXT,
            }

    def process_query(self, db: Session, request: QueryRequest, user_id: Optional[str] = None) -> QueryResponse:
        query_id = str(uuid.uuid4())
        jurisdiction_val = request.jurisdiction.value if isinstance(request.jurisdiction, JurisdictionEnum) else (request.jurisdiction or "India")
        session_id = request.session_id or f"sess_{uuid.uuid4().hex[:12]}"

        if not self._is_supported_query(request.query_text):
            return QueryResponse(
                query_id=query_id,
                answer_text="I can answer only Ayurveda IPR and regulatory questions covered by the approved corpus.",
                citations=[],
                confidence_score=0.0,
                confidence_label="Low",
                abstained=True,
                escalation_suggested=True,
                disclaimer=DISCLAIMER_TEXT,
            )

        # Ensure session exists in DB
        db_session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not db_session:
            db_session = SessionModel(
                session_id=session_id,
                user_id=user_id,
                jurisdiction_selected=jurisdiction_val,
                classification_result=request.classification_context
            )
            db.add(db_session)
            db.commit()
        elif user_id and not db_session.user_id:
            db_session.user_id = user_id
            db.commit()

        # 1. Try microservice HTTP call first, fall back to in-process RAG
        rag_payload = {
            "session_id": session_id,
            "query_text": request.query_text,
            "jurisdiction": jurisdiction_val,
            "classification_context": request.classification_context
        }

        rag_result = self._call_rag_service(rag_payload)
        if not rag_result:
            rag_result = self._call_direct_pipeline(
                query_text=request.query_text,
                jurisdiction=jurisdiction_val,
                classification_context=request.classification_context
            )

        # 2. Extract and format citations
        raw_citations = rag_result.get("citations", [])
        citations: List[Citation] = []
        for c in raw_citations:
            if isinstance(c, dict):
                citations.append(Citation(
                    source_title=canonical_source_title(c.get("source_title", "Statutory Source")),
                    section_or_article=canonical_section(c.get("section_or_article", "")),
                    jurisdiction=c.get("jurisdiction", jurisdiction_val),
                    regime=c.get("regime"),
                    chunk_id=c.get("chunk_id"),
                    source_url=c.get("source_url", "")
                ))
            elif isinstance(c, str):
                citations.append(Citation(
                    source_title=c,
                    section_or_article="",
                    jurisdiction=jurisdiction_val,
                    source_url=""
                ))

        confidence_score = float(rag_result.get("confidence_score", 0.85))
        confidence_label = rag_result.get("confidence_label", "High")
        abstained = bool(rag_result.get("abstained", False))
        escalation_suggested = bool(rag_result.get("escalation_suggested", False))
        answer_text = rag_result.get("answer_text", "")
        retrieved_chunk_ids = rag_result.get("retrieved_chunk_ids", [])

        # 3. Log query in database
        try:
            log_entry = QueryLogModel(
                query_id=query_id,
                session_id=session_id,
                user_id=user_id,
                query_text=request.query_text,
                retrieved_chunk_ids=retrieved_chunk_ids,
                confidence_score=round(confidence_score, 2),
                abstained=abstained,
                answer_text=answer_text
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Could not persist query log entry: {e}")

        return QueryResponse(
            query_id=query_id,
            answer_text=answer_text,
            citations=citations,
            confidence_score=round(confidence_score, 2),
            confidence_label=confidence_label,
            abstained=abstained,
            escalation_suggested=escalation_suggested,
            disclaimer=rag_result.get("disclaimer") or DISCLAIMER_TEXT
        )

rag_orchestrator = RAGOrchestrator()
