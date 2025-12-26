# PostgreSQL-backed walker implementations
# These walkers use the database API instead of JAC nodes

import uuid;
import datetime;
import requests;
import json;

# Database API base URL
DB_API_URL = "http://127.0.0.1:8004";

walker IntakeAgentDB {
    """
    IntakeAgent that stores data in PostgreSQL instead of JAC nodes
    """
    has report_data: dict;

    can validate_and_create with `root entry {
        print("IntakeAgentDB: Starting intake process");
        
        # Extract entities
        text = self.report_data["title"] + " " + self.report_data["description"];
        response = requests.post("http://127.0.0.1:8001/extract_entities", json={"text": text});
        entities = response.json() if response.status_code == 200 else {};
        
        # Image Analysis
        image_data = "";
        analysis_result = "";
        if "image_data" in self.report_data {
            image_data = self.report_data["image_data"];
            if image_data {
                img_response = requests.post("http://127.0.0.1:8001/analyze_image", json={"image_data": image_data});
                if img_response.status_code == 200 {
                    analysis_result = img_response.json()["analysis"];
                }
            }
        }

        # Create or get reporter in database
        reporter_email = self.report_data["email"];
        reporter_name = self.report_data.get("name", "");
        
        check_response = requests.get(DB_API_URL + "/reporters/email/" + reporter_email);
        if check_response.status_code == 200 {
            reporter_data = check_response.json();
            if reporter_data["exists"] {
                reporter_id = reporter_data["reporter_id"];
                print("IntakeAgentDB: Using existing reporter: " + reporter_id);
            } else {
                # Create new reporter
                create_reporter_response = requests.post(DB_API_URL + "/reporters", json={
                    "name": reporter_name if reporter_name else None,
                    "email": reporter_email,
                    "is_anonymous": (reporter_name == "")
                });
                if create_reporter_response.status_code == 200 {
                    reporter_id = create_reporter_response.json()["reporter_id"];
                    print("IntakeAgentDB: Created new reporter: " + reporter_id);
                } else {
                    print("IntakeAgentDB: Failed to create reporter");
                    disengage;
                }
            }
        } else {
            print("IntakeAgentDB: Failed to check reporter");
            disengage;
        }

        # Create report in database
        create_report_response = requests.post(DB_API_URL + "/reports", json={
            "title": self.report_data["title"],
            "description": self.report_data["description"],
            "category": "pending",
            "urgency": "medium",
            "entities": entities,
            "confidence": 0.5,
            "status": "submitted",
            "reporter_id": reporter_id,
            "image_data": image_data,
            "analysis_result": analysis_result
        });
        
        if create_report_response.status_code != 200 {
            print("IntakeAgentDB: Failed to create report");
            disengage;
        }
        
        report_id = create_report_response.json()["report_id"];
        print("IntakeAgentDB: Created report: " + report_id);

        # Classify report
        response = requests.post("http://127.0.0.1:8001/classify", json={"text": text});
        if response.status_code == 200 {
            data = response.json();
            category = data["category"];
            confidence = data["confidence"];
            
            # Update report with classification
            requests.patch(DB_API_URL + "/reports/" + report_id, json={
                "category": category,
                "confidence": confidence
            });
            print("IntakeAgentDB: Classified as: " + category);
        }

        # Assess urgency
        response = requests.post("http://127.0.0.1:8001/assess_urgency", json={"text": text});
        if response.status_code == 200 {
            urgency = response.json();
            requests.patch(DB_API_URL + "/reports/" + report_id, json={
                "urgency": urgency
            });
            print("IntakeAgentDB: Urgency: " + urgency);
        }

        # Store embedding (NLP service now stores directly in PostgreSQL)
        response = requests.post("http://127.0.0.1:8001/store_embedding", json={
            "report_id": report_id,
            "title": self.report_data["title"],
            "description": self.report_data["description"]
        });
        if response.status_code == 200 {
            print("IntakeAgentDB: Embedding stored");
        }

        # Update status to classified
        requests.patch(DB_API_URL + "/reports/" + report_id, json={
            "status": "classified"
        });

        # Check for duplicates
        response = requests.post("http://127.0.0.1:8001/find_duplicates", json={
            "report_id": report_id,
            "title": self.report_data["title"],
            "description": self.report_data["description"],
            "threshold": 0.85
        });
        
        is_duplicate = False;
        if response.status_code == 200 {
            duplicates = response.json()["duplicates"];
            if len(duplicates) > 0 {
                is_duplicate = True;
                print("IntakeAgentDB: Found " + str(len(duplicates)) + " duplicates");
                
                # Link related reports
                for dup in duplicates {
                    requests.post(DB_API_URL + "/related_reports", json={
                        "report_id": report_id,
                        "related_report_id": dup["report_id"],
                        "similarity_score": dup["score"],
                        "relationship_type": "duplicate"
                    });
                }
                
                # Mark as duplicate
                requests.patch(DB_API_URL + "/reports/" + report_id, json={
                    "status": "duplicate"
                });
            } else {
                print("IntakeAgentDB: No duplicates found");
                requests.patch(DB_API_URL + "/reports/" + report_id, json={
                    "status": "unique"
                });
            }
        }

        # If not duplicate, route to organisations
        if not is_duplicate {
            print("IntakeAgentDB: Routing report to organisations...");
            
            # Get report details
            report_response = requests.get(DB_API_URL + "/reports/" + report_id);
            if report_response.status_code == 200 {
                report = report_response.json();
                category = report.get("category", "");
                
                # Get organisations to notify based on category
                selected_orgs = [];
                
                if category == "infrastructure" {
                    # Get utility and government orgs
                    utility_orgs = requests.get(DB_API_URL + "/organisations/type/utility").json();
                    govt_orgs = requests.get(DB_API_URL + "/organisations/type/government").json();
                    selected_orgs = utility_orgs + govt_orgs;
                } elif category == "safety" {
                    # Get government orgs only
                    selected_orgs = requests.get(DB_API_URL + "/organisations/type/government").json();
                } elif category == "utility" {
                    # Get utility orgs only
                    selected_orgs = requests.get(DB_API_URL + "/organisations/type/utility").json();
                } else {
                    # Get all organisations
                    selected_orgs = requests.get(DB_API_URL + "/organisations").json();
                }
                
                print("IntakeAgentDB: Found " + str(len(selected_orgs)) + " organisations to notify");
                
                # Send to each organisation
                for org in selected_orgs {
                    # Draft message
                    message = "Report: " + report["title"] + " - " + report["description"];
                    try {
                        draft_response = requests.post("http://127.0.0.1:8001/draft_message", json={
                            "title": report["title"],
                            "description": report["description"],
                            "urgency": report.get("urgency", "medium"),
                            "org_type": org["type"]
                        });
                        if draft_response.status_code == 200 {
                            message = draft_response.json()["message"];
                        }
                    } except Exception as e {
                        print("IntakeAgentDB: Draft message failed: " + str(e));
                    }
                    
                    # Send email
                    if org.get("contact_email") {
                        print("IntakeAgentDB: Sending email to " + org["contact_email"]);
                        try {
                            import email_tool;
                            send_response = email_tool.send_email_tool(
                                to=org["contact_email"],
                                subject="Public Report: " + report["title"],
                                body=message
                            );
                            if send_response["status"] == "sent" {
                                print("IntakeAgentDB: Email sent successfully");
                            }
                        } except Exception as e {
                            print("IntakeAgentDB: Email send failed: " + str(e));
                        }
                    }
                    
                    # Create report route record
                    requests.post(DB_API_URL + "/report_routes", json={
                        "report_id": report_id,
                        "organisation_id": org["id"],
                        "message": message,
                        "status": "sent"
                    });
                }
                
                # Mark report as routed
                requests.patch(DB_API_URL + "/reports/" + report_id, json={
                    "status": "routed"
                });
            }
        }
        
        print("IntakeAgentDB: Report processing complete: " + report_id);
        report {"report_id": report_id, "status": "success"};
    }
}
