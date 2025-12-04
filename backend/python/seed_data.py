import requests
import json
import time

JASECI_URL = "http://localhost:8002"
USER_EMAIL = "admin@publiclens.com"
USER_PASSWORD = "password123"

def get_auth_token():
    # Try to login
    login_url = f"{JASECI_URL}/user/login"
    try:
        response = requests.post(login_url, json={"username": USER_EMAIL, "password": USER_PASSWORD})
        if response.status_code == 200:
            return response.json()["token"]
    except:
        pass
    
    # If login fails, try to create user
    create_url = f"{JASECI_URL}/user/create"
    try:
        response = requests.post(create_url, json={"username": USER_EMAIL, "password": USER_PASSWORD})
        if response.status_code == 201 or response.status_code == 200:
             # Login again to get token
             response = requests.post(login_url, json={"username": USER_EMAIL, "password": USER_PASSWORD})
             return response.json()["token"]
    except Exception as e:
        print(f"Error creating/logging in user: {e}")
        return None

def spawn_walker(walker_name, context={}, token=None):
    url = f"{JASECI_URL}/walker/{walker_name}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
        
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
    
    token = get_auth_token()
    if token:
        print(f"Authenticated as {USER_EMAIL}")
    else:
        print("Warning: Could not authenticate. Seeding as guest (data might not be visible to others).")

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
        result = spawn_walker("IntakeAgent", {"report_data": report}, token)
        if result:
            print(f"  -> Success! Result: {result}")
        else:
            print("  -> Failed.")
        time.sleep(1) # Be nice to the server

    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
