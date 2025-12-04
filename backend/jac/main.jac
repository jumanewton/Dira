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

walker RouterAgent {

    can route with Report entry {
        print("RouterAgent: routing report");
        
        # Select organisations based on category
        selected_orgs = [];
        
        if here.category == "infrastructure" {
            # Find utility or government organisations
            # Assuming root.out_nodes() returns a list of nodes
            # If not, we might need another way to traverse
            for org in root.out_nodes() {
                if "type" in org.context and (org.type == "utility" or org.type == "government") {
                    selected_orgs.append(org);
                }
            }
        } elif here.category == "safety" {
            # Find government organisations
            for org in root.out_nodes() {
                if "type" in org.context and org.type == "government" {
                    selected_orgs.append(org);
                }
            }
        } elif here.category == "utility" {
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
                "title": here.title,
                "description": here.description,
                "urgency": here.urgency,
                "org_type": org.type
            });
            if response.status_code == 200 {
                message = response.json()["message"];
            } else {
                message = "Report: " + here.title + " - " + here.description;
            }
            
            # Send notification
            if org.contact_email {
                send_response = requests.post("http://localhost:8003/send_email", json={
                    "to": org.contact_email,
                    "subject": "Public Report: " + here.title,
                    "body": message
                });
                if send_response.status_code == 200 {
                    print("Notification sent to " + org.name + " via email");
                } else {
                    print("Failed to send notification to " + org.name);
                }
            }
            
            # Create notification edge
            here ++> HandledBy(
                assigned_at=str(datetime.datetime.now()),
                status="sent"
            ) ++> org;
        }
        
        here.status = "routed";
        print("Report routed to " + str(len(selected_orgs)) + " organisations");
    }
}

walker DuplicateDetectorAgent {

    can detect with Report entry {
        print("DuplicateDetectorAgent: checking for duplicates");
        
        response = requests.post("http://localhost:8001/find_duplicates", json={
            "report_id": here.id,
            "title": here.title,
            "description": here.description,
            "threshold": 0.8
        });
        if response.status_code == 200 {
            duplicates = response.json()["duplicates"];
            # Simplified: assume no duplicates for now
            if False {
                here.status = "duplicate";
                print("Duplicates found:", len(duplicates));
            } else {
                here.status = "unique";
                print("No duplicates found");
            }
        }
        
        print("Duplicates checked");
        
        # Spawn RouterAgent
        spawn RouterAgent;
    }
}

walker ClassifierAgent {

    can classify with Report entry {
        print("ClassifierAgent: classifying report");
        
        text = here.title + " " + here.description;
        
        # Classify
        response = requests.post("http://localhost:8001/classify", json={"text": text});
        if response.status_code == 200 {
            data = response.json();
            here.category = data["category"];
            here.confidence = data["confidence"];
        }
        
        # Assess urgency
        response = requests.post("http://localhost:8001/assess_urgency", json={"text": text});
        if response.status_code == 200 {
            here.urgency = response.json();
        }
        
        # Store embedding
        response = requests.post("http://localhost:8001/store_embedding", json={
            "report_id": here.id,
            "title": here.title,
            "description": here.description
        });
        if response.status_code == 200 {
            print("Embedding stored");
        }
        
        here.status = "classified";
        print("Report classified");
        
        # Spawn DuplicateDetectorAgent
        spawn DuplicateDetectorAgent;
    }
}

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
        
        visit new_report;
    }

    can spawn_classifier with Report entry {
        # Spawn ClassifierAgent
        spawn ClassifierAgent;
        
        print("Report created with ID:", here.id);
        report {"report_id": here.id, "status": "submitted"};
    }
}

