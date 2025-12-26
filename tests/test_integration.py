import requests
import json
import time
import uuid

def test_direct_email():
    print("--- Testing Direct Email Notification (Port 8003) ---")
    try:
        response = requests.post("http://localhost:8003/send_email", json={
            "to": "ccs00056021@student.maseno.ac.ke",
            "subject": "Direct Test Email",
            "body": "This is a direct test from the test script."
        })
        if response.status_code == 200:
            print("Direct email request successful.")
            print(f"Response: {response.json()}")
        else:
            print(f"Direct email request failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to Notification Service on port 8003. Is it running?")
    except Exception as e:
        print(f"Error: {e}")

def test_jac_flow():
    print("\n--- Testing Full Flow via Jac (Port 8002) ---")
    unique_id = str(uuid.uuid4())
    import random
    random_words = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew"]
    random_desc = " ".join(random.sample(random_words, 3))
    
    try:
        # Payload for IntakeAgent
        payload = {
            "report_data": {
                "title": f"Unique Report {unique_id}",
                "description": f"This is a completely new issue about {random_desc} {unique_id}.",
                "name": "Test User",
                "email": "testuser@example.com"
            }
        }
        
        # Assuming standard Jac serve endpoint structure
        # We need to run the walker 'IntakeAgent' on the root node
        # The endpoint might be /walker/IntakeAgent/run or similar depending on Jac version
        # Let's try the standard /walker/IntakeAgent
        
        url = "http://localhost:8002/walker/IntakeAgent"
        print(f"Sending request to {url}...")
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("Jac walker executed successfully.")
            print(f"Response: {response.json()}")
            print("Check your email (ccs00056021@student.maseno.ac.ke) and the notification_service.log file.")
        else:
            print(f"Jac walker failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to Jac Backend on port 8002. Is it running?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_direct_email()
    # Uncomment the next line if you want to test the full flow immediately
    test_jac_flow()
