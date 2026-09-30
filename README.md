# IP-SAKTI Sahayak

> **Smart India Hackathon 2026 · Problem Statement ID: SIH26045**  
> A multilingual, RAG-based AI assistant for Intellectual Property and regulatory guidance in Ayurveda, across national and international regimes.

**Team:** VedaVerse &nbsp;|&nbsp; **Theme:** MedTech / BioTech / HealthTech &nbsp;|&nbsp; **Category:** Software  
**Ministry:** Ministry of Ayush  
**Core Principles:** *Source-Grounded · Traceable · Safety-First*

---

## What is IP-SAKTI Sahayak?

AYUSH startups, practitioners, and researchers face a frustrating wall: IPR and regulatory requirements are scattered across dozens of laws, treaties, and guidelines — and generic AI chatbots hallucinate non-existent legal sections, which is dangerous in a legal context.

**IP-SAKTI Sahayak** is a domain-specialized, citation-grounded decision support tool that:
- Classifies your Ayurvedic product into one of **6 regulatory categories** before searching
- Isolates **India vs International** legal jurisdictions so rules never cross-contaminate
- Returns answers **only** from its verified 22-source corpus, with verbatim statutory citations
- **Abstains safely** when evidence is insufficient, rather than hallucinating

---

## Repository Structure

```
IP-Sakti/
├── ip-sakti-backend/          # FastAPI API engine (Python)
│   ├── app/                   # Route handlers, services, models, core logic
│   │   ├── api/v1/            # REST endpoints (session, query, classification, abs, tkdl…)
│   │   ├── core/              # Citation, confidence, abstention, jurisdiction modules
│   │   ├── db/                # SQLAlchemy setup & schema init
│   │   ├── models/            # ORM models (session, query_log, escalation, tkdl_demo)
│   │   ├── schemas/           # Pydantic request/response models
│   │   └── services/          # RAG orchestrator, LLM, classification, TKDL, ABS
│   ├── corpus/                # Legal corpus chunks (India + International)
│   ├── postman/               # Postman collection for API testing
│   ├── tests/                 # Backend test suite
│   ├── Dockerfile             # Container image
│   ├── docker-compose.yml     # Compose stack
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment variable template
│   └── README.md              # Backend-specific docs
│
├── ip-sakti-RAG/              # Hybrid RAG pipeline (Python)
│   ├── app/                   # Corpus builder, ingestion, retrieval, knowledge graph
│   ├── data/                  # corpus.json, graph artifacts
│   ├── eval/                  # Evaluation scripts & labeled query benchmarks
│   ├── tests/                 # RAG-specific tests
│   └── README_RAG.md          # RAG pipeline docs
│
├── ip-sakti-frontend/         # React + Vite web application
│   ├── src/
│   │   ├── components/        # Reusable UI pieces (citation drawer, confidence badge…)
│   │   ├── pages/             # Route-level screens
│   │   ├── services/          # API client helpers
│   │   ├── context/           # App-level state (jurisdiction, session)
│   │   ├── hooks/             # Custom React hooks
│   │   └── utils/             # Constants and helpers
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── Documentation/             # Full project documentation
│   ├── 01_PRD.md
│   ├── 02_Technical_Architecture.md
│   ├── 03_Functional_Requirements_User_Stories.md
│   ├── 04_Data_Model_Corpus_Design.md
│   ├── 05_API_Specification.md
│   ├── 06_Project_Plan_Roadmap_Test_Plan.md
│   └── 07_SRS.md
│
├── Corpus Research/           # Raw legal research notes and downloaded PDFs
├── images/                    # UI mockups and reference images
└── ip_sakti.db                # SQLite database (session/audit logs)
```

---

## How It Works (6-Step Pipeline)

```
01 JURISDICTION  →  User picks: India  or  International
        ↓
02 CLASSIFY      →  Product mapped to 1 of 6 regulatory categories
        ↓
03 QUESTION      →  User asks an IPR / regulatory query
        ↓
04 RETRIEVE      →  BM25 (exact statutory terms) + Pinecone (semantic) → RRF fusion
        ↓
05 VERIFY        →  LLM generates answer strictly from retrieved chunks + NLI check
        ↓
06 ESCALATE      →  Low confidence? System abstains and offers human facilitator
```

