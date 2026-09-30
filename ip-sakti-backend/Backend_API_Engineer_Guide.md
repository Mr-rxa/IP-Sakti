# Backend API Engineer Guide

## 1. Objective
This guide is for the backend/API engineer working on the Ayurveda IPR assistant for SIH. The backend must support a citation-grounded, multilingual legal assistant that answers questions around Ayurvedic IP, patents, GI, trademarks, biodiversity, and regulatory compliance.

The backend is not just a chatbot API. It is the control layer for:
- user authentication and session management
- formulation classification flow
- jurisdiction switching (India vs international)
- retrieval pipeline coordination
- citation generation and confidence scoring
- audit logs, privacy controls, and escalation to human facilitator

---

## 2. Core Product Requirements to Implement
The backend must align with the problem statement:
- answer Ayurveda-specific IPR questions with source citations
- clearly separate India and international law
- route between IP type and product category logic
- classify products as:
  - classical/generic Ayurveda medicine
  - proprietary/patent medicine
  - new/non-classical drug
  - phytopharmaceutical
  - Ayurveda-Aahar / nutraceutical
  - cosmetic
- support ABS and TKDL/prior-art workflows
- provide “information, not legal advice” disclaimer
- maintain auditability and permissions for paid databases
- support multilingual requests and response handling
- allow safe abstention when the answer is uncertain or out of scope

---

## 3. Recommended Stack
Use a simple, production-friendly backend stack:
- Python + FastAPI
- PostgreSQL for metadata and user/session data
- Redis for caching and rate limiting
- Qdrant / Pinecone / Weaviate for vector storage
- Celery or background job workers for indexing and async processing
- MinIO or object storage for uploaded docs
- OpenTelemetry + structured logging for observability

This is enough for SIH while keeping the stack easy to explain and easy for a non-backend-heavy team to support.

---

## 4. Step-by-Step Implementation Plan

### Step 1: Define the backend architecture
Set up a clean service structure:
- app/
  - api/
  - core/
  - models/
  - schemas/
  - services/
  - db/
  - security/
  - utils/

Main responsibilities:
- API layer: endpoints for chat, classification, search, source retrieval, admin actions
- Service layer: orchestration of retrieval, routing, classification
- DB layer: user metadata, audit logs, document metadata, source registry entries
- Security layer: API keys, auth, PII handling, request validation

### Step 2: Create the core API contracts
Build the primary endpoints.

#### 2.1 Query endpoint
POST /api/v1/query
Request body:
- question
- jurisdiction: india | international
- product_type (optional)
- formulation_classification (optional)
- language (optional)
- user_context (optional)

Response:
- answer
- citations
- confidence
- jurisdiction
- classification_summary
- follow_up_questions (optional)
- disclaimer

#### 2.2 Formulation classification endpoint
POST /api/v1/classify-formulation
Body:
- product_name
- ingredients
- product_category
- use_case
- source_of_knowledge

Response:
- classification
- explanation
- required_ip_checks
- required_regulatory_checks
- relevant_law_sections

#### 2.3 Search endpoint
POST /api/v1/search
Body:
- query
- jurisdiction
- source_type
- filters

Response:
- top_results
- metadata
- document_ids

#### 2.4 Citation/source endpoint
GET /api/v1/source/{source_id}
Purpose: return a full source record and legal basis with source metadata.

#### 2.5 Admin endpoints
- document upload
- corpus version tracking
- manual review queue
- audit log export
- paid database access controls

### Step 3: Design the data model
The backend should maintain a strong metadata layer for every legal document or source.

Core source metadata:
- source_id
- title
- doc_type
- jurisdiction
- country
- legal_framework
- act_or_treaty
- section_or_article
- publication_date
- last_updated
- authority_name
- source_url
- is_official
- is_paid
- access_permission_required
- language
- tags

Core query metadata:
- query_id
- user_id
- session_id
- jurisdiction
- timestamp
- model_version
- retrieval_strategy
- confidence_score
- citation_count
- escalation_flag

### Step 4: Build the legal classification flow
This is a crucial part of the product. The backend should support a decision layer before retrieval and answer generation.

