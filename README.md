# Greenko ESG & Safety Incident Intelligence Dashboard

> **AI-Powered Renewable Energy Risk Monitoring, Root Cause Detection, and Decision Support Platform**  
> *Developed as part of the Greenko AI/ML Engineering Technical Assessment*

---

## 1. Project Overview

Greenko operates complex utility-scale renewable energy assets across India, encompassing solar photovoltaic blocks, wind turbine farms, pumped storage hydro installations, and high-voltage transmission switchyards. Operating in these mission-critical environments entails stringent Environment, Health, Safety (EHS), and ESG compliance mandates.

This project delivers an enterprise-grade, offline-capable **AI Incident Intelligence Platform** that automates the analysis of unstructured safety and ESG incident narratives. The application transforms brief, unstructured incident logs into structured operational intelligence:
- Classifying incident categories (`safety`, `environment`, `esg_compliance`)
- Estimating severity risk scores (`low`, `medium`, `high`, `critical`)
- Extracting multidimensional operational risk tags
- Generating concise, non-hallucinated summaries
- Detecting recurring failure modes and operational patterns
- Formulating context-aware preventive and corrective actions (Immediate, Preventive, Long-term)
- Providing an interactive, responsive analytics dashboard for executive EHS leadership

The system operates **100% offline without requiring external paid APIs or internet connectivity**, ensuring full data privacy, deterministic execution, and zero third-party latency.

---

## 2. Problem Statement

Renewable site operators and contractors encounter diverse incident scenarios daily—ranging from wet walkway slips during module washing, wind turbine gearbox lube-oil seepage, and night-shift vehicle movements near unlit cable trenches, to hazardous waste segregation deviations.

Historically, incident narratives have been recorded as brief, free-text entries in field logs. Operations teams face several critical bottlenecks:
1. **Manual Categorization Overhead:** Safety officers must manually parse and label incidents, leading to inconsistent severity grading.
2. **Delayed Escalation:** High-consequence near-misses (e.g., vehicles operating near unbarricaded excavation trenches) often get categorized identically to minor housekeeping issues.
3. **Fragmented Institutional Memory:** Lessons learned from past turbine or solar block incidents are rarely correlated with active work fronts.
4. **Action Gaps:** Recommendations often default to generic reprimands rather than systematic hierarchy-of-controls interventions (Elimination, Engineering, Administrative, PPE).

---

## 3. Objectives

The primary technical and operational objectives of the platform are:

| Objective | Description |
|---|---|
| **Autonomous Incident Triage** | Ingest unstructured narratives and predict category, severity, and risk tags with explainable evidence. |
| **Contextual Risk Scoring** | Distinguish actual harm from near-misses and handle contextual negations (e.g., *"no injury occurred"* vs *"minor injury sustained"*). |
| **Lightweight RAG Decision Support** | Retrieve semantically similar historical incidents using TF-IDF cosine similarity to ground action recommendations. |
| **Hierarchy-of-Controls Recommendations** | Deliver tiered action plans: *Immediate Containment*, *Preventive Engineering Controls*, and *Long-term Governance*. |
| **Pattern & Management Insight Detection** | Discover recurring human and equipment trends across contractor supervision, fluid containment, and high-risk zones. |
| **Enterprise Visualization** | Provide a modern, responsive web dashboard with live analytics, SVG charts, and a real-time incident analysis studio. |

---

## 4. Technology Stack

- **Backend Framework:** Python 3.11+ / 3.14, FastAPI, Uvicorn, Pydantic v2
- **Data Engineering:** Pandas, NumPy, Pathlib
- **NLP & Machine Learning:** Scikit-Learn (`TfidfVectorizer`, Cosine Similarity), Python Regular Expressions (`re`), Custom Domain Lexicons
- **Testing & Verification:** Pytest, FastAPI TestClient (`httpx`)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Zero external CDNs, 100% offline-resilient native SVG charts)
- **Deployment & Cloud:** Railway (`Procfile`, `railway.json`, Nixpacks)

---

## 5. Project File Structure

The repository is organized into the following backend, frontend, data, and documentation files:

