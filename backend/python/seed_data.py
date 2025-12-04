import requests
import json
import time

JASECI_URL = "http://localhost:8002"

def spawn_walker(walker_name, context={}):
    url = f"{JASECI_URL}/walker/{walker_name}"
    headers = {'Content-Type': 'application/json'}
    payload = context
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error spawning walker {walker_name}: {e}")
        return None

def seed_data():
    print("Seeding data...")
    
    reports = [
        {
            "title": "Dangerous Pothole on 5th Avenue",
            "description": "There is a massive pothole in the middle of the intersection at 5th Ave and Main St. It's causing cars to swerve dangerously.",
            "name": "John Doe",
            "email": "john@example.com"
        },
        {
            "title": "Streetlight out in residential area",
            "description": "The streetlight in front of 123 Oak Lane has been out for a week. It's very dark and unsafe for pedestrians.",
            "name": "Jane Smith",
            "email": "jane@example.com"
        },
        {
            "title": "Water main break",
            "description": "Water is gushing out of the ground near the park entrance. It looks like a pipe burst.",
            "name": "",
            "email": "" # Anonymous
        },
        {
            "title": "Suspicious activity at night",
            "description": "I've seen people loitering around the back of the community center late at night. It feels unsafe.",
            "name": "Concerned Citizen",
            "email": "citizen@example.com"
        }
    ]

    for report in reports:
        print(f"Submitting report: {report['title']}")
        result = spawn_walker("IntakeAgent", {"report_data": report})
        if result:
            print(f"  -> Success! Result: {result}")
        else:
            print("  -> Failed.")
        time.sleep(1) # Be nice to the server

    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
