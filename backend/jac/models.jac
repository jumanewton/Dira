node Organisation {
    has name: str;
    has type: str;  # e.g., government, utility
    has contact_email: str;
    has contact_api: str;  # optional API endpoint
    has facilities: str;  # list as json string
}

node Facility {
    has name: str;
    has location: str;
    has organisation: Organisation;
}

node Report {
    has id: str;
    has title: str;
    has description: str;
    has category: str;  # classified category
    has urgency: str;   # low, medium, high
    has entities: str; # extracted entities (org, location, etc.) as json string
    has confidence: float;
    has status: str;  # submitted, routed, resolved
    has submitted_at: str;
    has reporter: Reporter;
    has embedding: str;  # vector for duplicate detection as json string
}

node Reporter {
    has id: str;
    has name: str;  # optional for anonymous
    has email: str;
    has is_anonymous: bool;
}

node Agent {
    has name: str;
    has type: str;  # intake, classifier, duplicate_detector, router
}

node Policy {
    has name: str;
    has rules: str;  # routing rules, redaction rules as json string
}

# Edges
edge ReportsOf {
    has submitted_at: str;
}

with entry {
    print("Models loaded");
}

edge EscalatesTo {
    has reason: str;
    has priority: int = 1;
}

edge RelatedTo {
    has similarity_score: float;
    has relationship_type: str = "duplicate";  # duplicate, similar
}

edge HandledBy {
    has assigned_at: str;
    has status: str = "assigned";
}

edge Manages {
    # organisation manages facilities
}

edge BelongsTo {
    # reporter belongs to organisation? or general
}