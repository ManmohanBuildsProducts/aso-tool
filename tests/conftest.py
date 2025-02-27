import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

@pytest.fixture
def sample_app_data() -> Dict[str, Any]:
    return {
        "title": "Test App",
        "description": "This is a test app description",
        "score": 4.5,
        "ratings": 1000,
        "reviews": 500,
        "installs": "10,000+",
        "version": "1.0.0",
        "updated": int(datetime.now().timestamp()),
        "size": "15M",
        "category": "Tools"
    }

@pytest.fixture
def sample_reviews() -> List[Dict[str, Any]]:
    return [
        {
            "text": "Great app with amazing features!",
            "score": 5,
            "timestamp": datetime.now().isoformat()
        },
        {
            "text": "App needs improvement in performance",
            "score": 3,
            "timestamp": datetime.now().isoformat()
        },
        {
            "text": "Terrible app, keeps crashing",
            "score": 1,
            "timestamp": datetime.now().isoformat()
        }
    ]

@pytest.fixture
def sample_keywords() -> List[str]:
    return [
        "test",
        "app",
        "tool",
        "performance",
        "feature"
    ]

@pytest.fixture
def sample_competitor_data() -> List[Dict[str, Any]]:
    return [
        {
            "app_id": "com.competitor1",
            "title": "Competitor 1",
            "score": 4.2,
            "installs": "8,000+"
        },
        {
            "app_id": "com.competitor2",
            "title": "Competitor 2",
            "score": 4.7,
            "installs": "12,000+"
        }
    ]

@pytest.fixture
def mock_app_scraper(monkeypatch):
    """Mock app scraper to avoid actual API calls"""
    async def mock_get_app_details(app_id: str):
        return {
            "title": f"Test App {app_id}",
            "description": "Test description",
            "score": 4.5,
            "ratings": 1000,
            "reviews": 500,
            "installs": "10,000+",
            "version": "1.0.0"
        }
    
    from app.services.app_scraper import AppScraper
    monkeypatch.setattr(AppScraper, "get_app_details", mock_get_app_details)

@pytest.fixture
def mock_review_analyzer(monkeypatch):
    """Mock review analyzer for consistent results"""
    async def mock_analyze_reviews(reviews):
        return {
            "overall_sentiment": {
                "compound": 0.5,
                "positive_ratio": 0.6,
                "negative_ratio": 0.2,
                "neutral_ratio": 0.2
            },
            "key_topics": ["feature", "performance", "bug"],
            "recommendations": ["Improve performance", "Fix bugs"]
        }
    
    from app.services.review_analyzer import ReviewAnalyzer
    monkeypatch.setattr(ReviewAnalyzer, "analyze_reviews", mock_analyze_reviews)

@pytest.fixture
def mock_keyword_analyzer(monkeypatch):
    """Mock keyword analyzer for consistent results"""
    async def mock_analyze_keywords(app_id):
        return {
            "title_keywords": ["test", "app"],
            "description_keywords": ["feature", "performance"],
            "top_keywords": {
                "test": 0.8,
                "app": 0.6,
                "feature": 0.4
            }
        }
    
    from app.services.keyword_analyzer import KeywordAnalyzer
    monkeypatch.setattr(KeywordAnalyzer, "analyze_app_keywords", mock_analyze_keywords)

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_app_client():
    """Create a test client for the FastAPI app"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

@pytest.fixture
def mock_cache(monkeypatch):
    """Mock cache for testing cache-related functionality"""
    cache = {}
    
    def mock_get(key):
        return cache.get(key)
    
    def mock_set(key, value, expire=None):
        cache[key] = value
    
    def mock_delete(key):
        if key in cache:
            del cache[key]
    
    # Mock cache methods
    monkeypatch.setattr("app.core.cache.get", mock_get)
    monkeypatch.setattr("app.core.cache.set", mock_set)
    monkeypatch.setattr("app.core.cache.delete", mock_delete)
    
    return cache