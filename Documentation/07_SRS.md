# Software Requirements Specification (SRS)
## IP-SAKTI Sahayak — Multilingual RAG Assistant for Ayurveda IPR & Regulatory Guidance
**PS Number:** SIH26045 | **Ministry:** Ministry of Ayush
**Document version:** 1.0 | **Format reference:** IEEE 830

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for IP-SAKTI Sahayak, a retrieval-augmented-generation (RAG) assistant that provides source-cited, jurisdiction-aware IPR and regulatory guidance for the Ayurveda ecosystem. It is intended for the development team, evaluators/judges, and any future contributor extending the system beyond the hackathon MVP.

### 1.2 Scope
The software will:
- Classify an Ayurvedic formulation into one of six regulatory categories via guided Q&A.
- Answer natural-language IPR/regulatory questions, grounded strictly in a curated corpus of statutes, rules, and treaties.
- Keep India and International law answers visibly separate via a jurisdiction toggle.
- Cite the specific source (statute/section/treaty article) for every substantive claim.
- Abstain safely when confidence is low or the query is out of scope, and offer escalation to a human IP facilitator.
- Provide a demo-level multilingual experience.

The software will **not** (in this MVP): provide legal advice, offer legally binding determinations, connect live to paid/proprietary databases, or perform live registry filings.

### 1.3 Intended Audience
- SIH judges/evaluators
- Development team members (backend, frontend, corpus/research, QA)
- Future maintainers (Stage 2–4 teams)

### 1.4 Definitions, Acronyms, Abbreviations
| Term | Meaning |
|---|---|
| RAG | Retrieval-Augmented Generation |
| TK | Traditional Knowledge |
| TKDL | Traditional Knowledge Digital Library |
| ABS | Access and Benefit-Sharing |
| GI | Geographical Indication |
| DPDP | Digital Personal Data Protection (Act, India) |
| MVP | Minimum Viable Product |
| PS | Problem Statement |

### 1.5 References
- Problem Statement SIH26045 (Ministry of Ayush)
- Patents Act, 1970 and 2024 Rules
- Biological Diversity Act, 2002 (as amended 2023) and 2024 Rules
- WIPO Treaty on Genetic Resources and Associated Traditional Knowledge (2024)
- Companion project documents: PRD (Doc 1), Technical Architecture (Doc 2), Functional Requirements (Doc 3), Data Model (Doc 4), API Spec (Doc 5), Project Plan (Doc 6)

### 1.6 Overview
Section 2 gives an overall description of the product. Section 3 lists specific functional and non-functional requirements. Section 4 covers external interface requirements. Section 5 covers system features in detail. Section 6 covers other constraints, assumptions, and appendices.

---

## 2. Overall Description

### 2.1 Product Perspective
IP-SAKTI Sahayak is a new, standalone web application (chat-style interface) with a FastAPI backend, a vector-database-backed retrieval layer, and an LLM for answer generation. It is not a replacement for legal counsel; it is a decision-support and information tool.

### 2.2 Product Functions (summary)
- Formulation classification
- Jurisdiction-aware Q&A with citations
- Confidence scoring and safe abstention
- ABS-compliance checklist
- Static TKDL/prior-art lookup
- Human-facilitator escalation
- Multilingual query/answer (demo scope)

### 2.3 User Classes and Characteristics
| User Class | Technical Skill | Legal Skill | Primary Need |
|---|---|---|---|
| AYUSH Startup Founder | Medium | Low | Patentability & classification guidance |
| Ayurvedic Practitioner | Low | Low | Understand if formulation is protectable |
| Cultivator/TK Holder | Low | Low | ABS guidance in plain language |
| AYUSH MSME/Exporter | Medium | Low–Medium | Jurisdiction-specific export guidance |
| SIH Judge/Evaluator | High | Medium | Assess correctness, traceability, safety |

### 2.4 Operating Environment
- Web-based; runs in modern browsers (Chrome/Edge/Firefox)
- Backend: Python 3.10+, FastAPI
- Vector store: Chroma or FAISS (local for MVP)
- Deployable locally or on a lightweight cloud host (Render/Railway/HF Spaces) for demo purposes

### 2.5 Design and Implementation Constraints
- Must ground every answer in retrieved corpus text — no answer may be generated purely from the LLM's parametric knowledge.
- Must maintain a strict separation between India and International jurisdiction contexts at the retrieval-filtering level, not just in prompt phrasing.
- Hackathon time-box (36 hours) constrains scope to the Stage 1 MVP defined in the Project Plan (Doc 6).

### 2.6 Assumptions and Dependencies
- A curated corpus (Doc 4 list) will be assembled from official sources before/at the start of the build.
- Team has access to an LLM API key or a locally runnable open-weight model.
- No real user accounts or persistent PII storage in MVP — dependency on DPDP-grade infrastructure deferred to Stage 4.

---

## 3. Specific Requirements

### 3.1 Functional Requirements

**FR-1 Jurisdiction Toggle**
The system shall allow the user to select "India" or "International" and shall restrict retrieval and generation to the corresponding corpus subset for that session state.

**FR-2 Formulation Classification**
The system shall present a guided questionnaire (minimum number of questions) and shall output one of six classifications: Classical/Generic Medicine, Patent-or-Proprietary Medicine, New/Non-classical Drug, Phytopharmaceutical, Ayurveda-Aahar/Nutraceutical, or Cosmetic, along with a plain-language explanation of that category's IP/ABS posture.

