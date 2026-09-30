# Functional Requirements & User Stories
## IP-SAKTI Sahayak (SIH26045)

---

## 1. Personas (reference)
- **P1 — Startup Founder (Anya):** wants patentability + regulatory classification guidance
- **P2 — Practitioner (Vaidya Ramesh):** wants to know if his classical formulation is protectable
- **P3 — Cultivator (Community TK holder):** wants ABS guidance before disclosing knowledge
- **P4 — MSME Exporter (Priya):** wants international/export-market IP guidance

## 2. User Stories

### Epic A — Formulation Classification
- **US-A1:** As a user, I want to answer a short guided questionnaire so the assistant can classify my formulation (classical / proprietary / new drug / phytopharmaceutical / Ayurveda-Aahar / cosmetic).
  - *Acceptance criteria:* Minimum number of questions asked; classification result displayed with a one-line explanation of what that category implies for IP/ABS.
- **US-A2:** As a user, I want to skip classification and ask a general question if I don't know my product's category.
  - *Acceptance criteria:* Assistant still answers but flags that classification-specific nuance may be missing.

### Epic B — Jurisdiction-Aware Q&A
- **US-B1:** As a user, I want to toggle between India and International law so I don't get conflated answers.
  - *Acceptance criteria:* Toggle visibly changes the answer context; switching jurisdiction on the same question produces a distinctly labeled second answer, never merged into one.
- **US-B2:** As a user, I want every answer to cite the specific statute/section/treaty article it relies on.
  - *Acceptance criteria:* 100% of substantive answers contain at least one inline citation with source name + section/article.

### Epic C — Trust & Safety
- **US-C1:** As a user, I want to see a confidence indicator on each answer so I know how much to trust it.
  - *Acceptance criteria:* Low-confidence answers are visually flagged and include a suggestion to escalate.
- **US-C2:** As a user, I want the assistant to say "I don't know" rather than guess when a question is out of scope.
  - *Acceptance criteria:* On out-of-scope test queries, assistant abstains instead of fabricating an answer.
- **US-C3:** As a user, I want a persistent disclaimer reminding me this is information, not legal advice.
  - *Acceptance criteria:* Disclaimer visible on every screen/response.
- **US-C4:** As a user, I want an easy way to escalate to a human IP facilitator when the assistant can't help.
  - *Acceptance criteria:* Escalation CTA present on low-confidence/abstained answers.

### Epic D — TK & ABS Support
- **US-D1:** As a cultivator, I want to check if my traditional knowledge is already recorded (prior art) so I understand my ABS position.
  - *Acceptance criteria:* Assistant returns matching/near-matching TKDL demo records for a sample query.
- **US-D2:** As a startup founder, I want a basic ABS-compliance checklist relevant to my formulation type.
  - *Acceptance criteria:* Rule-based checklist output tied to classification result from Epic A.

### Epic E — Multilingual Access
- **US-E1:** As a non-English-speaking practitioner, I want to ask questions in my regional language.
  - *Acceptance criteria:* Demo supports at least one additional Indian language via translation layer; citations remain in original legal language with translated explanation.

## 3. Functional Requirements Summary Table
| ID | Requirement | Priority |
|---|---|---|
| FR-1 | Jurisdiction toggle (India/International) | Must-have |
| FR-2 | Formulation classification flow | Must-have |
| FR-3 | RAG Q&A grounded in curated corpus | Must-have |
| FR-4 | Mandatory inline citations | Must-have |
| FR-5 | Confidence indicator + abstention | Must-have |
| FR-6 | Persistent "not legal advice" disclaimer | Must-have |
| FR-7 | Escalation-to-human CTA | Must-have |
| FR-8 | Static TKDL/prior-art lookup demo | Should-have |
| FR-9 | ABS-compliance checklist | Should-have |
| FR-10 | Multilingual demo (1+ language) | Should-have |
| FR-11 | Knowledge graph reasoning | Won't-have (MVP) — Stage 2 |
| FR-12 | Live TKDL / paid-source connectors | Won't-have (MVP) — Stage 3 |
| FR-13 | Full Bhashini voice integration | Won't-have (MVP) — Stage 4 |
| FR-14 | DPDP-grade audit/security | Won't-have (MVP) — Stage 4 |

## 4. Sample Test Queries (for eval, see Doc 6)
1. "Can I patent a classical Ayurvedic formulation from Charaka Samhita?" (expect: Section 3(p) bar explanation, TK/TKDL context)
2. "What ABS obligations apply if I source a plant from a tribal community?" (expect: Biological Diversity Act reference)
3. "Is my herbal capsule a drug or a food supplement under FSSAI rules?" (expect: classification-flow trigger)
4. "What's the capital of France?" (expect: abstention — out of scope)
5. "How do I protect my formulation in the EU market?" (expect: jurisdiction = International; TRIPS/export-market context)