**Why pre-retrieval classification matters:** If a user asks about a classical formulation found in Charaka Samhita, the system must invoke Section 3(p) of the Patents Act — not synthetic-chemical patent rules. Classification before retrieval prevents legal cross-contamination at the source.

### 6 Supported Product Categories

| # | Category | Key Legal Consideration |
|---|---|---|
| 1 | Classical / Generic | Section 3(p) patent bar, TKDL prior art |
| 2 | Proprietary / Patent | Novelty, inventive step, safety evidence |
| 3 | New / Non-classical Drug | AYUSH Rule 158B, clinical data requirements |
| 4 | Phytopharmaceutical | Drugs & Cosmetics Rules, Chapter IVA |
| 5 | Ayurveda-Aahar / Nutraceutical | FSSAI Ayurveda Aahara Regulations 2022 |
| 6 | Ayurvedic Cosmetics | Schedule S, topical safety standards |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, React Router |
| **Backend API** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2 |
| **ORM / Database** | SQLAlchemy 2.x, aiosqlite / SQLite (dev), Supabase PostgreSQL (prod) |
| **RAG Retrieval** | BM25 (rank-bm25), Pinecone (dense embeddings), Reciprocal Rank Fusion |
| **LLM** | Google Gemini API (configurable: mock / openai / local) |
| **Testing** | Pytest, pytest-asyncio, Postman collections |
| **Containerization** | Docker, docker-compose |

---

## Legal Corpus (22 Sources · 91 Chunks)

### India
- The Patents Act, 1970 (incl. §3(p), §3(e), §3(d), §3(j))
- Biological Diversity Act, 2002 & Biological Diversity Rules, 2024
- Geographical Indications of Goods Act, 1999
- Drugs & Cosmetics Act, 1940 & Rules, 1945 (incl. AYUSH Rule 158B)
- Food Safety & Standards (Ayurveda Aahara) Regulations, 2022
- Traditional Knowledge Digital Library (TKDL) — prior-art guidelines
- Medicinal & Toilet Preparations framework

### International
- TRIPS Agreement (WTO)
- Convention on Biological Diversity (CBD)
- Nagoya Protocol on Access & Benefit-Sharing (ABS)
- WIPO Treaty on IP, Genetic Resources & Associated Traditional Knowledge (2024)
- Patent Cooperation Treaty (PCT)
- Budapest Treaty

Every chunk carries `jurisdiction`, `act_title`, `section_number`, `official_url`, and `effective_date` metadata — making every answer fully traceable.

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- (Optional) Docker

---

### 1. Backend (FastAPI)

```bash
cd ip-sakti-backend

# Create virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL, LLM_PROVIDER, and any API keys

# Run the server
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: `http://localhost:8000/docs`

**Environment variables (`.env.example`):**

```env
PROJECT_NAME="IP-SAKTI Sahayak Backend"
API_V1_PREFIX="/api/v1"
ENV="development"
DATABASE_URL=""

# Supabase PostgreSQL (production)
SUPABASE_URL="https://YOUR_PROJECT.supabase.co"
SUPABASE_DB_HOST="..."
SUPABASE_DB_USER="postgres.YOUR_PROJECT_REF"
SUPABASE_DB_PASSWORD="..."

# LLM
LLM_PROVIDER="mock"   # mock | openai | bhashini | local
OPENAI_API_KEY="your-api-key-here"
OPENAI_MODEL="gpt-4o-mini"
```

**Or run with Docker:**

```bash
cd ip-sakti-backend
docker-compose up --build
```

---

### 2. Frontend (React + Vite)

```bash
cd ip-sakti-frontend
npm install
npm run dev
```

App runs at: `http://localhost:5173`

Other scripts:
```bash
npm run build    # production build
npm run preview  # preview production build locally
```

---

### 3. RAG Pipeline

```bash
cd ip-sakti-RAG

python -m venv venv
.\venv\Scripts\activate   # or: source venv/bin/activate
pip install -r requirements.txt   # if requirements exist, else pip install rank-bm25 google-generativeai

# Build corpus from source documents
python -m app.corpus_builder

# Validate without rebuilding
python -m app.corpus_manifest --validate

# Build BM25 index only (offline/demo mode)
python -m app.ingestion --dense off

# Build BM25 + dense embeddings (needs GEMINI_API_KEY)
python -m app.ingestion --dense on

# Export provenance graph
python -m app.knowledge_graph

# Run evaluation benchmark
python eval/run_evaluation.py
```

