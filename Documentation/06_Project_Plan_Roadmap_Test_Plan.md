# Project Plan, Staged Roadmap & Test/Evaluation Plan (v2 — Multi-Week Timeline)
## IP-SAKTI Sahayak (SIH26045)

> Revision note: this version replaces the original 36-hour hackathon sprint plan with a realistic multi-week build timeline. Several items previously deferred to "Stage 2" (knowledge graph, real ABS/TKDL logic, calibrated confidence) are now pulled into the active build. Only the genuinely infrastructure-heavy items (live paid-source connectors, full DPDP-grade audit infra, full voice pipeline) remain deferred.

---

## 1. Revised Staged Roadmap

| Stage | Scope | Timeframe |
|---|---|---|
| **Phase 1 — Foundation** | Full corpus research & structuring | Days 1–3 |
| **Phase 2 — Core Pipeline** | RAG, classifier, jurisdiction toggle, citation enforcement, testing | Days 3–7 |
| **Phase 3 — Depth Features** | Knowledge graph, real ABS/TKDL logic, calibrated confidence/abstention | Days 7–12 |
| **Phase 4 — Multilingual & Hardening** | Real translation integration, UI polish, full evaluation pass, pitch prep | Days 12–16+ |
| **Post-event Stage 5** | Live registry connectors, paid-source connectors w/ logged permission, full Bhashini voice, DPDP-grade audit/security | Deferred beyond event — documented only |

---

## 2. Phase-by-Phase Execution Plan

### Phase 1 — Foundation (Days 1–3)
**Goal:** A properly sourced, correctly structured corpus. This is the highest-leverage phase — do not rush it.

| Day | Tasks |
|---|---|
| Day 1 | Finalize the full document list (see Data Model Doc 4, Section 2). Assign each team member 4–6 documents. Source primary texts only (India Code, official gazette PDFs, WIPO/CBD/TRIPS official sites) — no blog summaries as ground truth. |
| Day 2 | Extract and clean text section-by-section. Tag each section with metadata (source_title, section_or_article, jurisdiction, regime, effective_date, doc_version, source_url) per the schema in Doc 4. |
| Day 3 | Peer-review corpus for completeness and correct metadata; stand up the vector DB (Chroma/FAISS) and do a first ingestion pass. |

**Exit criteria:** 20+ properly tagged, section-level source documents ingested into the vector store, reviewed by at least one teammate other than the one who sourced them.

---

### Phase 2 — Core Pipeline (Days 3–7)
**Goal:** A working, testable RAG assistant with classification and jurisdiction separation — built calmly, not under sprint pressure.

| Day | Tasks |
|---|---|
| Day 3–4 | Build backend skeleton (FastAPI), implement `/session`, `/query`, `/classification/*` endpoints per API Spec (Doc 5). |
| Day 4–5 | Build RAG orchestrator: query embedding, jurisdiction-filtered retrieval, citation-enforced prompt template. |
| Day 5–6 | Build classification engine (guided Q&A → 6-category output) and wire into query context. |
| Day 6–7 | Build frontend: chat UI, jurisdiction toggle, classification flow, citation display. Connect end-to-end. |

**Exit criteria:** A user can complete the classification flow, toggle jurisdiction, ask a question, and get a cited answer end-to-end, tested against at least 10 hand-written queries with manually verified expected answers.

---

### Phase 3 — Depth Features (Days 7–12)
**Goal:** Move features that would normally be "roadmap slide only" into the actual build, since time allows it.

| Day | Tasks |
|---|---|
| Day 7–8 | Design the knowledge graph schema: nodes = {formulation category, IP regime, statute/section, jurisdiction}; edges = applicability/dependency relationships. Populate from the corpus metadata already tagged in Phase 1. |
| Day 8–9 | Wire the knowledge graph into the query router so multi-step questions ("my classical formulation has been modified — what changes?") can traverse category → regime → applicable-law instead of relying on single-shot retrieval. |
| Day 9–10 | Build real ABS/TKDL matching: construct a small structured dataset of known TK/TKDL-style entries; implement keyword + semantic similarity matching (not a hardcoded lookup table) for the prior-art pointer and ABS checklist. |
| Day 10–11 | Calibrate confidence scoring: run 30–50 test queries, log retrieval similarity scores against manually judged correct/incorrect/abstain outcomes, and tune the abstention threshold based on real data rather than a guessed constant. |
| Day 11–12 | Regression-test Phases 2+3 together; fix integration bugs between the graph layer and the base RAG pipeline. |

**Exit criteria:** Knowledge-graph-assisted multi-step queries return correct, cited answers; ABS/TKDL matching returns sensible results on novel (non-hardcoded) test inputs; abstention threshold is backed by a documented calibration run, not a guess.

---

### Phase 4 — Multilingual & Hardening (Days 12–16+)
**Goal:** Take the demo from "working" to "presentation-ready and robust."

| Day | Tasks |
|---|---|
| Day 12–13 | Integrate a real translation layer (Bhashini API if accessible during the build window; otherwise Google/Azure Translate as a documented stand-in) across the full chat flow — not a single stubbed message. |
| Day 13–14 | UI polish: loading states, error handling, mobile responsiveness if time allows, confidence badge and escalation CTA refinement. |
| Day 14–15 | Full evaluation pass against the expanded test set (aim for 30–50 queries covering all dimensions in Section 4 below); fix any accuracy, citation, or abstention failures found. |
| Day 15–16 | Prepare architecture diagrams, pitch deck, and roadmap slide (for the genuinely deferred Stage 5 items); rehearse the live demo end-to-end at least twice. |

**Exit criteria:** System passes the full evaluation set at target thresholds (Section 4.4), multilingual flow works live (not just for one canned example), and the team has rehearsed a smooth demo.

