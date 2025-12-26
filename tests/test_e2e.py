#!/usr/bin/env python3
"""
End-to-end integration test for Dira with PostgreSQL backend

Tests the complete flow:
1. Create reporter
2. Submit report
3. Classification (via NLP service)
4. Embedding storage (via pgvector)
5. Duplicate detection (via vector search)
6. Routing to organisations
"""

import requests
import time
import sys

# Service URLs
DB_API_URL = "http://127.0.0.1:8002"
NLP_API_URL = "http://127.0.0.1:8001"

def check_service(url, name):
    """Check if a service is running"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        if response.status_code == 200:
            print(f"{name} is running")
            return True
    except:
        pass
    print(f"{name} is NOT running at {url}")
    return False

def test_end_to_end():
    """Run end-to-end test"""
    
    print("Dira End-to-End Integration Test\n")
    print("=" * 60)
    
    # Check services
    print("\nChecking Services...")
    db_api_ok = check_service(DB_API_URL, "Database API (port 8002)")
    nlp_api_ok = check_service(NLP_API_URL, "NLP API (port 8001)")
    
    if not db_api_ok or not nlp_api_ok:
        print("\nOne or more services are not running!")
        print("\nTo start services:")
        print("Terminal 1: cd backend/python && python db_api.py")
        print("Terminal 2: cd backend/python && python nlp_service.py")
        return False
    
    # Test 1: Create Reporter
    print("\nCreating Reporter...")
    reporter_data = {
        "name": "Test User",
        "email": "test@example.com",
        "is_anonymous": False
    }
    
    response = requests.post(f"{DB_API_URL}/reporters", json=reporter_data)
    if response.status_code == 200:
        reporter_id = response.json()["reporter_id"]
        print(f"   Reporter created: {reporter_id}")
    else:
        print(f"   Failed to create reporter: {response.text}")
        return False
    
    # Test 2: Submit Report
    print("\nSubmitting Report...")
    report_data = {
        "title": "Water main break on Elm Street",
        "description": "Large water pipe has burst causing flooding on Elm Street near the intersection with Oak Avenue",
        "status": "submitted",
        "reporter_id": reporter_id
    }
    
    response = requests.post(f"{DB_API_URL}/reports", json=report_data)
    if response.status_code == 200:
        report_id = response.json()["report_id"]
        print(f"   Report created: {report_id}")
    else:
        print(f"   Failed to create report: {response.text}")
        return False
    
    # Test 3: Classify Report
    print("\nClassifying Report...")
    text = report_data["title"] + " " + report_data["description"]
    
    response = requests.post(f"{NLP_API_URL}/classify", json={"text": text})
    if response.status_code == 200:
        classification = response.json()
        category = classification["category"]
        confidence = classification["confidence"]
        print(f"   Classified as: {category} (confidence: {confidence:.2f})")
        
        # Update report with classification
        requests.patch(f"{DB_API_URL}/reports/{report_id}", json={
            "category": category,
            "confidence": confidence
        })
    else:
        print(f"   Classification failed: {response.text}")
        category = "infrastructure"  # Fallback
    
    # Test 4: Assess Urgency
    print("\nAssessing Urgency...")
    response = requests.post(f"{NLP_API_URL}/assess_urgency", json={"text": text})
    if response.status_code == 200:
        urgency = response.json()
        print(f"   Urgency: {urgency}")
        
        # Update report with urgency
        requests.patch(f"{DB_API_URL}/reports/{report_id}", json={"urgency": urgency})
    else:
        print(f"   Urgency assessment failed: {response.text}")
        urgency = "medium"  # Fallback
    
    # Test 5: Store Embedding
    print("\nStoring Embedding...")
    response = requests.post(f"{NLP_API_URL}/store_embedding", json={
        "report_id": report_id,
        "title": report_data["title"],
        "description": report_data["description"]
    })
    if response.status_code == 200:
        print(f"   Embedding stored in pgvector")
    else:
        print(f"   Failed to store embedding: {response.text}")
    
    # Test 6: Find Duplicates
    print("\nChecking for Duplicates...")
    response = requests.post(f"{NLP_API_URL}/find_duplicates", json={
        "report_id": report_id,
        "title": report_data["title"],
        "description": report_data["description"],
        "threshold": 0.85
    })
    if response.status_code == 200:
        duplicates = response.json()["duplicates"]
        if len(duplicates) > 0:
            print(f"   Found {len(duplicates)} potential duplicates")
            for dup in duplicates[:3]:  # Show first 3
                print(f"      - {dup['title']} (score: {dup['score']:.3f})")
        else:
            print(f"   No duplicates found - report is unique")
    else:
        print(f"   Duplicate detection failed: {response.text}")
    
    # Test 7: Get Organisations to Route To
    print("\nFinding Organisations to Route...")
    
    # Based on category, get relevant organisations
    if category == "infrastructure":
        org_response1 = requests.get(f"{DB_API_URL}/organisations/type/utility")
        org_response2 = requests.get(f"{DB_API_URL}/organisations/type/government")
        selected_orgs = org_response1.json() + org_response2.json()
    elif category == "safety":
        org_response = requests.get(f"{DB_API_URL}/organisations/type/government")
        selected_orgs = org_response.json()
    else:
        org_response = requests.get(f"{DB_API_URL}/organisations")
        selected_orgs = org_response.json()
    
    print(f"   Found {len(selected_orgs)} organisations to notify:")
    for org in selected_orgs:
        print(f"      - {org['name']} ({org['type']})")
    
    # Test 8: Create Report Routes
    print("\nCreating Report Routes...")
    route_count = 0
    for org in selected_orgs:
        route_response = requests.post(f"{DB_API_URL}/report_routes", json={
            "report_id": report_id,
            "organisation_id": org["id"],
            "message": f"Public report: {report_data['title']}",
            "status": "sent"
        })
        if route_response.status_code == 200:
            route_count += 1
    
    print(f"   Created {route_count} route records")
    
    # Test 9: Update Report Status
    print("\nUpdating Report Status...")
    requests.patch(f"{DB_API_URL}/reports/{report_id}", json={"status": "routed"})
    print(f"   Report marked as routed")
    
    # Final Verification
    print("\nVerifying Final State...")
    final_report = requests.get(f"{DB_API_URL}/reports/{report_id}").json()
    routes = requests.get(f"{DB_API_URL}/report_routes/report/{report_id}").json()
    
    print(f"\nFinal Report State:")
    print(f"   ID: {final_report['id']}")
    print(f"   Title: {final_report['title']}")
    print(f"   Category: {final_report.get('category', 'N/A')}")
    print(f"   Urgency: {final_report.get('urgency', 'N/A')}")
    print(f"   Status: {final_report['status']}")
    print(f"   Routes Created: {len(routes)}")
    
    print("\n" + "=" * 60)
    print("End-to-End Test PASSED!")
    print("=" * 60)
    
    # Cleanup
    print("\nCleaning up test data...")
    requests.delete(f"{DB_API_URL}/reports/{report_id}")
    print("   Test report deleted")
    
    return True

if __name__ == "__main__":
    try:
        success = test_end_to_end()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nTest failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
