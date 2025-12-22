# Dira - Feedback and Issue-Tracking Platform

## Overview
Dira is a feedback and issue-tracking platform for government organisations and public utilities. It uses Jaseci's Jac language with OSP graphs and byLLM agents to process, classify, and route public reports efficiently.

## Features
- **Multi-Agent System**: Intake, Classifier, Duplicate Detector, and Router agents working in concert.
- **Native byLLM Integration**: Uses Jac's `by llm` capability for classification, urgency assessment, and message drafting.
- **OSP Graph**: Models organizations, reports, and facilities spatially for intelligent routing.
- **Semantic Duplicate Detection**: Uses vector embeddings to identify and group similar reports.
- **Jac Client Frontend**: React application integrated with `jac-client` for seamless backend communication.
- **Transparency**: Public dashboards and organization-specific views.

## Architecture
- **Backend**: Jac (core) with OSP graphs and native `byLLM` agents.
- **Frontend**: React using `jac-client` library.
- **NLP Service**: Python microservice for entity extraction and vector embeddings.
- **Vector DB**: Weaviate for semantic search.
- **Integrations**: SMTP/API/SMS for routing.

See [Architecture Diagram](architecture.md) for agent interaction details.

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (optional for deployment)

### 1. Environment Configuration
Copy the `.env` file and configure your settings:
```bash
cp .env .env.local  # Optional: for local overrides
```

**Required Environment Variables:**
- `GEMINI_API_KEY`: Google Gemini API key for NLP tasks
- `SMTP_USERNAME` & `SMTP_PASSWORD`: Email credentials for notifications
- `WEAVIATE_URL`: Vector database connection
- `HUGGINGFACE_CACHE_DIR`: Directory for ML model caching

### 2. Install Dependencies

**Backend (Jac & Python):**
```bash
pip install jaseci
cd backend/python
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 3. Run Services
Start services in separate terminals:

**1. Weaviate Vector DB** (port 8080):
```bash
docker compose -f docker/docker-compose.yml up -d weaviate
```

**2. NLP Service** (port 8001):
```bash
cd backend/python
python nlp_service.py
```

**3. Notification Service** (port 8003):
```bash
cd backend/python
python notification_service.py
```

**4. Jaseci Backend** (port 8002):
```bash
cd backend/jac
jac serve main.jac --port 8002
```

**5. Frontend** (port 3000):
```bash
cd frontend
npm start
```

### 4. Load Seed Data
To populate the system with realistic demo data:
```bash
python load_seed_data.py
```

## Documentation
- [Agent Interaction Diagram](architecture.md)
- [Evaluation Plan](evaluation_plan.md)
- [Missing Requirements Analysis](missing_requirements.md)

## Evaluation
The project includes an evaluation plan covering:
- Classification Accuracy
- Duplicate Detection Precision
- Routing Latency
- Qualitative Message Quality

See [Evaluation Plan](evaluation_plan.md) for details.
