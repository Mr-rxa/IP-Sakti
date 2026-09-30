# API Specification
## IP-SAKTI Sahayak (SIH26045) — Backend REST API

Base URL (local dev): `http://localhost:8000/api/v1`

---

## 1. `POST /session`
Create a new session.

**Request body:** *(none required)*

**Response 200:**
```json
{
  "session_id": "uuid",
  "created_at": "2026-08-21T10:00:00Z"
}
```

---

## 2. `PATCH /session/{session_id}/jurisdiction`
Set or change the jurisdiction toggle.

**Request body:**
```json
{
  "jurisdiction": "India"
}
```
*(enum: `"India"` | `"International"`)*

**Response 200:**
```json
{
  "session_id": "uuid",
  "jurisdiction": "India"
}
```

---

## 3. `POST /classification/start`
Begin the guided formulation-classification flow.

**Request body:**
```json
{ "session_id": "uuid" }
```

**Response 200:**
```json
{
  "question_id": "q1",
  "question_text": "Is your formulation drawn directly from a First-Schedule authoritative text (e.g., Charaka Samhita) without modification?",
  "options": ["Yes", "No", "Not sure"]
}
```

## 4. `POST /classification/answer`
Submit an answer in the classification flow; returns next question or final classification.

**Request body:**
```json
{
  "session_id": "uuid",
  "question_id": "q1",
  "answer": "Yes"
}
```

**Response 200 (mid-flow):**
```json
{
  "next_question_id": "q2",
  "question_text": "..."
}
```

**Response 200 (final):**
```json
{
  "classification_result": "Classical/Generic Medicine",
  "explanation": "Because this is drawn from a First-Schedule text, it is treated as traditional knowledge and generally faces the Section 3(p) patent bar. It is defended primarily through the Traditional Knowledge Digital Library (TKDL) rather than new patent filing.",
  "relevant_regimes": ["Patents", "TK/ABS"]
}
```

---

## 5. `POST /query`
Main Q&A endpoint — submit a natural-language question.

**Request body:**
```json
{
  "session_id": "uuid",
  "query_text": "Can I patent a classical formulation I've slightly modified?",
  "jurisdiction": "India",
  "classification_context": "Classical/Generic Medicine"
}
```

**Response 200:**
```json
{
  "query_id": "uuid",
  "answer_text": "A classical formulation as recorded in a First-Schedule text generally cannot be patented under Section 3(p) of the Patents Act, 1970, as it is considered traditional knowledge...",
  "citations": [
    {
      "source_title": "Patents Act, 1970",
      "section_or_article": "Section 3(p)",
      "jurisdiction": "India",
      "source_url": "https://..."
    }
  ],
  "confidence_score": 0.87,
  "confidence_label": "High",
  "abstained": false,
  "escalation_suggested": false
}
```

**Response 200 (abstained / low confidence):**
```json
{
  "query_id": "uuid",
  "answer_text": "I don't have sufficient grounded information in my corpus to answer this confidently.",
  "citations": [],
  "confidence_score": 0.22,
  "confidence_label": "Low",
  "abstained": true,
  "escalation_suggested": true
}
```

---

## 6. `GET /tkdl/lookup?keyword={keyword}`
Static demo prior-art lookup.

**Response 200:**
```json
{
  "matches": [
    {
      "formulation_keyword": "Ashwagandha churna",
      "classification": "Classical",
      "matched_note": "Recorded in TKDL Class A61K — likely to face Section 3(p) bar."
    }
  ]
}
```

---

## 7. `GET /abs/checklist?classification={classification}`
Rule-based ABS compliance checklist.

**Response 200:**
```json
{
  "classification": "New Drug",
  "checklist": [
    "Determine if biological resource was accessed from within India (Biological Diversity Act applicability).",
    "Check if prior informed consent / benefit-sharing agreement is required under BD Rules 2024.",
    "Verify if National Biodiversity Authority (NBA) approval is needed before commercialization."
  ]
}
```

---

## 8. `POST /escalate`
Log an escalation request to a human IP facilitator (stub for MVP — just logs, no real routing).

**Request body:**
```json
{
  "session_id": "uuid",
  "query_id": "uuid",
  "user_contact_optional": "string or null"
}
```

**Response 200:**
```json
{ "status": "logged", "escalation_id": "uuid" }
```

---

## 9. `POST /translate` *(demo-only multilingual stub)*
**Request body:**
```json
{ "text": "Can I patent this formulation?", "target_language": "hi" }
```

**Response 200:**
```json
{ "translated_text": "क्या मैं इस फॉर्मूलेशन का पेटेंट करा सकता हूँ?" }
```

---

## 10. Error Format (all endpoints)
```json
{
  "error_code": "string",
  "message": "string"
}
```

## 11. Auth Note
No authentication required for hackathon MVP (public demo). Roadmap note: Stage 4 introduces access controls aligned with DPDP requirements if user accounts / paid-source connectors are added.
