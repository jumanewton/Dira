
import pytest
from fastapi.testclient import TestClient
from backend.python.db_api import app

client = TestClient(app)

def test_create_report_no_reporter():
    response = client.post("/reports", json={
        "title": "Test Report",
        "description": "Test Description",
        "reporter_id": None,
        "entities": {},
        "image_data": "",
        "analysis_result": ""
    })
    print(response.text)
    assert response.status_code == 200