```text
05_esg_safety_incident_intelligence_dashboard/
- backend/
  - __init__.py                 # Marks the backend as a Python package
  - app.py                      # Defines the FastAPI application and API routes
  - config.py                   # Stores shared paths and application settings
  - models.py                   # Defines Pydantic request and response models
  - services/
  - __init__.py             # Marks the services folder as a Python package
  - classification.py       # Classifies incident narratives
  - data_service.py          # Loads and validates incident data
  - evaluation.py            # Evaluates analysis against reference cases
  - pattern_analyzer.py      # Finds recurring incident patterns and insights
  - preprocessing.py         # Cleans and prepares incident text
  - recommendation_engine.py # Generates risk tags and recommended actions
  - retrieval_service.py     # Retrieves similar historical incidents
  - severity_analyzer.py     # Scores incident severity and risk
  - summarizer.py            # Creates concise structured incident summaries
- data/
  - dynamic_incidents.csv        # Additional incident records for dashboard analysis
  - safety_esg_incidents.csv     # Main safety and ESG incident dataset
- frontend/
  - index.html                   # Defines the dashboard page
  - css/
  - dashboard.css            # Styles dashboard layout and KPI sections
  - incidents.css            # Styles incident lists and tables
  - main.css                 # Provides shared page styles
  - studio.css               # Styles the live analysis studio
  - js/
  - api.js                   # Connects the frontend to backend endpoints
  - app.js                   # Initializes and coordinates dashboard features
  - config.js                # Stores frontend configuration values
  - components/
  - charts.js            # Renders dashboard charts
  - incidentsTable.js    # Renders incident records in a table
  - insights.js          # Displays patterns and recommendations
  - kpiCards.js          # Renders key performance indicator cards
  - liveStudio.js        # Handles live incident analysis interactions
  - testAi.js            # Provides the AI analysis testing interface
- tests/
  - test_backend.py              # Tests backend routes and analysis behavior
  - test_frontend_assets.py      # Checks that required frontend assets exist
- candidate_task.md                # Contains the original assessment task
- case_study.html                  # Presents the project case study
- evaluation_rubric.md             # Contains the assessment rubric
- submission_instructions.md       # Explains how to submit the project
- Procfile                         # Defines the command used to start the web service
- railway.json                     # Configures Railway deployment
- requirements.txt                 # Lists required Python packages
- README.md                        # Documents the project and how to run it
- uvicorn-error.log                # Captures Uvicorn server errors
- uvicorn.log                      # Captures Uvicorn server output
```

---

## 6. Dataset Description & Defensive Handling

The bundled benchmark dataset (`data/safety_esg_incidents.csv`) comprises 6 representative renewable-energy incident narratives:

| Incident ID | Narrative | Reference Category | Reference Severity |
|---|---|---|---|
| `S001` | *Contractor slipped near wet walkway at solar block, minor injury, housekeeping issue* | `safety` | `medium` |
| `S002` | *Oil seepage observed near wind gearbox maintenance bay, contained with spill kit* | `environment` | `high` |
| `S003` | *PPE non-compliance observed during panel cleaning activity* | `safety` | `medium` |
| `S004` | *Near miss: vehicle movement close to cable trench during night shift* | `safety` | `high` |
| `S005` | *Water usage spike during module cleaning due to valve leakage* | `environment` | `medium` |
| `S006` | *Repeated waste segregation deviation at contractor storage area* | `esg_compliance` | `low` |

### Defensive Data Safeguards
1. **Preservation of Reference Ground Truth:** Target labels are strictly used for evaluation and benchmark verification; they are never fed as input features during prediction.
2. **Schema & Label Validation:** `DataService` dynamically verifies required columns (`incident_id`, `narrative`, `target_category`, `target_severity`), sanitizes whitespace, and checks labels against allowed sets (`safety`, `environment`, `esg_compliance` and `low`, `medium`, `high`, `critical`).
3. **Resilient Deduplication & Missing Values:** Duplicate incident IDs are automatically flagged and indexed defensively without crashing the server.
4. **Pathlib Resolution:** Paths are dynamically resolved relative to `BASE_DIR`, preventing current-working-directory bugs.

---

## 7. AI / NLP Pipeline Architecture

```
Raw Incident Narrative
        │
        ▼
[ 1. NLP Preprocessing ] ────────► Lowercasing, whitespace normalization, protected term retention
        │
        ├─────────────────────────────────────────────────┐
        ▼                                                 ▼
[ 2. Category Classification ]                [ 3. Severity Risk Scoring ]
  • Weighted Domain Lexicons                    • Negation pattern matching ("no injury")
  • TF-IDF Vectorization & Cosine Sim           • High-voltage, height, hydrocarbon rules
  • Consensus Conflict Resolution Engine        • Explainable Risk Score (0 - 100)
        │                                                 │
        ├─────────────────────────────────────────────────┤
        ▼                                                 ▼
[ 4. Lightweight RAG Retrieval ]              [ 5. Risk Tagging & Controls ]
  • Top-k Nearest Neighbor Narratives           • Multi-tag extraction with evidence
  • Citation & Similarity Scoring               • Hierarchy of Controls Recommendations
        │                                                 │
        └────────────────────────┬────────────────────────┘
                                 ▼
                     [ 6. AI Summarization ]
                       • Concise narrative summary
                       • Structured operational hazard
                       • Hedged contributing factors
                                 │
                                 ▼
               [ 7. Unified JSON & Dashboard UI ]
```

