import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

# Test data
TEST_APP_ID = "com.whatsapp"
TEST_COMPETITOR_IDS = ["org.telegram.messenger", "org.thoughtcrime.securesms"]
TEST_REVIEWS = [
    {
        "text": "Great app, very user friendly!",
        "score": 5,
        "timestamp": "2024-02-27"
    },
    {
        "text": "App keeps crashing",
        "score": 2,
        "timestamp": "2024-02-27"
    }
]

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to ASO Tool API"}

def test_analyze_app():
    response = client.get(f"/analyze/app/{TEST_APP_ID}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data

def test_analyze_keywords():
    payload = {
        "app_id": TEST_APP_ID,
        "competitor_ids": TEST_COMPETITOR_IDS
    }
    response = client.post("/analyze/keywords/discover", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "analysis" in data

def test_analyze_competitors():
    payload = {
        "app_id": TEST_APP_ID,
        "competitor_ids": TEST_COMPETITOR_IDS
    }
    response = client.post("/analyze/competitors/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "comparison" in data

def test_analyze_reviews():
    response = client.post("/analyze/reviews/analyze", json=TEST_REVIEWS)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "analysis" in data
    assert "overall_sentiment" in data["analysis"]

def test_analyze_metadata():
    response = client.get(f"/analyze/metadata/analyze/{TEST_APP_ID}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "analysis" in data

def test_track_metadata():
    response = client.get(f"/track/track/{TEST_APP_ID}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "tracking_data" in data

def test_invalid_app_id():
    response = client.get("/analyze/app/invalid.app.id")
    assert response.status_code == 400

def test_invalid_competitor_ids():
    payload = {
        "app_id": TEST_APP_ID,
        "competitor_ids": ["invalid.app.id"]
    }
    response = client.post("/analyze/competitors/compare", json=payload)
    assert response.status_code == 400

def test_empty_reviews():
    response = client.post("/analyze/reviews/analyze", json=[])
    assert response.status_code == 400

def test_malformed_review():
    malformed_review = [{"text": "Test"}]  # Missing required fields
    response = client.post("/analyze/reviews/analyze", json=malformed_review)
    assert response.status_code == 400

def test_text_analysis():
    test_text = "This is a test description for the app."
    response = client.post(
        "/analyze/text/analyze",
        params={"text": test_text, "text_type": "full_description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "basic_metrics" in data["analysis"]