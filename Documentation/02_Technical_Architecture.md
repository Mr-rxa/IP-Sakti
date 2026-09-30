# Technical Architecture Document
## IP-SAKTI Sahayak (SIH26045)

---

## 1. High-Level Architecture (Stage 1 MVP)

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/Streamlit)                │
│  - Chat UI            - Jurisdiction Toggle (India/Intl)          │
│  - Classification Q&A - Disclaimer banner (persistent)            │
│  - Citation display   - Confidence badge - Escalation button      │
└───────────────────────────────┬─────────────────────────────────┘
                                 │ REST / WebSocket
┌───────────────────────────────▼─────────────────────────────────┐
│                        BACKEND API (FastAPI)                      │
│  ┌───────────────┐  ┌──────────────────┐  ┌───────────────────┐ │
│  │ Classification │  │  Query Router     │  │  ABS Checklist    │ │
│  │ Engine         │  │  (jurisdiction +  │  │  Helper (rule-    │ │
│  │ (decision tree │  │  IP-type routing) │  │  based)           │ │
│  │ / prompt-based)│  │                   │  │                   │ │
│  └───────────────┘  └─────────┬─────────┘  └───────────────────┘ │
│                                │                                   │
│                    ┌───────────▼───────────┐                      │
│                    │   RAG Orchestrator     │                      │
│                    │  (LangChain/LlamaIndex)│                      │
│                    └───────────┬───────────┘                      │
└────────────────────────────────┼──────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
┌───────────────┐      ┌──────────────────┐      ┌───────────────────┐
│  Vector DB      │      │   LLM API         │      │  Static TKDL      │
│  (Chroma/FAISS) │      │  (OpenAI/Claude/  │      │  Prior-Art Demo    │
│  - India corpus │      │  open-weight)     │      │  Dataset (JSON)    │
│  - Intl corpus  │      └──────────────────┘      └───────────────────┘
│  (metadata-      │
│  filtered)       │
└───────────────┘
        │
┌───────▼───────────────────────────────────────────────────────────┐
│                     CORPUS (curated, version-tracked)               │
│  Statutes | Rules | Treaties | Pharmacopoeial Standards | Registry  │
│  Records (metadata: source, section, jurisdiction, effective date)  │
└───────────────────────────────────────────────────────────────────┘
```

## 2. Component Breakdown

### 2.1 Frontend
- **Stack:** React (or Streamlit for faster hackathon build)
- **Responsibilities:** chat interface, jurisdiction toggle state, classification Q&A flow, citation rendering, persistent disclaimer, confidence badge, escalation CTA.

### 2.2 Backend API
- **Stack:** Python, FastAPI
- **Modules:**
  - `classification_engine`: short guided Q&A → returns formulation category
  - `query_router`: determines jurisdiction filter + relevant IP-type(s) before retrieval
  - `rag_orchestrator`: embeds query, retrieves top-k chunks (filtered by jurisdiction), constructs grounded prompt, calls LLM
  - `abs_helper`: rule-based checklist output (not full reasoning agent in MVP)
  - `tkdl_pointer`: looks up static demo dataset for prior-art examples

### 2.3 Vector Store
- **Stack:** Chroma or FAISS (local, no infra overhead for hackathon)
- **Metadata fields per chunk:** `source_title`, `section_or_article`, `jurisdiction` (India/International), `regime` (patents/GI/trademarks/ABS/drug-regulatory/etc.), `effective_date`, `doc_version`

### 2.4 LLM Layer
- Any API-based model (for speed) or an open-weight model (for the "sovereign/offline" angle if the team wants to differentiate)
- Prompt template enforces: (a) answer only from retrieved context, (b) always cite section/article, (c) abstain if retrieval confidence is low

### 2.5 Corpus & Data Pipeline
- Source documents chunked at section/article level (not arbitrary token windows) to preserve legal citation granularity
- Version-tracked (simple `doc_version` + `last_updated` metadata field is sufficient for MVP)

## 3. Data Flow (Single Query)
1. User selects jurisdiction (India / International) and optionally completes classification Q&A.
2. Query + jurisdiction + classification context sent to backend.
3. `query_router` builds a metadata filter (jurisdiction, relevant regime).
4. `rag_orchestrator` retrieves top-k chunks matching filter.
5. Retrieval confidence score computed (e.g., top similarity score threshold).
6. If confidence low → return abstention message + escalation CTA.
7. If confidence sufficient → LLM generates answer strictly grounded in retrieved chunks, with inline citations.
8. Response + citations + confidence badge returned to frontend.

## 4. Security & Privacy (documented for MVP, not fully implemented)
- No PII persisted beyond session state.
- Disclaimer shown before every session.
- Roadmap note: full DPDP-aligned logging/audit trail is a Stage 4 item.

## 5. Deployment (Hackathon Demo)
- Single-container or local deployment (Docker optional) — cloud deployment (Render/Railway/HuggingFace Spaces) if internet demo is needed; otherwise local demo is acceptable.

## 6. Stage 2+ Architecture Additions (roadmap only, not built for MVP)
- Knowledge graph layer (Neo4j or similar) linking IP regimes ↔ formulation types ↔ statutes for multi-hop reasoning
- Agentic orchestration (multi-tool agent: registry lookup, ABS calculator, citation validator)
- Bhashini API integration for full multilingual + voice
- Live TKDL and paid-source connectors with logged consent
- DPDP-compliant audit logging, encryption at rest, access controls