### 7.1 Text Preprocessing & Technical Term Preservation
Standard stopword filters inadvertently eliminate domain-critical keywords such as `"oil"`, `"spill"`, `"near"`, or `"miss"`. Our custom preprocessor maintains an explicit **Protected Domain Term List**:
`gearbox`, `turbine`, `solar`, `panel`, `electrical`, `leakage`, `seepage`, `oil`, `water`, `spill`, `kit`, `cable`, `trench`, `ppe`, `contractor`, `waste`, `segregation`, `walkway`, `valve`, `cleaning`, `night shift`, `near miss`, `slip`, `fall`, `injury`, `shock`, `fire`, `arc flash`.

### 7.2 Why a Hybrid Classification Approach?
With small sample sizes (N=6 in initial bootstrap), training a deep supervised neural network or fine-tuning a BERT model risks severe overfitting and catastrophic hallucination. Conversely, simple pure keyword lookups fail on nuanced narratives. 

Our **Hybrid Consensus Engine** combines:
1. **Domain Rule Engine:** Multi-word phrases and unigrams weighted by renewable asset domain importance.
2. **TF-IDF & Cosine Similarity:** Semantic vector alignment against historical narratives.
3. **Conflict Resolution Strategy:**
   - *Hybrid Consensus:* When rule match and top historical match agree ($\text{Confidence} \ge 0.85$).
   - *Rule Decisiveness:* When distinctive technical keywords (e.g., *"arc flash"*, *"oil seepage"*) indicate a specific operational category.
   - *Historical Retrieval:* When text lacks direct rule matches but aligns with historical incidents.
   - *Conservative Default:* Defaults to `safety` with explicit disclaimer when ambiguity is high.

### 7.3 Context-Aware Severity Risk Scoring
Severity is not determined by naive keyword counting. The system:
- **Detects Negations:** Explicit patterns like `"no injury occurred"` or `"without injuries"` neutralize false alarms while appropriately scoring secondary hazards.
- **Assesses Compound Factors:** Escalates scores for high-altitude work, night-shift operations, energized electrical gear, or uncontained hydrocarbons.
- **Categorizes Transparently:**
  - `0 - 39` $\rightarrow$ **LOW:** Minor housekeeping or clerical deviations.
  - `40 - 64` $\rightarrow$ **MEDIUM:** Minor injuries (first aid), valve leaks, procedural deviations.
  - `65 - 84` $\rightarrow$ **HIGH:** Near misses near excavations, hydrocarbon seepage, high voltage proximity.
  - `85 - 100` $\rightarrow$ **CRITICAL:** Fatalities, life-threatening injuries, major explosions, or catastrophic fires.

---

## 8. Evaluation Methodology & Statistical Limitations

### 8.1 Bundled Dataset Verification (N=6)
Using Leave-One-Out (excluding self-retrieval) across the bundled benchmark dataset:
- **Category Classification Accuracy:** $6 / 6$ (100%)
- **Severity Classification Accuracy:** $6 / 6$ (100%)

> [!WARNING]
> **Statistical Disclaimer for Hiring Evaluators:**  
> A sample size of $N=6$ is statistically insufficient to claim generalized machine learning accuracy. Classes are heavily imbalanced (Safety: 3, Environment: 2, ESG Compliance: 1; Critical: 0). Claiming 100% generalization performance from 6 samples would be methodologically flawed. Therefore, the pipeline was subjected to an independent **Unseen Validation Test Suite**.

### 8.2 Curated Unseen Validation Suite (8 Operational Test Cases)

