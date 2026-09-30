# IP-SAKTI Sahayak — Backend API Engine
## Multilingual RAG Assistant for Ayurveda IPR & Regulatory Guidance
**Problem Statement:** SIH26045 | **Ministry:** Ministry of Ayush

---

## 1. System Overview
IP-SAKTI Sahayak is a domain-specialized Retrieval-Augmented Generation (RAG) backend engineered to provide citation-grounded, jurisdiction-isolated legal and regulatory guidance for Ayurvedic innovators, practitioners, and MSMEs.

### Key Architectural Pillars
- **Strict Jurisdiction Isolation:** India and International legal frameworks are kept strictly partitioned at the corpus retrieval level (never blended in a single answer).
- **Formulation Classification State Machine:** Classifies Ayurvedic formulations into 6 regulatory categories (Classical, Proprietary, New Drug, Phytopharmaceutical, Ayurveda-Aahar, Cosmetic).
- **Mandatory Statutory Grounding:** Every factual answer is linked to authoritative statutes (e.g., Indian Patents Act 1970 §3(p)/§3(e), Biological Diversity Act 2002/2023 §6/§7, FSSAI Ayurveda Aahar Regs 2022, WIPO 2024 Treaty).
- **Confidence Scoring & Safe Abstention:** Automatically computes retrieval similarity thresholds; gracefully abstains and offers facilitator escalation on out-of-scope or low-confidence queries.
- **Defensive Prior-Art Pointers:** Illustrative TKDL reference search indicating prior art status.
- **ABS Compliance Engine:** Rule-based Access and Benefit-Sharing checklist generator mapped to biological resource usage.

---

## 2. Project Directory Structure
```
ip-sakti-backend/
├── app/
│   ├── main.py                     # FastAPI application setup, lifecycle & middleware
│   ├── config.py                   # Pydantic Settings & environment variables
│   ├── dependencies.py             # Shared dependency injection helpers
│   ├── api/
│   │   └── v1/
│   │       ├── router.py           # V1 route aggregator
│   │       ├── session.py          # POST /session, PATCH /session/{id}/jurisdiction
│   │       ├── classification.py   # POST /classification/start, POST /classification/answer
│   │       ├── query.py            # POST /query (Main cited RAG endpoint)
│   │       ├── tkdl.py             # GET /tkdl/lookup (Illustrative TKDL prior art)
│   │       ├── abs.py              # GET /abs/checklist (Biological diversity checklist)
│   │       ├── escalate.py         # POST /escalate (Facilitator escalation logging)
│   │       ├── translate.py        # POST /translate (Demo multilingual translation)
│   │       └── health.py           # GET /health, GET /ready, GET /corpus/version
│   ├── core/
│   │   ├── citation.py             # Source citation extractors
│   │   ├── confidence.py           # Confidence scoring & abstention thresholds
│   │   ├── disclaimer.py           # Persistent legal disclaimers
│   │   ├── exceptions.py           # Structured error classes
│   │   └── jurisdiction.py         # Jurisdiction isolation filters
│   ├── db/
│   │   ├── database.py             # SQLAlchemy engine & session factory
│   │   └── init_db.py              # Schema creation & TKDL seed loader
│   ├── models/
│   │   ├── session.py              # User session ORM
│   │   ├── query_log.py            # Query, confidence & abstention telemetry
│   │   ├── tkdl_demo.py            # Illustrative TKDL records ORM
│   │   └── escalation.py           # Human facilitator escalation log ORM
│   ├── schemas/                    # Pydantic models for request/response validation
│   ├── services/
│   │   ├── session_service.py
│   │   ├── classification_service.py
│   │   ├── retrieval_service.py
│   │   ├── llm_service.py
│   │   ├── rag_orchestrator.py
│   │   ├── tkdl_service.py
│   │   ├── abs_service.py
│   │   ├── escalation_service.py
│   │   └── translate_service.py
│   ├── security/
│   │   ├── rate_limit.py           # In-memory IP rate limiter
│   │   └── input_validation.py     # Input sanitization
│   └── utils/
│       ├── logging.py              # Structured logging
│       └── corpus_loader.py        # Legal corpus metadata chunking utility
├── corpus/
│   ├── corpus_changelog.md         # Legal amendment version provenance
│   ├── india/                      # Indian statutory reference documents
│   ├── international/              # International treaty reference documents
│   └── seed_data/
│       ├── tkdl_demo_records.json  # Seed illustrative TKDL records
│       ├── abs_rules.json          # Seed ABS compliance checklists
│       └── sample_corpus_chunks.json # Curated section-level corpus chunks
├── postman/                        # Postman Collection v2.1.0 & Local Environment
│   ├── IP_SAKTI_Sahayak.postman_collection.json
│   ├── IP_SAKTI_Local.postman_environment.json
│   └── README.md
├── tests/                          # Pytest integration suite (100% endpoint coverage)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 3. API Endpoints Specification Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/session` | Creates a new user session |
| `PATCH` | `/api/v1/session/{id}/jurisdiction` | Updates session jurisdiction (`India` \| `International`) |
| `POST` | `/api/v1/classification/start` | Initiates formulation classification guided Q&A |
| `POST` | `/api/v1/classification/answer` | Submits classification answers; transitions state machine |
| `POST` | `/api/v1/query` | Grounded RAG Q&A with citations, confidence & abstention |
| `GET` | `/api/v1/tkdl/lookup?keyword=...` | Illustrative prior art / TKDL lookup |
| `GET` | `/api/v1/abs/checklist?classification=...` | Rule-based ABS compliance checklist |
| `POST` | `/api/v1/escalate` | Logs query escalation to human IP facilitator |
| `GET` | `/api/v1/health` | Liveness and corpus-version health response |
| `GET` | `/api/v1/ready` | Safe readiness diagnostics for database, RAG service, and model/vector configuration |

