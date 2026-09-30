# Data Model & Corpus Design Document
## IP-SAKTI Sahayak (SIH26045)

---

## 1. Purpose
Defines the structure of the curated legal/regulatory corpus (the RAG knowledge base) and the lightweight relational data needed for session/classification state. This is the highest-leverage document for this project — answer quality depends entirely on corpus quality and chunking discipline.

## 2. Official Source Registry (per PS-provided dataset guidance)
The problem statement itself names these as representative open, authoritative public sources. All corpus documents below should be traced back to one of these registries wherever possible — do not substitute secondary/blog sources for these.

| Source | URL | Use for |
|---|---|---|
| Traditional Knowledge Digital Library (TKDL) | tkdl.res.in | TK/prior-art records; grounding the TKDL-pointer feature (FR-9) with real (not purely synthetic) example entries where publicly accessible |
| India Code | indiacode.nic.in | Primary text of all Indian statutes and rules (Patents Act, Biological Diversity Act, Designs Act, Copyright Act, Plant Variety Act, Drugs and Cosmetics Act, etc.) |
| IP India public databases (InPASS, Trade Marks, Designs, GI Registry) | ipindia.gov.in | Verifying patent/trademark/design/GI status examples; sourcing registry-record metadata for the corpus; useful for building realistic demo queries and for the TKDL/prior-art lookup feature |

**Note on TKDL access:** TKDL's full database has restricted access under bilateral access agreements (it's designed to be shown to patent examiners, not scraped publicly). For the MVP's TKDL-pointer feature, use whatever is publicly documented about TKDL's classification scheme and any publicly available sample/illustrative entries, and clearly label demo entries as illustrative rather than claiming they are live TKDL data. This keeps FR-9 honest without requiring privileged database access.

## 3. Corpus Document Set (MVP — prioritize these first)

### India — National Layer
| # | Document | Regime |
|---|---|---|
| 1 | Patents Act, 1970 — esp. Section 3(p) | Patents |
| 2 | Patent (Amendment) Rules, 2024 | Patents |
| 3 | Geographical Indications of Goods (Registration & Protection) Act, 1999 | GI |
| 4 | Trade Marks Act, 1999 (relevant sections) | Trademarks |
| 5 | Designs Act, 2000 (relevant sections) | Designs |
| 6 | Copyright Act, 1957 (relevant sections) | Copyright |
| 7 | Protection of Plant Varieties and Farmers' Rights Act, 2001 | Plant Variety |
| 8 | Biological Diversity Act, 2002 (as amended 2023) | ABS |
| 9 | Biological Diversity Rules, 2024 | ABS |
| 10 | Drugs and Cosmetics Act, 1940 (Ayurveda-relevant provisions) | Drug regulation |
| 11 | Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954 | Advertising |
| 12 | FSSAI Ayurveda-Aahar Regulations | Food/Nutraceutical |
| 13 | TKDL classification scheme overview (public documentation) | TK/Prior-art |

### International Layer
| # | Document | Regime |
|---|---|---|
| 14 | TRIPS Agreement (relevant articles) | Patents/IP baseline |
| 15 | Convention on Biological Diversity (CBD) | ABS |
| 16 | Nagoya Protocol | ABS |
| 17 | WIPO Treaty on Genetic Resources and Associated TK (2024) | TK/ABS |
| 18 | Patent Cooperation Treaty (PCT) — filing basics | Patents |
| 19 | Madrid System overview | Trademarks |
| 20 | Hague System overview | Designs |
| 21 | Budapest Treaty (micro-organism deposits) | Patents (biotech) |
| 22 | Summary of herbal-product market access rules (1–2 key export markets, e.g., EU/US) | Export/regulatory |

> Team should source items #1–13 primarily from **India Code (indiacode.nic.in)**, cross-checked against **IP India (ipindia.gov.in)** for anything patent/trademark/design/GI-registry specific. Items #14–22 (international) fall outside indiacode.nic.in's scope — source these directly from WIPO, the CBD Secretariat, and the relevant treaty-body's own publication pages. Do not use secondary blog summaries as ground truth — cite the primary source even if a secondary source is used to locate it.

## 4. Chunking Strategy
- **Granularity:** section/article-level, not fixed token windows — legal citation must map to a real numbered provision.
- **Overlap:** minimal (~1 sentence) only where a provision's meaning depends on the immediately preceding clause.
- **Chunk metadata schema (attached to every chunk):**

```json
{
  "chunk_id": "string (uuid)",
  "source_title": "string (e.g., 'Patents Act, 1970')",
  "section_or_article": "string (e.g., 'Section 3(p)')",
  "jurisdiction": "India | International",
  "regime": "Patents | GI | Trademarks | Designs | Copyright | PlantVariety | ABS | DrugRegulation | Advertising | Food | TK",
  "effective_date": "date",
  "doc_version": "string",
  "source_url": "string (official source link)",
  "text": "string (chunk content)"
}
```

## 5. Application Data Model (lightweight — sessions, not user accounts, for MVP)

### `session`
| Field | Type | Notes |
|---|---|---|
| session_id | uuid | primary key |
| jurisdiction_selected | enum(India, International) | current toggle state |
| classification_result | enum / nullable | from classification flow |
| created_at | timestamp | |

### `query_log` (for demo/eval purposes only — not production PII storage)
| Field | Type | Notes |
|---|---|---|
| query_id | uuid | primary key |
| session_id | uuid | FK |
| query_text | string | |
| retrieved_chunk_ids | array[uuid] | |
| confidence_score | float | |
| abstained | boolean | |
| answer_text | string | |
| timestamp | timestamp | |

### `tkdl_demo_record` (illustrative seed data for prior-art demo — see Section 2 note on TKDL access)
| Field | Type | Notes |
|---|---|---|
| record_id | uuid | |
| formulation_keyword | string | |
| classification | string | |
| matched_note | string | e.g., "Similar formulation pattern illustrated by TKDL Class XX" |
| is_illustrative | boolean | true for MVP — flags that this is a demo/illustrative entry, not a live TKDL query result |

## 6. Classification Taxonomy (used across corpus filtering + classification engine)
1. Classical / Generic Medicine (First-Schedule authoritative text)
2. Patent-or-Proprietary Medicine
3. New / Non-classical Drug
4. Phytopharmaceutical
5. Ayurveda-Aahar / Nutraceutical
6. Cosmetic

Each category maps to a pre-defined set of relevant regime tags used to narrow retrieval (e.g., "Classical" → weight TK/ABS/Patents-3(p) heavily; "New Drug" → weight Drug-regulation + Patents heavily).

## 7. Data Quality & Versioning Notes
- Every source document stamped with `doc_version` and `effective_date` — critical given the 2023/2024 legal changes referenced in the PS.
- Maintain a simple changelog file (`corpus_changelog.md`) noting when a source was added/updated — this directly supports the PS requirement to "keep its corpus current as the law changes."
