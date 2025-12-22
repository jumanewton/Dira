import json
import requests
import time
import sys
import os

# Configuration
JAC_BACKEND_URL = "http://localhost:8002"
WALKER_NAME = "IntakeAgent"
SEED_FILE = "reports.json"

def load_seed_data():
    print(f"--- Loading Seed Data from {SEED_FILE} ---")
    
    # 1. Read the seed file
    if not os.path.exists(SEED_FILE):
        print(f"❌ Error: {SEED_FILE} not found.")
        return

    try:
        with open(SEED_FILE, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Error: Failed to decode JSON from {SEED_FILE}.")
        return

    # 2. Extract reports
    # Handle different possible structures based on the file dump
    reports_to_load = []
    
    if "result" in data and "reports_list" in data["result"]:
        reports_to_load = data["result"]["reports_list"]
    elif "reports" in data and isinstance(data["reports"], list):
        # Sometimes reports might be a list of lists or just a list
        if len(data["reports"]) > 0 and isinstance(data["reports"][0], list):
             reports_to_load = data["reports"][0]
        else:
            reports_to_load = data["reports"]
    elif isinstance(data, list):
        reports_to_load = data
    
    if not reports_to_load:
        print("❌ Error: No reports found in the JSON structure.")
        return

    print(f"Found {len(reports_to_load)} reports to load.")

    # 3. Send to Backend
    success_count = 0
    fail_count = 0

    for i, report in enumerate(reports_to_load):
        # Construct payload for IntakeAgent
        # We only need title and description, maybe name/email if available
        # The agent generates ID, status, etc.
        
        payload = {
            "report_data": {
                "title": report.get("title", "Untitled Report"),
                "description": report.get("description", "No description provided."),
                "name": "Seed Data Loader",
                "email": "loader@example.com"
            }
        }

        try:
            url = f"{JAC_BACKEND_URL}/walker/{WALKER_NAME}"
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print(f"✅ [{i+1}/{len(reports_to_load)}] Loaded: {report.get('title')[:30]}...")
                success_count += 1
            else:
                print(f"❌ [{i+1}/{len(reports_to_load)}] Failed: {report.get('title')[:30]}... (Status: {response.status_code})")
                print(f"   Response: {response.text}")
                fail_count += 1
                
            # Small delay to avoid overwhelming the server/LLM
            time.sleep(0.5)
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Could not connect to {JAC_BACKEND_URL}. Is the backend running?")
            break
        except Exception as e:
            print(f"❌ Error processing report: {e}")
            fail_count += 1

    print("\n--- Summary ---")
    print(f"Total Reports: {len(reports_to_load)}")
    print(f"Successfully Loaded: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    load_seed_data()