The classification flow should determine:
1. Is the product classical/generic or proprietary/new?
2. Is it a drug, nutraceutical, phytopharmaceutical, or cosmetic?
3. What IP types are relevant?
4. What ABS/TKDL checks are required?
5. Which laws apply for India vs international context?

Backend logic should not decide legal conclusions alone. It should route to the correct legal context and then retrieve the relevant sources.

### Step 5: Implement jurisdiction-aware logic
The most important backend rule: never mix Indian and international law in one answer.

Implementation pattern:
- query.jurisdiction = india | international
- retrieval filters: jurisdiction = same scope
- rendering layer: present India answer separately from international answer
- answer generation prompt: must explicitly state which jurisdiction is being used

This is a non-negotiable product requirement for SIH.

### Step 6: Connect retrieval and answer generation
The backend must orchestrate:
- query classification
- retrieval from vector DB
- metadata filtering
- reranking
- source citation selection
- final answer synthesis

The backend should call the retriever service and then pass the retrieved context to the LLM with explicit citation rules.

### Step 7: Enforce source citation rules
Every answer should include:
- legal authority cited
- relevant act/rule/article
- source title
- confidence score
- whether the source is official or secondary material

A safe backend rule:
- if a fact has no verifiable source, do not answer confidently
- return abstention or ask for clarification

### Step 8: Add safe abstention and escalation logic
The backend should detect:
- out-of-scope question
- missing facts
- uncertain legal interpretation
- conflict between sources

In such cases:
- respond with “information, not legal advice”
- ask a clarifying question
- suggest escalation to a human IP facilitator

### Step 9: Build audit, privacy, and governance controls
This is essential for SIH and for an AI-based legal assistant.

Implement:
- request/response logging without exposing sensitive personal data
- consent tracking for paid-source access
- audit logs for all admin decisions
- model and retrieval version tracking
- rate limiting
- secure API key management
- role-based access for admin and facilitator users

### Step 10: Make it deployable
Prepare a simple deployment flow:
- FastAPI app containerized with Docker
- environment setup with .env
- CI/CD pipeline for staging and production
- health checks
- monitoring dashboards
- log retention policy

---

## 5. Minimum API Endpoints Checklist
The team should implement at least these:
- POST /api/v1/query
- POST /api/v1/classify-formulation
- POST /api/v1/search
- GET /api/v1/source/{id}
- GET /api/v1/health
- GET /api/v1/corpus/version
- POST /api/v1/escalate
- GET /api/v1/audit/logs

---

## 6. Backend Responsibilities by Phase

### Phase 1: MVP
- legal source ingestion metadata API
- query orchestration API
- classification endpoint
- citation retrieval
- jurisdiction separation
- basic audit logging

### Phase 2: Advanced version
- knowledge graph service integration
- multi-step agent workflow
- enhanced reranking
- multilingual routing
- paid-source connector governance

### Phase 3: Production readiness
- access control
- user consent management
- secure logging
- monitoring and fallback behavior
- human escalation workflow

---

## 7. Suggested Backend Error Handling Rules
- if no trusted source found: return safe answer with low confidence
- if multiple jurisdictions are mixed: reject the query and ask for a jurisdiction choice
- if legal answer requires specialist review: escalate
- if source is outdated or version conflict: flag as stale and avoid strong conclusion

---

## 8. Things to Avoid
- mixing India and international legal rules in the same answer
- returning legal advice without source citation
- using a vector DB without metadata filtering
- storing raw sensitive user inputs without retention rules
- allowing paid-source access without explicit approval
- generating answers without stating the uncertainty level

---

## 9. Simple Acceptance Criteria for the Backend
The backend is considered working if:
- every answer is traceable to a source
- jurisdiction is visible and separate
- formulation classification is supported
- legal sources are versioned and metadata-rich
- safety disclaimers appear consistently
- query results can be audited

---

## 10. Final Note for the Engineer
The backend engineer is the “control center” for this project. If retrieval and RAG are the brain, the backend is the safety layer, the routing engine, and the source-traceability system. In this SIH challenge, clarity, separation of legal jurisdictions, and citation integrity matter more than fancy features.
