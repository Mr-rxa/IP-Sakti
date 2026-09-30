# Product Requirements Document (PRD)
## IP-SAKTI Sahayak — Multilingual RAG Assistant for Ayurveda IPR & Regulatory Guidance
**PS Number:** SIH26045 | **Ministry:** Ministry of Ayush | **Category:** Software

---

## 1. Problem Statement (condensed)
Ayurvedic innovation sits at the intersection of seven overlapping legal regimes — patents, GI, trademarks, copyright, designs, trade secrets, plant-variety rights — plus Access-and-Benefit-Sharing (ABS) obligations and a drug-regulatory framework that varies by product classification. Practitioners, AYUSH startups, MSMEs, and cultivators have no single authoritative, plain-language tool to navigate this. Result: under-protection of legitimate innovation domestically, and exposure of Indian traditional knowledge (TK) to misappropriation abroad.

## 2. Goals & Objectives
| Goal | Metric |
|---|---|
| Give accurate, source-cited IPR guidance specific to Ayurveda | ≥90% citation correctness on eval set |
| Keep India vs. international law strictly separated | 100% of answers tagged with correct jurisdiction |
| Correctly classify a formulation before answering IP questions | ≥85% classification accuracy on labeled test cases |
| Prevent hallucinated legal claims | 0 fabricated citations in eval set; safe abstention on out-of-scope queries |
| Be usable by non-lawyers in regional languages | Demo in ≥2 languages (English + 1 Indian language) |

## 3. Target Users / Personas
1. **AYUSH Startup Founder** — needs to know if their formulation is patentable and what regulatory category it falls under before raising funds.
2. **Ayurvedic Practitioner / Vaidya** — wants to know if a classical formulation they use can be protected or is public-domain TK.
3. **Cultivator / Community TK holder** — needs plain-language ABS guidance before sharing biological resource knowledge with a company.
4. **AYUSH MSME / Researcher** — needs jurisdiction-specific guidance when exporting a formulation.

## 4. Scope

### In Scope (Hackathon MVP — Stage 1)
- Formulation classification flow (guided Q&A → classical / proprietary / new drug / phytopharmaceutical / Ayurveda-Aahar / cosmetic)
- Jurisdiction toggle (India ↔ International) with visibly separated answer sets
- RAG-based Q&A over a curated corpus of Indian statutes/rules + international treaties
- Mandatory inline source citation (statute, section, treaty article)
- Confidence indicator + safe-abstention behavior on uncertain/out-of-scope queries
- Standing "information, not legal advice" disclaimer
- Static escalation-to-human-facilitator stub
- Demo of multilingual capability (stub/API-based translation for 1–2 languages)

### Out of Scope (explicitly deferred — Stage 2+)
- Full relational knowledge graph across IP types
- Live agentic multi-source orchestration
- Live Bhashini integration (voice + full multilingual pipeline)
- Live TKDL registry connector (hardcoded example matches only for demo)
- Paid-source connectors (user's own subscriptions) with logged permission
- Full DPDP-aligned audit/security infrastructure (documented in architecture, not built)

## 5. Key Features (MVP)
1. Jurisdiction Toggle
2. Formulation Classifier (guided intake)
3. RAG Chat Assistant with citations
4. Confidence Indicator & Abstention
5. TKDL / Prior-Art Pointer (static demo data)
6. ABS-Compliance Helper (rule-based checklist, not full agentic reasoning)
7. Escalation-to-human stub
8. Disclaimer banner (persistent)
9. Multilingual demo toggle

## 6. Non-Functional Requirements
- **Accuracy over fluency**: assistant must prefer "I don't know / consult a facilitator" over a confident wrong answer.
- **Traceability**: every factual claim must map to a retrieved chunk with source metadata.
- **Latency**: answer within ~5–8 seconds for demo purposes.
- **Privacy**: no PII stored beyond session; disclosed clearly to user (design toward DPDP alignment, not full compliance for MVP).

## 7. Success Metrics (for judging / eval)
- Answer accuracy (spot-checked against ground truth from source docs)
- Citation correctness (citation actually supports the claim)
- Safe abstention rate on deliberately out-of-scope test queries
- Jurisdiction-separation correctness (no cross-contamination of India/international answers)
- Multilingual answer quality (basic fluency + citation retention)

## 8. Assumptions & Constraints
- Corpus is static/curated for MVP — not live-updated from government sources during hackathon.
- No real legal sign-off — tool explicitly positioned as "information, not advice."
- Team has access to an LLM API (or open-weight model) and basic cloud/local compute for the demo.

## 9. Staged Roadmap Summary (see Doc 6 for full plan)
1. **Stage 1 (Hackathon MVP):** Citation-grounded RAG + classifier + jurisdiction toggle
2. **Stage 2:** Knowledge graph + agentic orchestration
3. **Stage 3:** Paid-source connectors, live TKDL integration
4. **Stage 4:** Full multilingual + voice (Bhashini), DPDP-grade security/audit

## 10. Open Questions
- Which specific statutes/treaties will be prioritized for the initial corpus (finalize list before Doc 4 corpus build)?
- Which LLM/embedding provider will the team standardize on (cost vs. quality trade-off)?
- Will the demo target English + Hindi, or a different regional language pairing?
