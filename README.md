# Asha-Mind AI Caregiver & Dementia Assistance Backend

Mindner is a production-ready, backend platform designed for dementia care coordination, cognitive therapy games, multi-domain cognitive trajectory analysis, adaptive difficulty calibration, and caregiver alert automation.

---

## 🏛️ Architecture Overview

The backend is built following a clean, layered architecture with unidirectional dependencies:

```text
API Routers (/api/v1/*)
      ↓
Pydantic Schemas (Input/Output Validation)
      ↓
Business Logic Services (Scoring, Adaptive, Baseline, Analytics, Alerts, Recommendations)
      ↓
Database Access Layer (Queries & Safe Context Managers)
      ↓
SQLite Engine (database/caregiver.db)
```

---

## 📂 Project Structure

```text
mindner/
├── .env                         # Local environment configuration (ignored by git)
├── .env.example                 # Safe environment configuration template
├── .gitignore                   # Production gitignore rules
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point & lifespan startup
│   │
│   ├── api/                     # REST API route handlers (/api/v1)
│   │   ├── __init__.py          # Centralized router registry
│   │   ├── health.py            # Health check & SQLite table auto-discovery
│   │   ├── patients.py          # Patient registration, updates & caregiver queries
│   │   ├── caregivers.py        # Caregiver management & patient linking
│   │   ├── games.py             # Cognitive game catalogue & specifications
│   │   ├── sessions.py          # Game session recording & score triggering
│   │   ├── progress.py          # Comprehensive patient progress reports
│   │   ├── analytics.py         # Cognitive domain metrics & score calculation
│   │   ├── adaptive.py          # Dynamic difficulty calibration
│   │   ├── recommendations.py   # AI assessment and care recommendations
│   │   ├── alerts.py            # Symptoms, emergency alerts, and reminders
│   │   └── sync.py              # Offline device session ingestion & audit logs
│   │
│   ├── core/                    # Core configuration & platform security
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic Settings management
│   │   ├── logging_config.py    # Structured console logging
│   │   └── security.py          # Cryptographic hashing & auth placeholders
│   │
│   ├── database/                # Database connections and auto-discovery
│   │   ├── __init__.py
│   │   ├── connection.py        # Safe connection context managers & table discovery
│   │   ├── models.py            # Entity dataclass definitions
│   │   ├── queries.py           # Parameterized SQL query catalogue
│   │   └── init_db.py           # Startup initialization & diagnostic inspector
│   │
│   ├── schemas/                 # Pydantic validation models
│   │   ├── __init__.py
│   │   ├── patient.py
│   │   ├── caregiver.py
│   │   ├── game.py
│   │   ├── session.py
│   │   ├── attempt.py
│   │   ├── progress.py
│   │   ├── scoring.py
│   │   ├── adaptive.py
│   │   ├── recommendation.py
│   │   └── alert.py
│   │
│   ├── services/                # Encapsulated business logic services
│   │   ├── __init__.py
│   │   ├── scoring_service.py   # Multi-factor cognitive scoring
│   │   ├── adaptive_service.py  # Adaptive challenge level tuning
│   │   ├── baseline_service.py  # Baseline calibration & decline detection
│   │   ├── analytics_service.py # Domain aggregation & platform statistics
│   │   ├── recommendation_service.py # AI clinical recommendation synthesis
│   │   └── alert_service.py     # Severity-based caregiver alerts & reminders
│   │
│   └── utils/                   # Shared utility helpers
│       ├── __init__.py
│       ├── validators.py        # Format and range validators
│       ├── datetime_utils.py    # UTC ISO timestamp helpers
│       └── response.py          # Standardized response envelopes
│
├── database/
│   ├── caregiver.db             # Primary SQLite application database
│   ├── schema.sql               # SQLite DDL defining 13 relational tables
│   └── seed.py                  # Seed script with realistic clinical test data
│
└── tests/                       # Pytest test suite
    ├── __init__.py
    ├── test_health.py
    ├── test_patients.py
    ├── test_caregivers.py
    ├── test_games.py
    ├── test_sessions.py
    ├── test_progress.py
    ├── test_adaptive.py
    └── test_analytics.py
```

---

## 🗄️ Database Model (13 Tables)

| Table | Purpose |
| :--- | :--- |
| `patients` | Dementia patient profiles, diagnosis date, stage, and baseline score |
| `caregivers` | Caregiver contact details and medical/family roles |
| `patient_caregivers` | Many-to-many relationship mapping between patients and caregivers |
| `cognitive_games` | Registered therapy games (memory, recognition, problem solving, routines) |
| `game_sessions` | Recorded game sessions (duration, score, accuracy, reaction time) |
| `cognitive_scores` | Multi-domain normalized scores and baseline deviations |
| `ai_assessments` | Clinical cognitive assessments, trend analysis, and risk scoring |
| `ai_recommendations` | Actionable recommendations for caregivers and patients |
| `reminders` | Scheduled reminders for medication, hydration, and games |
| `symptoms` | Logged behavioral/physical symptoms with severity tracking |
| `alerts` | Notification alerts (critical severity automatic triggers) |
| `daily_activity` | Daily summaries of cognitive exercise adherence and scores |
| `sync_log` | Audit logs for offline device data synchronizations |

---

## 🚀 Quick Start

### 1. Setup Virtual Environment

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database

```bash
python database/seed.py
```

This creates `database/demo_caregiver.db` from `database/schema.sql` and inserts
demo records into all application tables. To recreate the demo database from
scratch, run:

```bash
python database/seed.py --reset
```

To seed a specific database path, use `--db`. Use `--reset` only when you
intentionally want to delete and recreate that database:

```bash
python database/seed.py --db database/caregiver.db --reset
```

### 4. Run the Backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Access Interactive Documentation

- **Swagger UI**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
- **ReDoc**: [http://127.0.0.1:8000/api/v1/redoc](http://127.0.0.1:8000/api/v1/redoc)
- **Health Check**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 🧪 Running Tests

## Execute the automated test suite

```bash

python -m pytest
```

## 📈 XGBoost Experiment

Train and tune a binary XGBoost classifier on reproducible random data, then save
accuracy, ROC/AUC, and confusion-matrix plots:

```bash
python scripts/train_xgboost.py
```

The combined report is saved to `artifacts/xgboost_evaluation.png`, and the
metrics and best parameters are saved automatically to
`artifacts/xgboost_metrics.json`. Use `--output path/to/report.png` or
`--metrics-output path/to/metrics.json` to choose different output paths.

## PowerShell usage

- Start the app: .\run.ps1
- Run the tests: .\run.ps1 -Mode test
