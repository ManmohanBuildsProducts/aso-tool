import pytest
from fastapi.testclient import TestClient
from backend.server import app
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Use test database
test_mongo_url = os.environ.get('MONGO_URL', "").replace(
    "test_database", "test_aso_database"
)
client = AsyncIOMotorClient(test_mongo_url)
db = client.test_aso_database

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True)
async def setup_teardown():
    """Setup test data and cleanup after tests"""
    # Clear existing data
    await db.apps.delete_many({})
    await db.keywords.delete_many({})
    await db.rankings.delete_many({})
    
    # Insert test data
    await db.apps.insert_many([
        {
            "package_name": "com.badhobuyer",
            "name": "BadhoBuyer",
            "is_competitor": False,
            "metadata": {
                "title": "BadhoBuyer - B2B Wholesale App",
                "full_description": "A wholesale app for business"
            }
        },
        {
            "package_name": "club.kirana",
            "name": "Kirana Club",
            "is_competitor": True,
            "metadata": {
                "title": "Kirana Club - B2B Distributor",
                "full_description": "B2B wholesale distributor app"
            }
        }
    ])
    
    await db.keywords.insert_many([
        {
            "keyword": "b2b wholesale",
            "category": "primary",
            "search_volume_score": 80,
            "difficulty_score": 60
        },
        {
            "keyword": "distributor app",
            "category": "primary",
            "search_volume_score": 70,
            "difficulty_score": 50
        }
    ])
    
    # Add some ranking data
    await db.rankings.insert_many([
        {
            "app_id": "com.badhobuyer",
            "keyword": "b2b wholesale",
            "rank": 5,
            "date": datetime.utcnow() - timedelta(days=1)
        },
        {
            "app_id": "club.kirana",
            "keyword": "b2b wholesale",
            "rank": 3,
            "date": datetime.utcnow() - timedelta(days=1)
        }
    ])
    
    yield
    
    # Cleanup
    await db.apps.delete_many({})
    await db.keywords.delete_many({})
    await db.rankings.delete_many({})

def test_root(test_client):
    """Test root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_keywords(test_client):
    """Test keyword analysis endpoint"""
    response = test_client.get("/analyze/keywords?keywords=b2b,wholesale,distributor")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
    assert all("opportunity_score" in r for r in results)
    assert all("priority" in r for r in results)
    assert all("recommendation" in r for r in results)

def test_analyze_app(test_client):
    """Test app analysis endpoint"""
    response = test_client.get("/analyze/app/com.badhobuyer")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "b2b_metrics" in data
    
    # Test invalid app
    response = test_client.get("/analyze/app/invalid.app")
    assert response.status_code == 404

def test_analyze_competitors(test_client):
    """Test competitor analysis endpoint"""
    response = test_client.get("/analyze/competitors/com.badhobuyer")
    assert response.status_code == 200
    analyses = response.json()
    assert len(analyses) > 0
    assert all("competitor_id" in a for a in analyses)
    assert all("analysis" in a for a in analyses)

def test_ranking_history(test_client):
    """Test ranking history endpoint"""
    response = test_client.get("/rankings/history/com.badhobuyer?days=30")
    assert response.status_code == 200
    rankings = response.json()
    assert len(rankings) > 0
    assert all("date" in r for r in rankings)
    assert all("keyword" in r for r in rankings)
    assert all("rank" in r for r in rankings)

def test_force_ranking_check(test_client):
    """Test force ranking check endpoint"""
    response = test_client.post("/rankings/check")
    assert response.status_code == 200
    assert response.json()["status"] == "success"