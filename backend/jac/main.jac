# Main entry point for PublicLens

import uuid;
import datetime;

# Node definitions
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

edge EscalatesTo {}

edge RelatedTo {
    has similarity_score: float;
}

edge HandledBy {}

# Walker definitions
walker IntakeAgent {
    has report_data: dict;

    can validate_and_create with `root entry {
        print("IntakeAgent: validating and creating report");
        
        # Create report node
        new_report = Report(
            id=str(uuid.uuid4()),
            title=self.report_data["title"],
            description=self.report_data["description"],
            category="pending",
            urgency="medium",
            entities="{}",
            confidence=0.5,
            status="submitted",
            submitted_at=str(datetime.datetime.now()),
            reporter=Reporter(
                id=str(uuid.uuid4()),
                name=self.report_data["name"],
                email=self.report_data["email"],
                is_anonymous=(self.report_data["name"] == "")
            ),
            embedding="[]"
        );
        
        # Connect to root
        root ++> new_report;
        
        print("Report created with ID:", new_report.id);
        report {"report_id": new_report.id, "status": "submitted"};
    }
}

walker ClassifierAgent {
    has report_data: dict;
    has report: Report;

    can classify with Report entry {
        print("ClassifierAgent: classifying report");
        # Placeholder: classify
        print("Report classified");
    }
}

walker DuplicateDetectorAgent {
    has report: Report;

    can detect with Report entry {
        print("DuplicateDetectorAgent: checking for duplicates");
        # Placeholder: detect
        print("Duplicates checked");
    }
}

walker RouterAgent {
    has report: Report;

    can route with Report entry {
        print("RouterAgent: routing report");
        # Placeholder: route
        print("Report routed");
    }
}

with entry {
    # Create sample organisations
    gov_org = Organisation(
        name="Sample Government Agency",
        type="government",
        contact_email="reports@gov.example.com",
        contact_api="",
        facilities="[]"
    );

    utility_org = Organisation(
        name="Sample Utility Company",
        type="utility",
        contact_email="support@utility.example.com",
        contact_api="",
        facilities="[]"
    );

    # Connect to root
    root ++> gov_org;
    root ++> utility_org;

    # Create sample policies
    routing_policy = Policy(name="auto_routing", rules="{}");

    root ++> routing_policy;

    print("PublicLens OSP graph initialized");
    print("Organisations:", gov_org.name, utility_org.name);
}