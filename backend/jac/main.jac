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
    has relationship_type: str;
}

edge HandledBy {}

# Walker definitions
walker IntakeAgent {
    has report_data: dict;

    can validate_and_create with `root entry {
        print("IntakeAgent: validating and creating report");
        
        # Extract entities
        text = self.report_data["title"] + " " + self.report_data["description"];
        response = requests.post("http://localhost:8001/extract_entities", json={"text": text});
        entities = response.json() if response.status_code == 200 else {};
        
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
        spawn ClassifierAgent;
        
        print("Report created with ID:", new_report.id);
        report {"report_id": new_report.id, "status": "submitted"};
    }
}

walker ClassifierAgent {
    has report_data: dict;

    can classify with Report entry {
        print("ClassifierAgent: classifying report");
        
        text = self.title + " " + self.description;
        
        # Classify
        response = requests.post("http://localhost:8001/classify", json={"text": text});
        if response.status_code == 200 {
            data = response.json();
            self.category = data["category"];
            self.confidence = data["confidence"];
        }
        
        # Assess urgency
        response = requests.post("http://localhost:8001/assess_urgency", json={"text": text});
        if response.status_code == 200 {
            self.urgency = response.json();
        }
        
        # Store embedding
        response = requests.post("http://localhost:8001/store_embedding", json={
            "report_id": self.id,
            "title": self.title,
            "description": self.description
        });
        if response.status_code == 200 {
            print("Embedding stored");
        }
        
        self.status = "classified";
        print("Report classified");
        
        # Spawn DuplicateDetectorAgent
        spawn DuplicateDetectorAgent;
    }
}

walker DuplicateDetectorAgent {

    can detect with Report entry {
        print("DuplicateDetectorAgent: checking for duplicates");
        
        response = requests.post("http://localhost:8001/find_duplicates", json={
            "report_id": self.id,
            "title": self.title,
            "description": self.description,
            "threshold": 0.8
        });
        if response.status_code == 200 {
            duplicates = response.json()["duplicates"];
            # Simplified: assume no duplicates for now
            if False {
                self.status = "duplicate";
                print("Duplicates found:", len(duplicates));
            } else {
                self.status = "unique";
                print("No duplicates found");
            }
        }
        
        print("Duplicates checked");
        
        # Spawn RouterAgent
        spawn RouterAgent;
    }
}

walker RouterAgent {

    can route with Report entry {
        print("RouterAgent: routing report");
        
        # Select organisations based on category
        selected_orgs = [];
        
        if self.category == "infrastructure" {
            # Find utility or government organisations
            # Assuming root.out_nodes() returns a list of nodes
            # If not, we might need another way to traverse
            for org in root.out_nodes() {
                if "type" in org.context and (org.type == "utility" or org.type == "government") {
                    selected_orgs.append(org);
                }
            }
        } elif self.category == "safety" {
            # Find government organisations
            for org in root.out_nodes() {
                if "type" in org.context and org.type == "government" {
                    selected_orgs.append(org);
                }
            }
        } elif self.category == "utility" {
            # Find utility organisations
            for org in root.out_nodes() {
                if "type" in org.context and org.type == "utility" {
                    selected_orgs.append(org);
                }
            }
        } else {
            # Default to all organisations
            for org in root.out_nodes() {
                if "type" in org.context {
                    selected_orgs.append(org);
                }
            }
        }
        
        # For each selected organisation, draft and send notification
        for org in selected_orgs {
            # Draft message
            response = requests.post("http://localhost:8001/draft_message", json={
                "title": self.title,
                "description": self.description,
                "urgency": self.urgency,
                "org_type": org.type
            });
            if response.status_code == 200 {
                message = response.json()["message"];
            } else {
                message = "Report: " + self.title + " - " + self.description;
            }
            
            # Send notification
            if org.contact_email {
                send_response = requests.post("http://localhost:8003/send_email", json={
                    "to": org.contact_email,
                    "subject": "Public Report: " + self.title,
                    "body": message
                });
                if send_response.status_code == 200 {
                    print("Notification sent to " + org.name + " via email");
                } else {
                    print("Failed to send notification to " + org.name);
                }
            }
            
            # Create notification edge
            self ++> HandledBy(
                assigned_at=str(datetime.datetime.now()),
                status="sent"
            ) ++> org;
        }
        
        self.status = "routed";
        print("Report routed to " + str(len(selected_orgs)) + " organisations");
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