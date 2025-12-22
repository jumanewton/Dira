# Agent Interaction Diagram

This diagram illustrates the multi-agent workflow in Dira, showing how a report is processed from submission to routing.

```mermaid
sequenceDiagram
    participant User
    participant IntakeAgent
    participant ClassifierAgent
    participant DuplicateDetectorAgent
    participant RouterAgent
    participant ExternalServices as External Services (VectorDB/Email)

    User->>IntakeAgent: Submit Report (Title, Desc)
    activate IntakeAgent
    IntakeAgent->>IntakeAgent: Create Report Node
    IntakeAgent->>IntakeAgent: Create Reporter Node
    IntakeAgent->>ClassifierAgent: Spawn(Report)
    deactivate IntakeAgent
    
    activate ClassifierAgent
    ClassifierAgent->>ClassifierAgent: byLLM: Classify Category
    ClassifierAgent->>ClassifierAgent: byLLM: Assess Urgency
    ClassifierAgent->>ExternalServices: Store Embedding
    ClassifierAgent->>DuplicateDetectorAgent: Spawn(Report)
    deactivate ClassifierAgent

    activate DuplicateDetectorAgent
    DuplicateDetectorAgent->>ExternalServices: Query Vector DB
    ExternalServices-->>DuplicateDetectorAgent: Return Similar Reports
    
    alt Duplicate Found
        DuplicateDetectorAgent->>DuplicateDetectorAgent: Mark Status = "duplicate"
        DuplicateDetectorAgent->>RouterAgent: Spawn(Report)
    else Unique Report
        DuplicateDetectorAgent->>DuplicateDetectorAgent: Mark Status = "unique"
        DuplicateDetectorAgent->>RouterAgent: Spawn(Report)
    end
    deactivate DuplicateDetectorAgent

    activate RouterAgent
    RouterAgent->>RouterAgent: Check Status
    
    alt Status is Duplicate
        RouterAgent->>RouterAgent: Disengage
    else Status is Unique
        RouterAgent->>RouterAgent: Traverse Graph (Find Org)
        loop For Each Selected Org
            RouterAgent->>RouterAgent: byLLM: Draft Notification
            RouterAgent->>ExternalServices: Send Email
            RouterAgent->>RouterAgent: Create 'HandledBy' Edge
        end
        RouterAgent->>RouterAgent: Mark Status = "routed"
    end
    deactivate RouterAgent
```

## Agent Responsibilities

| Agent | Responsibility | Triggers |
|-------|----------------|----------|
| **IntakeAgent** | Validates input, creates graph nodes, initializes report state. | User submission via API/Frontend. |
| **ClassifierAgent** | Uses `byLLM` to determine category and urgency. Stores vector embeddings. | Spawning by `IntakeAgent`. |
| **DuplicateDetectorAgent** | Queries vector database to find semantic duplicates. Updates status. | Spawning by `ClassifierAgent`. |
| **RouterAgent** | Traverses OSP graph to find relevant organizations. Drafts messages via `byLLM` and sends notifications. | Spawning by `DuplicateDetectorAgent`. |
