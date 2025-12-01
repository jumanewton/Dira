# PublicLens Development Todo List

## Phase 1: Setup and Core OSP Graph
- [x] Create folder structure
- [x] Set up README with setup instructions
- [x] Define OSP graph models (nodes and edges)
- [x] Implement core walkers (IntakeAgent, ClassifierAgent, DuplicateDetectorAgent, RouterAgent)
- [x] Create main.jac entry point
- [x] Set up basic React frontend with submission form
- [x] Configure Docker for deployment
- [x] Install and test Jaseci locally
- [x] Test Jac OSP graph initialization

## Phase 2: NLP and Vector DB Integration
- [x] Implement NLP service for entity extraction
- [x] Add classification and urgency assessment
- [x] Integrate vector database for embeddings
- [x] Implement duplicate detection logic
- [x] Add confidence scoring

## Phase 3: Routing and Notifications
- [x] Implement organisation selection logic
- [x] Add message drafting with byLLM
- [x] Integrate SMTP/API/SMS connectors
- [x] Add delivery status tracking

## Phase 4: Dashboards and UI
- [x] Create organisation dashboard
- [x] Add public transparency view
- [x] Implement privacy controls and redaction
- [x] Add analytics and metrics display

## Phase 5: Testing and Evaluation
- [ ] Create seed dataset
- [ ] Implement evaluation metrics
- [ ] Test end-to-end workflow
- [ ] Record demo video
- [ ] Prepare GitHub repository

## Phase 6: Deployment and Polish
- [ ] Deploy to cloud (Render/GCP/Azure)
- [ ] Add CI/CD with GitHub Actions
- [ ] Final testing and bug fixes
- [ ] Documentation updates