`/api/v1/ready` always returns HTTP 200 and reports `ready` or `degraded` per dependency. It exposes configuration presence and reachability only; API keys, passwords, URLs containing credentials, and tokens are never returned. The RAG service and optional providers may be unavailable in the local offline mode without preventing the backend from starting.
| `POST` | `/api/v1/translate` | Translation through an explicitly configured provider |
| `POST` | `/api/v1/paid-sources/consents` | Authenticated consent record for a future paid-source connector |
| `GET` | `/api/v1/health` | Liveness & readiness check |
| `GET` | `/api/v1/corpus/version` | Legal corpus versioning and amendment index |

---

## 4. Setup & Running Locally

### 4.1 Prerequisites
- Python 3.10+
- virtualenv

### 4.2 Installation
```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment configuration
cp .env.example .env

# 4. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4.3 Running Tests
```bash
# Run Pytest suite
pytest tests/ -v

# Run Postman Collection via Newman CLI
newman run postman/IP_SAKTI_Sahayak.postman_collection.json -e postman/IP_SAKTI_Local.postman_environment.json
```

### 4.4 Security and provider configuration
- Requests are limited to `MAX_REQUEST_BODY_BYTES` (default `262144`) and `RATE_LIMIT_REQUESTS` per `RATE_LIMIT_WINDOW_SECONDS` per client IP (defaults `100` per `60` seconds).
- Query and translation text fields are bounded by request schemas. Oversized requests return `413`; rate-limited requests return `429`.
- Set `TRANSLATION_PROVIDER=http` and `TRANSLATION_PROVIDER_URL` to use an explicitly configured HTTP provider. The default `TRANSLATION_PROVIDER=none` returns `501` without making a network call. `TRANSLATION_PROVIDER_API_KEY` is sent only to that provider and is redacted from backend logs.
- Paid-source access has no connector in this release. An authenticated client must create an active consent record before a future connector may call `PaidSourceService.require_consent`; absent or expired consent is denied.

### 4.5 Running with Docker
```bash
docker compose up --build
```

### 4.6 Postman API Testing
Import `postman/IP_SAKTI_Sahayak.postman_collection.json` and `postman/IP_SAKTI_Local.postman_environment.json` into Postman to test all 11 endpoints organized into 8 modular feature folders.

Interactive Swagger API documentation is also available at: `http://localhost:8000/docs`
