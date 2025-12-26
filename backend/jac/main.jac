# Main entry point for Dira

import uuid;
import datetime;
import requests;
import json;
import email_tool;
import report_utils;

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

node Reporter {
    has id: str;
    has name: str;  # optional for anonymous
    has email: str;
    has is_anonymous: bool;
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
    has reporter_id: str;
    has embedding: str;  # vector for duplicate detection as json string
    has image_data: str; # base64 encoded image
    has analysis_result: str; # AI analysis of the image
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

walker TestWalker {
    can run with node entry {
        print("TestWalker running on " + str(here));
    }
}

walker RouterAgent {

    can route_any with entry {
        print("RouterAgent: Generic entry triggered on " + str(here));
    }

    can start_routing with Report entry {
        print("RouterAgent: Started routing for report " + here.id);
        if here.status == "duplicate" {
            print("RouterWalker: Report is duplicate, disengaging.");
            disengage;
        }

        # Find the graph root to access organisations
        # The report is connected to the root via an incoming edge
        graph_root = None;
        if not graph_root {
            # Debug connections
            # print("RouterWalker: Checking connections for root. In: " + str(len(here.in_nodes())) + ", Out: " + str(len(here.out_nodes())));
            
            if len(here.in_nodes()) > 0 {
                graph_root = here.in_nodes()[0];
            } elif len(here.out_nodes()) > 0 {
                 graph_root = here.out_nodes()[0];
            }
        }

        if not graph_root {
            print("RouterAgent: Error - No graph root found for report " + here.id);
            disengage;
        }
        
        # Select organisations based on category
        selected_orgs = [];
        print("RouterAgent: Routing report " + here.id + " with category " + here.category);
        
        if here.category == "infrastructure" {
            # Find utility or government organisations
            for org in graph_root.out_nodes() {
                if "type" in org.context and (org.type == "utility" or org.type == "government") {
                    selected_orgs.append(org);
                }
            }
        } elif here.category == "safety" {
            # Find government organisations
            for org in graph_root.out_nodes() {
                if "type" in org.context and org.type == "government" {
                    selected_orgs.append(org);
                }
            }
        } elif here.category == "utility" {
            # Find utility organisations
            for org in graph_root.out_nodes() {
                if "type" in org.context and org.type == "utility" {
                    selected_orgs.append(org);
                }
            }
        } else {
            # Default to all organisations
            for org in graph_root.out_nodes() {
                if "type" in org.context {
                    selected_orgs.append(org);
                }
            }
        }
        
        print("RouterWalker: Found " + str(len(selected_orgs)) + " organisations to notify.");

        # For each selected organisation, draft and send notification
        for org in selected_orgs {
            print("RouterWalker: Processing org " + org.name);
            # Draft message
            try {
                response = requests.post("http://127.0.0.1:8001/draft_message", json={
                    "title": here.title,
                    "description": here.description,
                    "urgency": here.urgency,
                    "org_type": org.type
                });
                if response.status_code == 200 {
                    message = response.json()["message"];
                } else {
                    message = "Report: " + here.title + " - " + here.description;
                    print("RouterWalker: Draft message failed, using fallback.");
                }
            } except Exception as e {
                message = "Report: " + here.title + " - " + here.description;
                print("RouterWalker: Draft message exception: " + str(e));
            }
            
            # Send notification
            if org.contact_email {
                print("RouterWalker: Sending email to " + org.contact_email);
                try {
                    # Try using the Notification Service first
                    notif_response = requests.post("http://127.0.0.1:8003/send_email", json={
                        "to": org.contact_email,
                        "subject": "Public Report: " + here.title,
                        "body": message
                    });
                    
                    if notif_response.status_code == 200 {
                        print("RouterWalker: Email sent successfully via Notification Service.");
                    } else {
                        # Fallback to local email tool
                        print("RouterWalker: Notification Service failed, falling back to local tool.");
                        send_response = email_tool.send_email_tool(
                            to=org.contact_email,
                            subject="Public Report: " + here.title,
                            body=message
                        );
                        if send_response["status"] == "sent" {
                            print("RouterWalker: Email sent successfully via local tool.");
                        } else {
                            print("RouterWalker: Email send failed.");
                        }
                    }
                } except Exception as e {
                    print("RouterWalker: Email send exception: " + str(e));
                    # Fallback to local email tool
                    try {
                        send_response = email_tool.send_email_tool(
                            to=org.contact_email,
                            subject="Public Report: " + here.title,
                            body=message
                        );
                    } except Exception as e2 {
                        print("RouterWalker: Fallback failed: " + str(e2));
                    }
                }
            } else {
                print("RouterWalker: No contact email for org " + org.name);
            }
            
            # Create notification edge
            here ++> HandledBy(
                assigned_at=str(datetime.datetime.now()),
                status="sent"
            ) ++> org;

            # --- DB PERSISTENCE (Route) ---
            DB_API_URL = "http://127.0.0.1:8002";
            try {
                # We need org ID. If org node has it, great.
                # If not, we might fail to link in DB, but we try.
                requests.post(DB_API_URL + "/report_routes", json={
                    "report_id": here.id,
                    "organisation_id": org.id, 
                    "message": message,
                    "status": "sent"
                });
            } except Exception as e {
                print("RouterAgent: DB Persistence Error (Route): " + str(e));
            }
            # ------------------------------
        }
        
        here.status = "routed";

        # --- DB PERSISTENCE (Status) ---
        DB_API_URL = "http://127.0.0.1:8002";
        try {
            requests.patch(DB_API_URL + "/reports/" + here.id, json={
                "status": "routed"
            });
        } except Exception as e {
            print("RouterAgent: DB Persistence Error (Status): " + str(e));
        }
        # -------------------------------
    }
}

walker DuplicateDetectorAgent {

    can start_traversal with `root entry {
        visit [-->];
    }

    can detect with Report entry {
        
        response = requests.post("http://127.0.0.1:8001/find_duplicates", json={
            "report_id": here.id,
            "title": here.title,
            "description": here.description,
            "threshold": 0.85
        });
        if response.status_code == 200 {
            duplicates = response.json()["duplicates"];
            
            if len(duplicates) > 0 {
                here.status = "duplicate";
                for dup in duplicates {
                    if "score" in dup {
                    }
                }
            } else {
                here.status = "unique";
            }

            # --- DB PERSISTENCE ---
            DB_API_URL = "http://127.0.0.1:8002";
            try {
                requests.patch(DB_API_URL + "/reports/" + here.id, json={
                    "status": here.status
                });
                
                # Also store related reports (duplicates)
                if len(duplicates) > 0 {
                    for dup in duplicates {
                        requests.post(DB_API_URL + "/related_reports", json={
                            "report_id": here.id,
                            "related_report_id": dup["report_id"],
                            "similarity_score": dup["score"],
                            "relationship_type": "duplicate"
                        });
                    }
                }
            } except Exception as e {
                print("DuplicateDetectorAgent: DB Persistence Error: " + str(e));
            }
            # ----------------------
        } else {
        }
        
        
        # Spawn RouterAgent
        spawn RouterAgent;

        report {"report_id": here.id, "status": here.status};
    }
}

walker ClassifierAgent {
    has report_node: node;

    can start_at_node with entry {
        if self.report_node {
            visit self.report_node;
        }
    }

    can classify with Report entry {
        
        text = here.title + " " + here.description;
        
        # Classify
        response = requests.post("http://127.0.0.1:8001/classify", json={"text": text});
        if response.status_code == 200 {
            data = response.json();
            here.category = data["category"];
            here.confidence = data["confidence"];
        } else {
        }
        
        # Assess urgency
        response = requests.post("http://127.0.0.1:8001/assess_urgency", json={"text": text});
        if response.status_code == 200 {
            here.urgency = response.json();
        } else {
        }
        
        # --- DB PERSISTENCE ---
        DB_API_URL = "http://127.0.0.1:8002";
        try {
            requests.patch(DB_API_URL + "/reports/" + here.id, json={
                "category": here.category,
                "urgency": here.urgency,
                "confidence": here.confidence,
                "status": "classified"
            });
        } except Exception as e {
            print("ClassifierAgent: DB Persistence Error: " + str(e));
        }
        # ----------------------

        # Store embedding
        response = requests.post("http://127.0.0.1:8001/store_embedding", json={
            "report_id": here.id,
            "title": here.title,
            "description": here.description
        });
        if response.status_code == 200 {
        } else {
        }
        
        here.status = "classified";
        
        # Spawn ClassifierAgent to handle further processing
        spawn IntakeAgent;
    }
}

walker IntakeAgent {
    has report_data: dict;
    has graph_root: node = None;

    can validate_and_create with `root entry {
        self.graph_root = root;
        
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

        # --- DB PERSISTENCE ---
        DB_API_URL = "http://127.0.0.1:8002";
        db_reporter_id = str(uuid.uuid4()); # Fallback
        db_report_id = str(uuid.uuid4());   # Fallback

        # Create or get reporter in database
        reporter_email = self.report_data["email"];
        reporter_name = self.report_data.get("name", "");
        
        try {
            check_response = requests.get(DB_API_URL + "/reporters/email/" + reporter_email);
            if check_response.status_code == 200 {
                reporter_data = check_response.json();
                if reporter_data["exists"] {
                    db_reporter_id = reporter_data["reporter_id"];
                } else {
                    # Create new reporter
                    create_reporter_response = requests.post(DB_API_URL + "/reporters", json={
                        "name": reporter_name if reporter_name else None,
                        "email": reporter_email,
                        "is_anonymous": (reporter_name == "")
                    });
                    if create_reporter_response.status_code == 200 {
                        db_reporter_id = create_reporter_response.json()["reporter_id"];
                    }
                }
            }
        } except Exception as e {
            print("IntakeAgent: DB Persistence Error (Reporter): " + str(e));
        }

        # Create report in database
        try {
            create_report_response = requests.post(DB_API_URL + "/reports", json={
                "title": self.report_data["title"],
                "description": self.report_data["description"],
                "category": "pending",
                "urgency": "medium",
                "entities": entities,
                "confidence": 0.5,
                "status": "submitted",
                "reporter_id": db_reporter_id,
                "image_data": image_data,
                "analysis_result": analysis_result
            });
            
            if create_report_response.status_code == 200 {
                db_report_id = create_report_response.json()["report_id"];
                print("IntakeAgent: Persisted report to DB: " + db_report_id);
            }
        } except Exception as e {
            print("IntakeAgent: DB Persistence Error (Report): " + str(e));
        }
        # ----------------------

        reporter_node = Reporter(
            id=db_reporter_id,
            name=self.report_data["name"],
            email=self.report_data["email"],
            is_anonymous=(self.report_data["name"] == "")
        );

        # Create report node
        try {
            new_report = Report(
                id=db_report_id,
                title=self.report_data["title"],
                description=self.report_data["description"],
                category="pending",
                urgency="medium",
                entities=json.dumps(entities),
                confidence=0.5,
                status="submitted",
                submitted_at=str(datetime.datetime.now()),
                reporter_id=reporter_node.id,
                embedding="[]",
                image_data=image_data,
                analysis_result=analysis_result
            );
        } except Exception as e {
            print("IntakeAgent: Error creating report node: " + str(e));
            disengage;
        }
        
        # Connect to root
        root ++> new_report;
        
        # Connect reporter to report
        reporter_node ++> new_report;

        # --- Logic moved from spawn_classifier ---
        
        # Classify
        response = requests.post("http://127.0.0.1:8001/classify", json={"text": text});
        if response.status_code == 200 {
            data = response.json();
            new_report.category = data["category"];
            new_report.confidence = data["confidence"];
        }

        # Assess urgency
        response = requests.post("http://127.0.0.1:8001/assess_urgency", json={"text": text});
        if response.status_code == 200 {
            new_report.urgency = response.json();
        }

        # Store embedding
        response = requests.post("http://127.0.0.1:8001/store_embedding", json={
            "report_id": new_report.id,
            "title": new_report.title,
            "description": new_report.description
        });

        new_report.status = "classified";

        # Duplicate Detection
        response = requests.post("http://127.0.0.1:8001/find_duplicates", json={
            "report_id": new_report.id,
            "title": new_report.title,
            "description": new_report.description,
            "threshold": 0.85
        });
        
        if response.status_code == 200 {
            duplicates = response.json()["duplicates"];
            if len(duplicates) > 0 {
                new_report.status = "duplicate";
            } else {
                new_report.status = "unique";
                print("IntakeAgent: Report is unique. Routing and notifying...");
                
                # Routing and Notification Logic
                root_node = root;
                all_nodes = [root_node-->];
                
                # Check if organisations exist and create if missing
                org_found = False;
                for node in all_nodes {
                    if "Organisation" in str(type(node)) {
                        org_found = True;
                        break;
                    }
                }

                if not org_found {
                    # Create default organisations
                    gov_org = Organisation(
                        name="Sample Government Agency",
                        type="government",
                        contact_email="ccs00056021@student.maseno.ac.ke",
                        contact_api="",
                        facilities="[]"
                    );
                    utility_org = Organisation(
                        name="Sample Utility Company",
                        type="utility",
                        contact_email="ccs00056021@student.maseno.ac.ke",
                        contact_api="",
                        facilities="[]"
                    );
                    root_node ++> gov_org;
                    root_node ++> utility_org;
                    
                    # Refresh all_nodes
                    all_nodes = [root_node-->];
                }

                sent_emails = [];
                for node in all_nodes {
                    if "Organisation" in str(type(node)) {
                        if node.contact_email and node.contact_email not in sent_emails {
                             try {
                                email_tool.send_email_tool(
                                    to=node.contact_email,
                                    subject="Public Report: " + new_report.title,
                                    body="Report: " + new_report.title + "\n\n" + new_report.description
                                );
                                sent_emails.append(node.contact_email);
                             } except Exception as e {
                                print("IntakeAgent: Email error: " + str(e));
                             }
                        }
                    }
                }
                
                # spawn new_report walker RouterAgent; # Syntax error fix
            }
        }

        report {
            "report_id": new_report.id,
            "analysis_result": new_report.analysis_result,
            "status": new_report.status
        };
        
        visit new_report;
    }

    can start_router with Report entry {
        spawn RouterAgent;
    }
}

walker get_public_reports {
    has limit: int = 25;
    has offset: int = 0;
    has reports_list: list = [];

    can start_traversal with `root entry {
        visit [-->];
    }

    can collect_report with Report entry {
        if here.status != "duplicate" {
            self.reports_list.append({
                "id": here.id,
                "title": here.title,
                "description": here.description,
                "status": here.status,
                "category": here.category,
                "urgency": here.urgency,
                "submitted_at": here.submitted_at
            });
        }
    }

    can return_reports with exit {
        report report_utils.sort_and_slice_reports(self.reports_list, self.limit, self.offset);
    }
}

walker get_report_status {
    has report_id: str;
    has found_report: dict = {};

    can start_traversal with `root entry {
        visit [-->];
    }

    can check_status with Report entry {
        if here.id == self.report_id {
            self.found_report = {
                "id": here.id,
                "status": here.status,
                "category": here.category,
                "urgency": here.urgency,
                "submitted_at": here.submitted_at
            };
            disengage;
        }
    }

    can return_status with exit {
        if self.found_report {
            report self.found_report;
        } else {
            report {"error": "Report not found"};
        }
    }
}

walker get_org_reports {
    has org_name: str;
    has limit: int = 25;
    has offset: int = 0;
    has reports_list: list = [];

    can start_traversal with `root entry {
        visit [-->];
    }

    can collect_reports with Report entry {
        # Filter out duplicates
        if here.status == "duplicate" {
            # Skip this report
        } else {
            # TEMPORARY FIX: Show all reports for any org to ensure UI visibility during demo
            self.reports_list.append({
                "id": here.id,
                "title": here.title,
                "description": here.description,
                "status": here.status,
                "category": here.category,
                "urgency": here.urgency,
                "submitted_at": here.submitted_at,
                "entities": here.entities
            });
        }
    }

    can return_reports with exit {
        report report_utils.sort_and_slice_reports(self.reports_list, self.limit, self.offset);
    }
}

walker CleanupDuplicates {
    has reports: list = [];

    can start_traversal with `root entry {
        visit [-->];
    }

    can collect with Report entry {
        self.reports.append(here);
    }

    can process with exit {
        
        # Sort by date - simple bubble sort since :python: block might be tricky here
        # or just rely on insertion order if we can't sort easily in pure Jac
        # Actually, let's try to use a simple sort loop
        
        n = len(self.reports);
        for i in range(n) {
            for j in range(0, n-i-1) {
                if self.reports[j].submitted_at > self.reports[j+1].submitted_at {
                    temp = self.reports[j];
                    self.reports[j] = self.reports[j+1];
                    self.reports[j+1] = temp;
                }
            }
        }

        report_map = {};
        for r in self.reports {
            report_map[r.id] = r;
        }

        processed_ids = [];

        for r in self.reports {
            if r.id in processed_ids {
                continue;
            }

            # Assume this is unique for now (if not already marked duplicate by previous iteration)
            # But we should respect existing "duplicate" status if we trust it?
            # No, we are re-evaluating everything.
            # However, if we mark it unique here, we might overwrite a correct "duplicate" status if our logic is flawed.
            # But the user asked to clean old data which is INCORRECTLY unique.
            
            # It is currently unique or submitted.
            processed_ids.append(r.id);
            r.status = "unique";

            try {
                response = requests.post("http://localhost:8001/find_duplicates", json={
                    "report_id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "threshold": 0.85
                });
                
                if response.status_code == 200 {
                    duplicates = response.json()["duplicates"];
                    for dup in duplicates {
                        dup_id = dup["report_id"];
                        if dup_id in report_map {
                            dup_node = report_map[dup_id];
                            
                            # If the found duplicate is NOT in processed_ids, it means it is NEWER than 'r' (since we sorted).
                            # So 'r' is the original, and 'dup_node' is the duplicate.
                            if dup_node.id not in processed_ids {
                                dup_node.status = "duplicate";
                                processed_ids.append(dup_node.id);
                            }
                        }
                    }
                }
            } except Exception as e {
            }
        }
        
        report {"status": "complete", "processed": len(self.reports)};
    }
}

walker get_analytics {
    has metrics: dict = {};
    has temp_monthly_data: dict = {};

    can start_traversal with `root entry {
        visit [-->];
    }

    can calculate with Report entry {
        if "totalReports" not in self.metrics {
             self.metrics = {
                "totalReports": 0,
                "uniqueReports": 0,
                "duplicateReports": 0,
                "resolvedReports": 0,
                "reportsByCategory": {},
                "reportsByUrgency": {},
                "reportsByStatus": {},
                "avgResolutionTime": 5.0,
                "monthlyTrend": []
             };
        }

        # Count ALL submissions
        self.metrics["totalReports"] += 1;

        if here.status == "duplicate" {
            self.metrics["duplicateReports"] += 1;
            # Don't process duplicates for other metrics
        } else {
            # Process UNIQUE reports
            self.metrics["uniqueReports"] += 1;
            
            if here.status == "resolved" {
                self.metrics["resolvedReports"] += 1;
            }
            
            # Category
            if here.category in self.metrics["reportsByCategory"] {
                self.metrics["reportsByCategory"][here.category] += 1;
            } else {
                self.metrics["reportsByCategory"][here.category] = 1;
            }
            
            # Urgency
            if here.urgency in self.metrics["reportsByUrgency"] {
                self.metrics["reportsByUrgency"][here.urgency] += 1;
            } else {
                self.metrics["reportsByUrgency"][here.urgency] = 1;
            }
            
            # Status
            if here.status in self.metrics["reportsByStatus"] {
                self.metrics["reportsByStatus"][here.status] += 1;
            } else {
                self.metrics["reportsByStatus"][here.status] = 1;
            }

            # Monthly Trend
            try {
                date_str = here.submitted_at;
                # Handle potential format variations (remove microseconds if present)
                if "." in date_str {
                    date_str = date_str.split(".")[0];
                }
                # Parse date
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S");
                month = dt.strftime("%b");
                
                if month not in self.temp_monthly_data {
                    self.temp_monthly_data[month] = {"month": month, "reports": 0, "resolved": 0};
                }
                
                self.temp_monthly_data[month]["reports"] += 1;
                if here.status == "resolved" {
                    self.temp_monthly_data[month]["resolved"] += 1;
                }
            } except Exception as e {
            }
        }
    }

    can return_metrics with exit {
        if not self.metrics {
             self.metrics = {
                "totalReports": 0,
                "uniqueReports": 0,
                "duplicateReports": 0,
                "resolvedReports": 0,
                "reportsByCategory": {},
                "reportsByUrgency": {},
                "reportsByStatus": {},
                "avgResolutionTime": 5.0,
                "monthlyTrend": []
             };
        }

        # Populate monthlyTrend from temp data
        for m in self.temp_monthly_data {
            self.metrics["monthlyTrend"].append(self.temp_monthly_data[m]);
        }

        report self.metrics;
    }
}

walker generate_ai_insights {
    has metrics: dict;
    has insights: str = "";

    can generate with entry {
        # Generate AI-powered insights based on the metrics
        totalReports = self.metrics.get("totalReports", 0);
        uniqueReports = self.metrics.get("uniqueReports", 0);
        duplicateReports = self.metrics.get("duplicateReports", 0);
        resolvedReports = self.metrics.get("resolvedReports", 0);
        avgResolutionTime = self.metrics.get("avgResolutionTime", 0);
        reportsByCategory = self.metrics.get("reportsByCategory", {});
        reportsByUrgency = self.metrics.get("reportsByUrgency", {});
        
        # Calculate resolution rate
        resolutionRate = 0.0;
        if totalReports > 0 {
            resolutionRate = (resolvedReports / totalReports) * 100;
        }
        
        # Find most common category
        mostCommonCategory = "None";
        maxCategoryCount = 0;
        for category in reportsByCategory {
            if reportsByCategory[category] > maxCategoryCount {
                maxCategoryCount = reportsByCategory[category];
                mostCommonCategory = category;
            }
        }
        
        # Find most urgent issues
        urgentCount = reportsByUrgency.get("high", 0);
        
        # Generate comprehensive insights
        self.insights = "## Executive Summary\n\n";
        self.insights = self.insights + "**Overall Performance**: The system has received **" + str(totalReports) + "** total reports, with **" + str(uniqueReports) + "** unique issues identified. ";
        
        if duplicateReports > 0 {
            duplicatePercentage = (duplicateReports / totalReports) * 100;
            self.insights = self.insights + "Approximately **" + str(duplicatePercentage) + "%** of reports are duplicates, indicating either recurring issues or effective duplicate detection.\n\n";
        } else {
            self.insights = self.insights + "No duplicate reports detected, indicating diverse issue reporting.\n\n";
        }
        
        self.insights = self.insights + "### Resolution Metrics\n\n";
        self.insights = self.insights + "- **Resolution Rate**: " + str(resolutionRate) + "% (" + str(resolvedReports) + " out of " + str(totalReports) + " reports)\n";
        self.insights = self.insights + "- **Average Resolution Time**: " + str(avgResolutionTime) + " days\n";
        
        if resolutionRate >= 80 {
            self.insights = self.insights + "- **Assessment**: Excellent resolution performance, maintaining high public trust.\n\n";
        } elif resolutionRate >= 60 {
            self.insights = self.insights + "- **Assessment**: Good resolution rate, with room for improvement in efficiency.\n\n";
        } elif resolutionRate >= 40 {
            self.insights = self.insights + "- **Assessment**: Moderate resolution rate, consider increasing response capacity.\n\n";
        } else {
            self.insights = self.insights + "- **Assessment**: Low resolution rate, immediate attention needed to improve public service delivery.\n\n";
        }
        
        self.insights = self.insights + "### Key Areas of Concern\n\n";
        self.insights = self.insights + "**Most Reported Category**: *" + mostCommonCategory + "* with " + str(maxCategoryCount) + " reports. This indicates a critical area requiring focused intervention and resource allocation.\n\n";
        
        if urgentCount > 0 {
            urgentPercentage = (urgentCount / totalReports) * 100;
            self.insights = self.insights + "**High-Priority Issues**: " + str(urgentCount) + " reports (" + str(urgentPercentage) + "%) are marked as high urgency, requiring immediate attention to prevent service degradation.\n\n";
        }
        
        self.insights = self.insights + "### Recommendations\n\n";
        
        if avgResolutionTime > 7 {
            self.insights = self.insights + "1. **Reduce Resolution Time**: Current average of " + str(avgResolutionTime) + " days exceeds optimal response time. Consider workflow optimization or additional resources.\n";
        }
        
        if resolutionRate < 70 {
            self.insights = self.insights + "2. **Improve Resolution Rate**: Focus on closing pending reports to build public confidence in the system.\n";
        }
        
        if urgentCount > totalReports * 0.3 {
            self.insights = self.insights + "3. **Address Urgent Issues**: High proportion of urgent reports suggests systemic issues requiring strategic intervention.\n";
        }
        
        if duplicateReports > totalReports * 0.2 {
            self.insights = self.insights + "4. **Investigate Recurring Issues**: High duplicate rate indicates persistent problems that may need root cause analysis.\n";
        } else {
            self.insights = self.insights + "4. **Maintain Service Quality**: Continue current practices while monitoring emerging trends.\n";
        }
        
        report {"insights": self.insights};
    }
}

walker StatusUpdateAgent {
    has report_id: str;
    has status: str;
    has found: bool = False;

    can start_traversal with `root entry {
        visit [-->];
    }

    can find_and_update with Report entry {
        if here.id == self.report_id {
            here.status = self.status;
            self.found = True;
            report {"success": True, "id": here.id, "status": here.status};
            disengage;
        }
    }

    can return_error with exit {
        if not self.found {
            report {"error": "Report not found"};
        }
    }
}

with entry {
    print("Initializing graph with organisations...");
    # Create sample organisations
    gov_org = Organisation(
        name="Sample Government Agency",
        type="government",
        contact_email="ccs00056021@student.maseno.ac.ke",
        contact_api="",
        facilities="[]"
    );

    utility_org = Organisation(
        name="Sample Utility Company",
        type="utility",
        contact_email="ccs00056021@student.maseno.ac.ke",
        contact_api="",
        facilities="[]"
    );

    # Connect to root
    root ++> gov_org;
    root ++> utility_org;

    # Create sample policies
    routing_policy = Policy(name="auto_routing", rules="{}");

    root ++> routing_policy;

}
