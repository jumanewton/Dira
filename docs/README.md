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

### 1. Install Jaseci
```bash
pip install jaseci
```

### 2. Install Python Dependencies
```bash
cd backend/python
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 4. Set up Vector Database
- Install Weaviate or use cloud instance
- Configure connection in `vector_db/config.py`

### 5. Run Backend
```bash
cd backend/jac
jac run main.jac
```
This initializes the OSP graph with sample organizations and policies.

### 6. Run Frontend (Placeholder)
```bash
cd frontend
npm start
```
Note: Jac Client integration pending.

### 7. Run NLP Service
```bash
cd backend/python
python nlp_service.py
```

## Current Status
- ✅ Jac OSP graph with nodes (Organisation, Report, etc.) and edges
- ✅ Basic multi-agent walkers (IntakeAgent, ClassifierAgent, etc.)
- ✅ Graph initialization with sample data
- 🔄 byLLM integration (simplified placeholders due to compilation issues)
- 🔄 Frontend Jac Client integration
- 🔄 NLP and vector DB services

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