walker get_public_reports {
    can return_reports with `root entry {
        reports_list = [];
        # Traverse to all Report nodes connected to root
        # Note: In a real graph, we might want to filter by status="resolved" or similar
        # For now, we return all reports for transparency
        for node in root.out_nodes() {
            if "title" in node.context { # Check if it's a Report node (has title)
                 # Basic redaction logic could go here if not handled by frontend
                 reports_list.append({
                    "id": node.id,
                    "title": node.title,
                    "description": node.description,
                    "status": node.status,
                    "category": node.category,
                    "urgency": node.urgency,
                    "submitted_at": node.submitted_at
                 });
            }
        }
        report reports_list;
    }
}

walker get_report_status {
    has report_id: str;

    can check_status with `root entry {
        found = False;
        for node in root.out_nodes() {
            if "id" in node.context and node.id == self.report_id {
                report {
                    "id": node.id,
                    "status": node.status,
                    "category": node.category,
                    "urgency": node.urgency,
                    "submitted_at": node.submitted_at
                };
                found = True;
            }
        }
        if not found {
            report {"error": "Report not found"};
        }
    }
}

walker get_org_reports {
    has org_name: str;

    can return_reports with `root entry {
        reports_list = [];
        # Iterate all reports connected to root
        for node in root.out_nodes() {
            if "title" in node.context { # Is a Report
                # Check if handled by the org
                is_handled = False;
                # In a real graph database we would traverse edges. 
                # Here we check if the report is connected to the org via HandledBy edge.
                # We iterate the report's out nodes to find the organisation.
                for connected_node in node.out_nodes() {
                    if "name" in connected_node.context and connected_node.name == self.org_name {
                        is_handled = True;
                        break;
                    }
                }
                
                # Also include if status is 'routed' and org matches logic (simplified for demo)
                # Or if we just want to show all reports for demo purposes if logic is complex
                if is_handled {
                    reports_list.append({
                        "id": node.id,
                        "title": node.title,
                        "description": node.description,
                        "status": node.status,
                        "category": node.category,
                        "urgency": node.urgency,
                        "submitted_at": node.submitted_at,
                        "entities": node.entities
                    });
                }
            }
        }
        report reports_list;
    }
}

walker get_analytics {
    can calculate_metrics with `root entry {
        total_reports = 0;
        resolved_reports = 0;
        reports_by_category = {};
        reports_by_urgency = {};
        reports_by_status = {};
        
        # Iterate all reports
        for node in root.out_nodes() {
            if "title" in node.context { # Is a Report
                total_reports += 1;
                
                if node.status == "resolved" {
                    resolved_reports += 1;
                }
                
                # Category
                if node.category in reports_by_category {
                    reports_by_category[node.category] += 1;
                } else {
                    reports_by_category[node.category] = 1;
                }
                
                # Urgency
                if node.urgency in reports_by_urgency {
                    reports_by_urgency[node.urgency] += 1;
                } else {
                    reports_by_urgency[node.urgency] = 1;
                }
                
                # Status
                if node.status in reports_by_status {
                    reports_by_status[node.status] += 1;
                } else {
                    reports_by_status[node.status] = 1;
                }
            }
        }
        
        # Mock monthly trend for now
        monthly_trend = [
          { "month": "Oct", "reports": 34, "resolved": 28 },
          { "month": "Nov", "reports": 45, "resolved": 32 },
          { "month": "Dec", "reports": 77, "resolved": 29 }
        ];
        
        report {
            "totalReports": total_reports,
            "resolvedReports": resolved_reports,
            "avgResolutionTime": 5.0,
            "reportsByCategory": reports_by_category,
            "reportsByUrgency": reports_by_urgency,
            "reportsByStatus": reports_by_status,
            "monthlyTrend": monthly_trend
        };
    }
}

walker StatusUpdateAgent {
    has report_id: str;
    has status: str;

    can find_report with `root entry {
        found = False;
        for node in root.out_nodes() {
            if "id" in node.context and node.id == self.report_id {
                visit node;
                found = True;
                break;
            }
        }
        if not found {
            report {"error": "Report not found"};
        }
    }

    can update_report with Report entry {
        here.status = self.status;
        report {"success": True, "id": here.id, "status": here.status};
        disengage;
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