| Test ID | Scenario Description | Expected Category | Pred. Category | Expected Severity | Pred. Severity | Overlap Risk Tags | Pass Status |
|---|---|---|---|---|---|---|---|
| `TEST_001` | Contractor slips on wet floor in inverter room | `safety` | `safety` | `medium` | `medium` | Slip and Fall, Contractor Safety | **PASSED** |
| `TEST_002` | Worker atop 5m solar structure without harness | `safety` | `safety` | `high` | `high` | PPE Non-Compliance | **PASSED** |
| `TEST_003` | Synthetic gear oil leak beneath wind nacelle | `environment` | `environment` | `high` | `high` | Oil Leakage, Equipment Failure | **PASSED** |
| `TEST_004` | Underground cleaning water pipeline rupture | `environment` | `environment` | `medium` | `medium` | Water Leakage | **PASSED** |
| `TEST_005` | Transport truck near unbarricaded trench at night | `safety` | `safety` | `high` | `high` | Near Miss, Vehicle Movement Risk | **PASSED** |
| `TEST_006` | Repeated co-mingling of oily rags with scrap | `esg_compliance` | `esg_compliance` | `low` | `low` | Waste Management, Contractor Safety | **PASSED** |
| `TEST_007` | Major electrical fire & explosion in 33kV switchyard | `safety` | `safety` | `critical` | `critical` | Fire Risk, Electrical Hazard | **PASSED** |
| `TEST_008` | Fatal electrocution during breaker isolation | `safety` | `safety` | `critical` | `critical` | Electrical Hazard, Contractor Safety | **PASSED** |

**Unseen Suite Pass Rate:** **100% (8 / 8 scenarios passed across Category and Severity)**.

---

## 9. API Documentation

The backend exposes fully documented RESTful APIs. Interactive Swagger UI is available at `/docs`.

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the enterprise web analytics dashboard UI. |
| `GET` | `/api/health` | System health, dataset load status, and record counts. |
| `GET` | `/api/demo` | Preserved starter demo endpoint with architectural metadata. |
| `GET` | `/api/incidents` | All historical incidents with full AI analysis outputs. |
| `GET` | `/api/incidents/{id}` | Detailed intelligence report for a specific incident ID. |
| `GET` | `/api/dashboard` | Real-time computed KPIs, distributions, risk matrix, patterns, and insights. |
| `POST` | `/api/analyze` | Ingests a new narrative and executes the full intelligence pipeline. |
| `POST` | `/api/run` | Preserved backward-compatible endpoint for starter queries. |
| `GET` | `/api/evaluation` | Full evaluation report on reference data and 8 unseen test cases. |
| `GET` | `/case_study` | Assignment reference document. |

### Sample `POST /api/analyze` Request & Response

#### Request:
```json
{
  "text": "Oil leakage observed near the wind turbine gearbox during maintenance."
}
```

#### Response:
```json
{
  "input": "Oil leakage observed near the wind turbine gearbox during maintenance.",
  "clean_text": "oil leakage observed near wind turbine gearbox during maintenance",
  "predicted_category": "environment",
  "category_confidence": 0.85,
  "classification_method": "rule_based",
  "classification_explanation": "Decisive domain rule match (score 5.0) based on keywords/phrases: oil leakage, gearbox.",
  "predicted_severity": "high",
  "risk_score": 68,
  "risk_factors": [
    "Substantial hydrocarbon seepage/leakage near rotating equipment"
  ],
  "requires_immediate_attention": true,
  "risk_tags": [
    "Oil Leakage",
    "Equipment Failure"
  ],
  "summary": "Oil seepage was detected in the wind gearbox maintenance bay, which was contained using an on-site spill kit. The event represents an environmental containment and maintenance priority.",
  "structured_summary": {
    "brief": "Oil seepage was detected in the wind gearbox maintenance bay...",
    "identified_hazard": "Hydrocarbon leakage and slip/environmental contamination hazard",
    "possible_contributing_factor": "Possible mechanical seal wear or gasket degradation during maintenance",
    "operational_impact": "Maintenance area containment initiated; oil recovery executed",
    "recommended_action": "Perform torque and seal audit on gearbox, replenish spill kit inventory."
  },
  "similar_incidents": [
    {
      "retrieved_incident_id": "S002",
      "original_narrative": "Oil seepage observed near wind gearbox maintenance bay, contained with spill kit",
      "category": "environment",
      "reference_severity": "high",
      "similarity_score": 0.38,
      "relevance_explanation": "Shared operational terms: gearbox, maintenance, near"
    }
  ],
  "recommendations": {
    "immediate_actions": [
      "URGENT: Escalate incident to Site Head and Corporate EHS Director within 1 hour.",
      "Deploy containment boom / absorbent pads from the spill kit to stop spread.",
      "Isolate gearbox lube-oil lines and tag out equipment if leakage exceeds drip tolerance."
    ],
    "preventive_actions": [
      "Conduct dye-penetrant or torque inspection on gearbox casing seals and oil flanges.",
      "Restock used spill kit materials and dispose of contaminated absorbents via authorized recycler."
    ],
    "long_term_actions": [
      "Implement automated oil-level drop telemetry and condition monitoring for early seal wear detection."
    ],
    "recommendation_reason": "Preventing environmental soil/groundwater contamination and catastrophic rotating equipment failure."
  },
  "limitations": [
    "AI-assisted decision-support recommendation; does not replace mandatory regulatory or safety assessments.",
    "Classification is based on domain heuristic rules and TF-IDF similarity on historical records.",
    "Root cause indications represent possible contributing factors based on narrative evidence, not forensic proof."
  ]
}
```

