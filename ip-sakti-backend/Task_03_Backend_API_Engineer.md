# Task Document — Role 3: Backend / API Engineer (Classification, ABS, TKDL)
## IP-SAKTI Sahayak (SIH26045) — Individual Work Assignment

---

## 1. Role Summary
You build everything in the backend that isn't the core RAG pipeline: the FastAPI application shell, the formulation-classification engine, the ABS-compliance checklist logic, and the TKDL/prior-art lookup. You're also the integration point that assembles Role 2's RAG functions and Role 5's graph functions into one coherent API that Role 4's frontend can call.

## 2. Dependencies
- Works in parallel with Role 2 from Day 1 (different subsystems), integrates with Role 2's `/query` logic starting Day 6–7.
- Needs Role 1's ABS/TKDL illustrative dataset by Phase 3 (Day 9-ish) to build real matching logic.
- Role 4 depends on your endpoints being stable and documented early — communicate any API changes immediately.

## 3. Reference Documents to Read First
- `05_API_Specification.md` — this entire document is your build spec; treat every endpoint as a contract.
- `03_Functional_Requirements_User_Stories.md` — Epic A (classification), Epic D (ABS/TKDL) are your primary user stories.
- `04_Data_Model_Corpus_Design.md` — Section 5 (application data model: session, query_log, tkdl_demo_record) and Section 6 (classification taxonomy).
- `07_SRS.md` — FR-2, FR-7, FR-8, FR-9, FR-10, FR-12.

## 4. Detailed Task Breakdown

### Phase 1 (Days 1–3) — Backend Skeleton
- Set up the FastAPI project structure (shared repo with Role 2 — agree on folder structure and dependency management on Day 1).
- Implement `POST /session` and session storage (in-memory or lightweight DB like SQLite is fine for MVP — no need for production-grade DB per NFR-5 privacy note in `07_SRS.md`).
- Implement `PATCH /session/{session_id}/jurisdiction`.
- Design the classification decision-tree: work out the actual question sequence needed to sort a formulation into the 6 categories from `04_Data_Model_Corpus_Design.md` Section 6. Sketch this as a flowchart before coding — this logic needs to be legally sound, so review it with Role 1 before implementing.

### Phase 2 (Days 3–7) — Classification Engine + Core Endpoints
**Day 3–4:**
- Implement the classification engine as a simple state machine (question → answer → next question or final result), backing `POST /classification/start` and `POST /classification/answer` per the API spec's exact response shapes.
- Each final classification result must include the plain-language explanation of that category's IP/ABS posture (get this wording reviewed by Role 1 — legal accuracy matters even in a UI-facing string).

**Day 4–6:**
- Implement `POST /escalate` (simple logging stub — no real routing needed for MVP, per API spec Section 8).
- Implement the `query_log` table/storage and wire logging into whichever endpoints touch a query (coordinate with Role 2 — you likely own the storage layer, Role 2 populates it from within `/query`).
- Stub out `/tkdl/lookup` and `/abs/checklist` with placeholder logic so Role 4 can start frontend integration without waiting for Phase 3's real logic.

**Day 6–7:**
- Integrate Role 2's `rag_orchestrator` into the `/query` endpoint end-to-end.
- Full backend integration test: session creation → jurisdiction set → classification → query → citation response, all through real HTTP calls (not just unit tests).

### Phase 3 (Days 7–12) — ABS/TKDL Depth Features
**Day 8–10:**
- Take Role 1's illustrative ABS/TKDL dataset (`tkdl_demo_record` entries) and implement real matching logic for `GET /tkdl/lookup?keyword={keyword}` — use keyword matching plus basic semantic similarity (you can reuse Role 2's embedding model for this rather than building a separate one) instead of a flat lookup table.
- Ensure every response includes the `is_illustrative: true` flag and doesn't overstate itself as live TKDL data (see Role 1's note on TKDL access restrictions).
- Implement `GET /abs/checklist?classification={classification}` with real rule-based logic mapping each of the 6 classifications to a meaningful, legally-reviewed checklist (get Role 1 to sanity-check the checklist content).

**Day 10–12:**
- Support integration testing for knowledge-graph-assisted queries (Role 5/Role 2's work) — make sure your classification-context payload correctly flows into the query router.
- Fix any API-contract mismatches surfaced during Phase 2/3 integration testing with Role 4.

### Phase 4 (Days 12–16+) — Hardening
- Implement `POST /translate` integration (or hand this to Role 5 if they're the multilingual specialist — coordinate ownership explicitly by Day 12).
- Add proper error handling across all endpoints (the error format in API spec Section 10) — every endpoint should fail gracefully, not 500 with a stack trace, during the live demo.
- Support the full evaluation pass: be available to quickly patch any classification-logic or endpoint bugs the QA pass surfaces.
- Basic input validation and rate-limit-free but abuse-resistant handling (no need for production auth per SRS Section 3.4 Auth Note, but don't leave endpoints trivially breakable during a live demo).

## 5. Deliverables Checklist
- [ ] FastAPI project scaffolded, shared repo structure agreed with Role 2
- [ ] `/session`, `/session/{id}/jurisdiction` endpoints working
- [ ] Classification decision-tree designed and reviewed by Role 1
- [ ] `/classification/start`, `/classification/answer` implemented
- [ ] `/escalate` implemented
- [ ] `query_log` storage implemented
- [ ] `/query` fully integrated with Role 2's RAG pipeline
- [ ] `/tkdl/lookup` with real matching logic (Phase 3)
- [ ] `/abs/checklist` with reviewed rule-based logic (Phase 3)
- [ ] `/translate` integrated (Phase 4, ownership confirmed with Role 5)
- [ ] Full error handling across all endpoints
- [ ] End-to-end integration test passing (session → classify → query → citations)

## 6. Tools/Stack
- Python, FastAPI, SQLite (or in-memory) for session/query storage
- Shared embedding model access from Role 2 for TKDL semantic matching

## 7. What "Good" Looks Like
A frontend developer (Role 4) should be able to build against your API purely from the spec document, without needing to ask you what a response looks like — because your implementation matches the spec exactly, and error cases are handled, not left to crash.
