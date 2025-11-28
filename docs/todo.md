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
- [ ] Implement NLP service for entity extraction
- [ ] Add classification and urgency assessment
- [ ] Integrate vector database for embeddings
- [ ] Implement duplicate detection logic
- [ ] Add confidence scoring

## Phase 3: Routing and Notifications
- [ ] Implement organisation selection logic
- [ ] Add message drafting with byLLM
- [ ] Integrate SMTP/API/SMS connectors
- [ ] Add delivery status tracking

## Phase 4: Dashboards and UI
- [ ] Create organisation dashboard
- [ ] Add public transparency view
- [ ] Implement privacy controls and redaction
- [ ] Add analytics and metrics display

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