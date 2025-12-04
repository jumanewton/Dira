# PublicLens - Feedback and Issue-Tracking Platform

## Overview
PublicLens is a feedback and issue-tracking platform for government organisations and public utilities. It uses Jaseci's Jac language with OSP graphs and byLLM agents to process, classify, and route public reports efficiently.

## Features
- Anonymous or named report submissions
- NLP pipeline for entity extraction, classification, and urgency assessment
- Semantic duplicate detection via vector database
- OSP graph for modeling organizations, reports, and workflows
- byLLM agents for summarization, routing, and auto-drafting
- Dashboard for organizations and public transparency view

## Architecture
- **Backend**: Jac (core) with OSP graphs and byLLM agents
- **Frontend**: React with Jac Client for walker calls
- **NLP Service**: Python microservice for entity extraction and classification
- **Vector DB**: Weaviate for semantic search and duplicate detection
- **Storage**: MongoDB for metadata
- **Integrations**: SMTP/API/SMS for routing

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

**Optional Variables:**
- `NLP_PORT`, `NOTIFICATION_PORT`: Service ports (defaults: 8001, 8003)
- `SMTP_SERVER`, `SMTP_PORT`: Email server settings

Edit `.env` with your configuration before running services.

### 2. Install Jaseci
```bash
pip install jaseci
```

### 3. Install Python Dependencies
```bash
cd backend/python
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 5. Set up Vector Database
- Install Weaviate locally or use cloud instance
- Configure connection in `.env` (WEAVIATE_URL)

### 6. Download ML Models
The first run will automatically download models from Hugging Face:
- **Gemini 3 Pro (Preview)**: Used for text classification, urgency assessment, and message drafting (requires API key).
- **SentenceTransformers** (`sentence-transformers/all-MiniLM-L6-v2`): Generates embeddings for semantic search (cached locally).

Models are cached in `HUGGINGFACE_CACHE_DIR` (default: `./models_cache`).

**Note**: First run may take time to download the embedding model. Subsequent runs will use cached models.

### 7. Run Services
Start services in separate terminals:

**Weaviate Vector DB** (port 8080):
```bash
docker compose -f docker/docker-compose.yml up -d weaviate
```

**NLP Service** (port 8001):
```bash
cd backend/python
# Ensure GEMINI_API_KEY is set in .env
python nlp_service.py
```

**Notification Service** (port 8003):
```bash
cd backend/python
python notification_service.py
```

**Jaseci Backend** (port 8002):
```bash
cd backend/jac
chmod +x serve.sh
./serve.sh
```

**Seed Data** (Important for Demo):
Populate the graph with sample reports and create the admin user.
```bash
cd backend/python
python seed_data.py
```

**Frontend** (port 3000):
```bash
cd frontend
npm start
```
The frontend is configured to automatically log in as the admin user for demonstration purposes.

## Demo Credentials
The system uses a default admin account for the demo:
- **Username**: `admin@publiclens.com`
- **Password**: `password123`

Features include:
- Report submission form with anonymous option
- Organization dashboard for managing assigned reports
- Public transparency view of resolved issues
- Analytics dashboard with metrics and charts
- Privacy controls with automatic data redaction

## Current Status
- ✅ Jac OSP graph with nodes (Organisation, Report, etc.) and edges
- ✅ Basic multi-agent walkers (IntakeAgent, ClassifierAgent, DuplicateDetectorAgent, RouterAgent)
- ✅ Graph initialization with sample data
- ✅ NLP service with entity extraction, classification, and message drafting
- ✅ Vector database integration with Weaviate
- ✅ Duplicate detection using semantic search
- ✅ Automated routing and notification system
- ✅ Environment configuration with .env support
- ✅ Organization dashboard with report management
- ✅ Public transparency view with resolved reports
- ✅ Privacy controls and data redaction
- ✅ Analytics dashboard with metrics and insights
- ✅ Frontend Jac Client integration (Auto-login enabled)

## Project Structure
```
publiclens/
├── backend/
│   ├── jac/          # Jac source files
│   └── python/       # Python microservices
├── frontend/         # React app
├── vector_db/        # Vector DB config
├── docker/           # Docker files
├── docs/             # Documentation
└── tests/            # Test files
```


## License
MIT