Outputs:
- `data/corpus/corpus.json` — 91 structured legal chunks
- `data/graph/corpus_graph.json` — 217 nodes, 364 edges
- `data/graph/corpus_graph.sqlite3` — queryable provenance DB

---

## API Endpoints (v1)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/session` | Create a new user session |
| `PATCH` | `/api/v1/session/{id}/jurisdiction` | Switch India / International |
| `POST` | `/api/v1/classification/start` | Start product classification wizard |
| `POST` | `/api/v1/classification/answer` | Submit wizard answer, get next step |
| `POST` | `/api/v1/query` | Submit IPR/regulatory query, get cited answer |
| `GET` | `/api/v1/tkdl/lookup` | TKDL prior-art illustrative lookup |
| `GET` | `/api/v1/abs/checklist` | ABS compliance checklist for classification |
| `POST` | `/api/v1/escalate` | Log escalation request to human facilitator |
| `POST` | `/api/v1/translate` | Demo multilingual translation |
| `GET` | `/api/v1/health` | Health check |

Full spec: [`Documentation/05_API_Specification.md`](./Documentation/05_API_Specification.md)  
Postman collection: [`ip-sakti-backend/postman/`](./ip-sakti-backend/postman/)

---

## Safety & Trust Model

IP-SAKTI Sahayak takes legal accuracy seriously:

- **Zero hallucination tolerance:** The LLM is prompted to cite only chunk IDs present in the retrieved context. No out-of-corpus claims are permitted.
- **Confidence thresholding:** Each response carries a similarity-based confidence score. Below the threshold, the system abstains.
- **Safe abstention:** Out-of-scope queries (e.g., EU medical device CE marking) return a clear notice and escalation prompt — not a fabricated answer.
- **Jurisdiction hard filters:** India-mode queries are physically filtered to Indian statutes only; International-mode to multilateral frameworks only. Cross-leakage is impossible at the retrieval layer.
- **Persistent disclaimers:** Every response includes a legal disclaimer clarifying this is decision support, not legal advice.

---

## Documentation Index

| File | Contents |
|---|---|
| [`Documentation/01_PRD.md`](./Documentation/01_PRD.md) | Product Requirements Document |
| [`Documentation/02_Technical_Architecture.md`](./Documentation/02_Technical_Architecture.md) | System architecture & design decisions |
| [`Documentation/03_Functional_Requirements_User_Stories.md`](./Documentation/03_Functional_Requirements_User_Stories.md) | User stories & functional specs |
| [`Documentation/04_Data_Model_Corpus_Design.md`](./Documentation/04_Data_Model_Corpus_Design.md) | Corpus schema, chunk format & classification taxonomy |
| [`Documentation/05_API_Specification.md`](./Documentation/05_API_Specification.md) | Full REST API contract |
| [`Documentation/06_Project_Plan_Roadmap_Test_Plan.md`](./Documentation/06_Project_Plan_Roadmap_Test_Plan.md) | Roadmap, milestones & test plan |
| [`Documentation/07_SRS.md`](./Documentation/07_SRS.md) | Software Requirements Specification |
| [`ip-sakti-backend/README.md`](./ip-sakti-backend/README.md) | Backend developer guide |
| [`ip-sakti-RAG/README_RAG.md`](./ip-sakti-RAG/README_RAG.md) | RAG pipeline developer guide |

---

## Team VedaVerse

| Role | Contribution |
|---|---|
| RAG & Vector DB Engineer | Hybrid retrieval (BM25 + Pinecone), corpus ingestion, citation grounding, safe abstention |
| Legal Researcher | 22-source corpus, 91 chunks, classification taxonomy, ABS checklist logic |
| Backend Engineer | FastAPI endpoints, classification state machine, session & jurisdiction routing |
| Frontend Engineer | React + Vite SPA, classification wizard, citation drawer, jurisdiction toggle |
| QA Engineer | Benchmark dataset, citation accuracy validation, abstention & regression tests |
| Presentation Lead | SIH pitch deck, user journey design, project documentation |

---

*Built for Smart India Hackathon 2026 by Team VedaVerse.*
