# Main entry point for PublicLens

import uuid;
import datetime;
import requests;
import json;

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
        
        # Extract entities
        text = self.report_data["title"] + " " + self.report_data["description"];
        try {
            response = requests.post("http://localhost:8001/extract_entities", json={"text": text});
            entities = response.json() if response.status_code == 200 else {};
        } catch {
            entities = {};
        }
        
        # Create report node
        new_report = Report(
            id=str(uuid.uuid4()),
            title=self.report_data["title"],
            description=self.report_data["description"],
            category="pending",
            urgency="medium",
            entities=json.dumps(entities),
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
        
        # Spawn ClassifierAgent
        spawn ClassifierAgent(report=new_report) --> new_report;
        
        print("Report created with ID:", new_report.id);
        report {"report_id": new_report.id, "status": "submitted"};
    }
}

walker ClassifierAgent {
    has report_data: dict;
    has report: Report;

    can classify with Report entry {
        print("ClassifierAgent: classifying report");
        
        text = self.report.title + " " + self.report.description;
        
        # Classify
        try {
            response = requests.post("http://localhost:8001/classify", json={"text": text});
            if response.status_code == 200 {
                data = response.json();
                self.report.category = data["category"];
                self.report.confidence = data["confidence"];
            }
        } catch {
            print("Classification failed");
        }
        
        # Assess urgency
        try {
            response = requests.post("http://localhost:8001/assess_urgency", json={"text": text});
            if response.status_code == 200 {
                self.report.urgency = response.json();
            }
        } catch {
            print("Urgency assessment failed");
        }
        
        # Store embedding
        try {
            response = requests.post("http://localhost:8001/store_embedding", json={
                "report_id": self.report.id,
                "title": self.report.title,
                "description": self.report.description
            });
            if response.status_code == 200 {
                print("Embedding stored");
            }
        } catch {
            print("Embedding storage failed");
        }
        
        self.report.status = "classified";
        print("Report classified");
        
        # Spawn DuplicateDetectorAgent
        spawn DuplicateDetectorAgent(report=self.report) --> self.report;
    }
}

walker DuplicateDetectorAgent {
    has report: Report;

    can detect with Report entry {
        print("DuplicateDetectorAgent: checking for duplicates");
        
        try {
            response = requests.post("http://localhost:8001/find_duplicates", json={
                "report_id": self.report.id,
                "title": self.report.title,
                "description": self.report.description,
                "threshold": 0.8
            });
            if response.status_code == 200 {
                duplicates = response.json()["duplicates"];
                for dup in duplicates {
                    # Find the duplicate report node
                    dup_report = root --> Report(id=dup["report_id"]) --> Report;
                    if dup_report {
                        self.report --> RelatedTo(similarity_score=dup["_additional"]["certainty"], relationship_type="duplicate") --> dup_report;
                    }
                }
                if duplicates {
                    self.report.status = "duplicate";
                    print("Duplicates found:", len(duplicates));
                } else {
                    self.report.status = "unique";
                    print("No duplicates found");
                }
            }
        } catch {
            print("Duplicate detection failed");
            self.report.status = "checked";
        }
        
        print("Duplicates checked");
        
        # Spawn RouterAgent
        spawn RouterAgent(report=self.report) --> self.report;
    }
}

walker RouterAgent {
    has report: Report;

    can route with Report entry {
        print("RouterAgent: routing report");
        
        # Placeholder: route based on category, urgency, etc.
        # For now, just mark as routed
        self.report.status = "routed";
        
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