**FR-3 Grounded Question Answering**
The system shall retrieve relevant corpus chunks for a user query (filtered by jurisdiction and, where available, classification context) and shall generate an answer strictly grounded in the retrieved text.

**FR-4 Mandatory Citation**
The system shall attach at least one citation (source title + section/article) to every substantive answer. Answers without a supporting citation shall not be presented as factual claims.

**FR-5 Confidence Scoring**
The system shall compute and display a confidence indicator (e.g., High/Medium/Low) for every answer, derived from retrieval similarity scores.

**FR-6 Safe Abstention**
The system shall decline to answer (and shall state so explicitly) when confidence is below a defined threshold or when the query is determined to be out of scope, rather than generating an unsupported answer.

**FR-7 Escalation**
The system shall provide a mechanism for the user to request escalation to a human IP facilitator, particularly on low-confidence or abstained answers.

**FR-8 Persistent Disclaimer**
The system shall display a persistent notice that it provides information, not legal advice, on every screen/response.

**FR-9 TKDL/Prior-Art Pointer**
The system shall provide a lookup function returning example prior-art/TKDL-style matches for a given formulation keyword (static dataset acceptable for MVP).

**FR-10 ABS Compliance Checklist**
The system shall generate a basic rule-based ABS-compliance checklist based on the user's formulation classification.

**FR-11 Multilingual Demo**
The system shall support submission and response in at least one Indian language in addition to English, for demonstration purposes.

**FR-12 Query Logging (session-scoped)**
The system shall log queries, retrieved chunk IDs, confidence scores, and abstention flags for evaluation purposes, without persisting personally identifying information beyond the session.

### 3.2 Non-Functional Requirements

**NFR-1 Accuracy over Fluency**
The system shall be tuned to prefer abstention over a fluent but unsupported answer.

**NFR-2 Traceability**
Every factual claim in an answer shall be traceable to a specific retrieved corpus chunk with source metadata.

**NFR-3 Performance**
The system shall return an answer within approximately 5–8 seconds under demo conditions.

**NFR-4 Usability**
The classification flow and jurisdiction toggle shall be usable without prior legal training; question wording shall avoid unexplained legal jargon.

**NFR-5 Privacy (MVP-level)**
The system shall not persist PII beyond the active session and shall disclose this to the user. Full DPDP-grade compliance (encryption at rest, access controls, audit trail) is deferred to Stage 4 and documented, not implemented, in the MVP.

**NFR-6 Maintainability**
Corpus documents shall carry version and effective-date metadata so future updates do not require restructuring the retrieval pipeline.

**NFR-7 Portability**
The system shall be deployable either fully locally (for offline/sovereign demo scenarios) or on a lightweight cloud host, without code changes beyond configuration.

### 3.3 External Interface Requirements

**3.3.1 User Interfaces**
- Chat-style main interface with: jurisdiction toggle, classification-flow entry point, message input, citation display beneath each answer, confidence badge, escalation button, persistent disclaimer banner.

**3.3.2 Software Interfaces**
- LLM API (OpenAI-compatible or equivalent) or local open-weight model runtime.
- Vector database client (Chroma/FAISS).
- Optional translation API for multilingual demo (or Bhashini API stub, per PS recommendation).

**3.3.3 Communication Interfaces**
- REST over HTTPS (or HTTP for local demo) between frontend and backend, as specified in the API Specification (Doc 5).

### 3.4 System Features (traceability to user stories, Doc 3)
| Feature | Related FR(s) | Related User Story |
|---|---|---|
| Classification flow | FR-2 | US-A1, US-A2 |
| Jurisdiction toggle | FR-1 | US-B1 |
| Cited Q&A | FR-3, FR-4 | US-B2 |
| Confidence & abstention | FR-5, FR-6 | US-C1, US-C2 |
| Disclaimer | FR-8 | US-C3 |
| Escalation | FR-7 | US-C4 |
| TKDL lookup | FR-9 | US-D1 |
| ABS checklist | FR-10 | US-D2 |
| Multilingual | FR-11 | US-E1 |

---

## 4. Verification / Acceptance Criteria
Each functional requirement above is considered met when its corresponding acceptance criterion in the Functional Requirements & User Stories document (Doc 3) passes on the test query set defined in the Project Plan (Doc 6, Section 4.2).

## 5. Appendix

### 5.1 Requirements Traceability to PS Expected Solution
| PS Expected-Solution Element | Covered By |
|---|---|
| Citation-grounded RAG MVP | FR-3, FR-4, NFR-1, NFR-2 |
| Jurisdiction toggle | FR-1 |
| Formulation classification flow | FR-2 |
| ABS-compliance helper + TKDL pointer | FR-9, FR-10 |
| Mandatory citations + confidence + escalation | FR-4, FR-5, FR-6, FR-7 |
| Multilingual delivery | FR-11 |
| Guardrails / disclaimer / privacy alignment | FR-8, NFR-5 |
| Knowledge graph / agentic orchestration | Deferred — Stage 2 (see Doc 6 Roadmap) |
| Paid-source connectors, full multilingual/voice | Deferred — Stage 3/4 (see Doc 6 Roadmap) |

### 5.2 Out-of-Scope Statement (MVP)
Live registry connectors, full knowledge graph reasoning, full Bhashini voice pipeline, paid-source integrations, and DPDP-grade audit infrastructure are explicitly out of scope for the hackathon MVP and are documented as staged future work, not implemented in this version.
