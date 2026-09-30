# IP-SAKTI RAG Backend

This folder contains the working RAG pipeline for the Ayurveda IPR/legal corpus.

## Build The Corpus

The researcher DOCX notes are converted into section/heading-level chunks with stable metadata:

```powershell
.\venv\Scripts\python.exe -m app.corpus_builder
```

Output:

- `data/corpus/corpus.json`
- `data/corpus/corpus_manifest.json`
- `data/corpus/corpus_changelog.md`

Validate the checked-in corpus and manifest without rebuilding it:

```powershell
.\venv\Scripts\python.exe -m app.corpus_manifest --validate
```

## Build Retrieval Indexes

Build the local BM25 index:

```powershell
.\venv\Scripts\python.exe -m app.ingestion --dense off
```

Build BM25 plus Chroma/Gemini dense embeddings when `GEMINI_API_KEY` is configured:

```powershell
.\venv\Scripts\python.exe -m app.ingestion --dense on
```

The app works in BM25-only mode for offline demos. Dense retrieval and Gemini generation are optional quality upgrades.

## Evaluation

Run the grounded labeled set and write a JSON report:

```powershell
.\venv\Scripts\python.exe eval\run_evaluation.py
```

The checked-in labels are limited to claims directly represented by the 22-source corpus. Each metric is null when its label dimension has no cases; an empty `labeled_queries.json` is therefore a valid sparse-data run, not a passing accuracy claim. Citation accuracy checks the expected source title, while answer accuracy checks explicitly listed answer phrases.

## Provenance Graph Foundation

Export metadata relationships from the corpus to local JSON and SQLite artifacts:

```powershell
.\venv\Scripts\python.exe -m app.knowledge_graph
```

This creates `data/graph/corpus_graph.json` and `data/graph/corpus_graph.sqlite3`. Schema version `1.0.0` contains source-chunk, source, jurisdiction, regime, and section nodes with metadata-derived edges. Every node and edge records source chunk IDs. It is deliberately a provenance foundation only: no graph service, graph-based retrieval, or legal/agentic reasoning is claimed.

## Run The API

Offline/local deterministic mode:

```powershell
$env:IP_SAKTI_ENABLE_LLM='off'
$env:IP_SAKTI_ENABLE_DENSE='off'
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

Gemini-enabled mode:

```powershell
$env:GEMINI_API_KEY='your_key_here'
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

Base URL:

```text
http://127.0.0.1:8000/api/v1
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Main Query Endpoint

```powershell
$session = Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/v1/session

Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/v1/query `
  -ContentType 'application/json' `
  -Body (@{
    session_id = $session.session_id
    query_text = 'Can I patent a classical turmeric formulation if I slightly changed the ratio?'
    jurisdiction = 'India'
    classification_context = 'Classical/Generic Medicine'
  } | ConvertTo-Json)
```

Expected response fields:

- `answer_text`
- `citations`
- `confidence_score`
- `confidence_label`
- `abstained`
- `escalation_suggested`
- `retrieved_chunk_ids`

## Implemented RAG Layers

- DOCX corpus builder from legal research notes
- section/article-aware chunk metadata
- BM25 sparse retrieval
- optional Chroma + Gemini dense retrieval
- query understanding with offline fallback
- HyDE query expansion when Gemini is available
- LLM reranking with lexical fallback
- grounded JSON generation with extractive fallback
- claim verification with lexical fallback
- confidence scoring with a trainable model hook
- FastAPI endpoints from the project API spec

## Evaluation

Run the repeatable labeled-query evaluation. An empty labeled file is valid and produces a zero-case report:

```powershell
.\venv\Scripts\python.exe eval/run_evaluation.py
```