---

## 3. Team Roles (unchanged structure, now with realistic workload across weeks rather than hours)

| Role | Phase 1 focus | Phase 2 focus | Phase 3 focus | Phase 4 focus |
|---|---|---|---|---|
| Corpus/Legal Research Lead | Full corpus sourcing & tagging | Support retrieval QA | Build knowledge graph schema + populate | Support evaluation (ground-truth judging) |
| Backend/RAG Engineer | Support corpus review | RAG orchestrator, prompt engineering | Wire knowledge graph into router | Confidence tuning, bug fixes |
| Backend/API Engineer | Vector DB setup | FastAPI endpoints, classification engine | ABS/TKDL matching logic | API hardening, error handling |
| Frontend Engineer | — | Chat UI, jurisdiction toggle, classification flow | Citation/graph-answer display | UI polish, loading/error states |
| Frontend/UX + Multilingual | — | Escalation/disclaimer UX | Support graph-answer UX | Real translation integration |
| QA/Pitch Lead | Corpus peer review | Build initial 10-query test set | Run 30–50 query calibration set | Full evaluation pass, deck, demo rehearsal |

---

## 4. Test / Evaluation Plan (expanded — now feasible with more time)

### 4.1 Evaluation Dimensions
1. **Answer accuracy** — verified against source documents by a human reviewer
2. **Citation correctness** — cited section/article actually supports the claim
3. **Safe abstention** — correctly declines on out-of-scope/uncertain queries
4. **Jurisdiction separation** — no conflation between India and International answers
5. **Multilingual quality** — fluency + citation retention in translated output
6. **Multi-step reasoning correctness** (new, enabled by knowledge graph) — correct traversal across category → regime → statute for compound questions
7. **ABS/TKDL matching relevance** (new) — sensible matches on inputs not seen during dataset construction

### 4.2 Expanded Test Query Set (30–50 queries, categorized)
| Category | Example | Target count |
|---|---|---|
| In-scope, India, single-step | "Can I patent a classical Ayurvedic formulation?" | 8–10 |
| In-scope, International, single-step | "How do I protect my formulation in the EU?" | 5–8 |
| ABS-specific | "What if I source a plant from a tribal community?" | 5 |
| Classification-triggering | "Is my herbal capsule a food or a drug?" | 5 |
| Multi-step (knowledge-graph-dependent) | "My classical formulation has been modified with a new extraction method — what changes in my IP options?" | 5–8 |
| Out-of-scope | "What's the weather today?" | 3 |
| Ambiguous/low-confidence | Vague or malformed legal questions | 3–5 |
| Multilingual variants | Repeat 3–5 of the above in a second language | 3–5 |

### 4.3 Manual QA Checklist (run at end of Phase 3 and again at end of Phase 4)
- [ ] Every substantive answer contains at least one citation
- [ ] Jurisdiction toggle changes retrieval context correctly (mirrored query test)
- [ ] Disclaimer visible on every screen
- [ ] Abstention triggers correctly on out-of-scope queries
- [ ] Escalation CTA appears on low-confidence answers
- [ ] Classification flow produces correct category on hand-crafted test cases
- [ ] Knowledge-graph multi-step queries traverse correctly (spot-check reasoning path, not just final answer)
- [ ] ABS/TKDL matching returns relevant results on inputs outside the seed dataset
- [ ] Multilingual flow works live across the full chat interaction, not just a single message
- [ ] Confidence threshold reflects the Phase 3 calibration run, documented with the data behind it

### 4.4 Target Thresholds (now realistic to actually measure, not just assert)
| Metric | Target |
|---|---|
| Citation correctness | ≥90% of citations verified to support their claim |
| Answer accuracy | ≥85% on the full 30–50 query set |
| Safe abstention rate | 100% correct on out-of-scope subset |
| Jurisdiction separation errors | 0 |
| Multi-step reasoning accuracy | ≥75% (harder category, lower bar acceptable) |

---

## 5. Risks & Mitigations (updated for multi-week build)

| Risk | Mitigation |
|---|---|
| Corpus research takes longer than 3 days | Buffer built into Phase 1; if slipping, cut breadth (fewer export-market summaries) before cutting depth on core Indian statutes |
| Knowledge graph scope creep | Timebox graph schema to the categories already defined in Doc 4's classification taxonomy — resist adding new regimes mid-build |
| Team members drop features under deadline pressure near Phase 4 | Keep Phase 3 "depth" features functionally isolated from Phase 2 "core" features so a partial Phase 3 failure doesn't break the base demo |
| LLM hallucinating citations despite grounding | Enforce strict prompt constraint + post-process citation verification (check cited section actually exists in the retrieved chunk set) — test this specifically during Phase 2 and re-check after Phase 3 integration |
| Translation layer introduces new errors near demo day | Integrate multilingual support by Day 13, leaving a buffer before Day 16 to catch and fix issues, rather than adding it last-minute |

---

## 6. Demo Script Outline (unchanged core structure, now backed by real evaluation data)
1. Problem framing (30s) — cite the fragmentation across 7+ regimes
2. Live demo: classification flow → jurisdiction toggle → cited answer (2 min)
3. Live demo: a multi-step, knowledge-graph-driven question (1 min) — showcases depth beyond a basic RAG bot
4. Show abstention on an out-of-scope query (30s)
5. Show multilingual flow live (30s)
6. Present evaluation results (accuracy/citation/abstention numbers from Section 4.4) — real numbers, not projected ones (1 min)
7. Roadmap slide: genuinely deferred Stage 5 items (live connectors, full voice, DPDP audit infra) (30s)
8. Close on impact: protects TK, unlocks commercialization for AYUSH MSMEs
