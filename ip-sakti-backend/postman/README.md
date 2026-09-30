# IP-SAKTI Sahayak — Postman API Collection & Environment

This directory contains the complete, ready-to-import Postman collection and environment configuration for testing the IP-SAKTI Sahayak backend API.

---

## 1. Files in this Directory

- `IP_SAKTI_Sahayak.postman_collection.json`: Complete collection v2.1.0 organized into 8 feature folders with sample payloads and automated environment variable capture scripts.
- `IP_SAKTI_Local.postman_environment.json`: Local development environment variables (`base_url`, `session_id`, `query_id`).

---

## 2. Collection Folder Structure

```
IP-SAKTI Sahayak Backend API
├── 01 - Session Management
│   ├── Create Session                     (Auto-saves {{session_id}})
│   ├── Set Jurisdiction to India
│   └── Set Jurisdiction to International
├── 02 - Formulation Classification
│   ├── Start Classification Flow
│   ├── Submit Answer - Classical (Yes to Q1 -> Final)
│   ├── Submit Answer - Non-Classical (No to Q1 -> Next)
│   ├── Submit Answer - Therapeutic Use (Q2 -> Q3)
│   └── Submit Answer - Phytopharmaceutical (Q3 -> Final)
├── 03 - Grounded RAG & Query
│   ├── Query - India Jurisdiction         (Auto-saves {{query_id}})
│   ├── Query - International Jurisdiction
│   └── Query - Safe Abstention
├── 04 - TKDL & Prior Art
│   ├── Lookup TKDL Prior Art (Ashwagandha)
│   └── Lookup TKDL Prior Art (Curcumin)
├── 05 - ABS & Biodiversity Compliance
│   ├── Get ABS Checklist - Classical Medicine
│   ├── Get ABS Checklist - Patent/Proprietary Medicine
│   └── Get ABS Checklist - Phytopharmaceutical
├── 06 - Facilitator Escalation
│   └── Log Escalation Request
├── 07 - Multilingual Translation
│   └── Translate Text (English to Hindi)
└── 08 - System & Health
    ├── Health Check
    └── Get Corpus Version
```

---

## 3. How to Use in Postman

1. Open **Postman**.
2. Click **Import** (top left).
3. Drag & drop or select:
   - `IP_SAKTI_Sahayak.postman_collection.json`
   - `IP_SAKTI_Local.postman_environment.json`
4. Select the **IP-SAKTI Local Environment** from the environment dropdown in the top right.
5. Start your backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
6. Run `01 - Session Management > Create Session`. The `session_id` will be automatically stored in your environment and used by subsequent requests!

---

## 4. Running via Newman CLI (Automated Test Execution)

```bash
# Install newman if not already installed
npm install -g newman

# Run the collection
newman run postman/IP_SAKTI_Sahayak.postman_collection.json \
  -e postman/IP_SAKTI_Local.postman_environment.json
```