---

## 10. Local Installation & Execution

### Prerequisites
- Python 3.11, 3.12, 3.13, or 3.14
- Git (optional)

### Setup Steps

1. **Clone or Navigate to the Workspace:**
   ```bash
   cd 05_esg_safety_incident_intelligence_dashboard
   ```

2. **Create and Activate a Virtual Environment (Recommended):**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Automated Test Suite:**
   ```bash
   pytest tests/test_backend.py -v
   ```
   *(All 22 unit, integration, and endpoint tests will execute and pass).*

5. **Start the Application Server:**
   ```bash
   uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the Application:**
   - **Interactive Web Dashboard:** [http://localhost:8000/](http://localhost:8000/)
   - **Interactive API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Alternative ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - **Assignment Case Study:** [http://localhost:8000/case_study](http://localhost:8000/case_study)

---

## 11. Railway Cloud Deployment Guide

The repository is pre-configured for automated continuous deployment on [Railway](https://railway.app/).

### Files Provided for Railway:
- `Procfile`: Declares the web service process: `web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
- `railway.json`: Declares deployment builder (Nixpacks), health-check route (`/api/health`), and restart policies.
- `requirements.txt`: Cleanly pinned production dependencies.

### Step-by-Step Deployment Instructions:

1. **Push to GitHub / GitLab:**
   ```bash
   git init
   git add .
   git commit -m "feat: Greenko ESG & Safety Incident Intelligence Platform"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Log in to your [Railway Dashboard](https://railway.app/).
   - Click **"New Project"** $\rightarrow$ **"Deploy from GitHub repo"**.
   - Select your repository.
   - Railway will automatically detect the Python environment and `Procfile`.
   - The server binds to `0.0.0.0` and reads the assigned `$PORT` environment variable.
   - Railway will monitor the `/api/health` endpoint for zero-downtime deployment.

3. **Verification:**
   - Open your deployed Railway domain (e.g., `https://greenko-ehs-dashboard.up.railway.app/`).
   - The full dashboard UI will load immediately with all features functional.

---

## 12. Assumptions, Limitations & Production-Readiness Gaps

### Assumptions
1. **Domain Context:** Narratives originate from utility-scale solar, wind, and transmission operations where safety precautions and hierarchy of controls apply.
2. **Offline Resilience:** The application is architected to run completely in self-contained environments without relying on third-party SaaS embeddings or internet connectivity.

### Limitations
1. **Corpus Size:** The starter dataset contains 6 records. While supplemented with an 8-case unseen test suite, this is not a substitute for an enterprise database of 10,000+ incident logs.
2. **Lexical Paraphrase Sensitivity:** TF-IDF cosine similarity measures vocabulary and n-gram overlap; heavily metaphorical descriptions with zero overlapping terms require dense semantic embeddings.
3. **Indicative Root-Cause:** AI inferences are categorized as *"possible contributing factors"*; formal EHS incident investigations require on-site forensic analysis.

### Enterprise Production Roadmap
1. **Enterprise LLM / SLM Fine-Tuning:** Fine-tune a lightweight on-premise model (e.g., Llama-3.2-3B or Mistral-7B) using LoRA on Greenko's historical EHS repository.
2. **Vector Database Integration:** Replace in-memory TF-IDF with an on-premise vector store (Qdrant or Chroma) using domain-adapted embeddings (`bge-base` or `all-MiniLM-L6-v2`).
3. **Telemetry & SCADA Ingestion:** Ingest real-time inverter alarms, wind turbine vibration sensors, and water flow telemetry directly into the incident scoring pipeline.
4. **Mobile Field Reporting App:** Provide an offline-first mobile PWA for site engineers with voice-to-text narrative recording.

---

## 13. Summary of Deliverables

- [x] Complete, tested Python backend with modular architecture (`backend/services/`)
- [x] Preprocessing, classification, severity scoring, RAG retrieval, summarization, and recommendation modules
- [x] Professional Greenko-themed analytics dashboard UI with native SVG charts (`frontend/index.html`)
- [x] Full suite of 22 automated tests with 100% pass rate (`tests/test_backend.py`)
- [x] Evaluation on bundled data and 8 unseen operational scenarios (`/api/evaluation`)
- [x] Preserved starter endpoints (`/api/demo`, `/api/run`) with full backward compatibility
- [x] Complete deployment readiness configuration for Railway (`Procfile`, `railway.json`)
