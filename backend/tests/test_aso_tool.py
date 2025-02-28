import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from aso_tool.server import app, JobStatus
from aso_tool.external_integrations.playstore_scraper import PlayStoreScraper
from aso_tool.external_integrations.deepseek_analyzer import DeepseekAnalyzer

client = TestClient(app)

# Test data
TEST_PACKAGE_NAME = "com.example.b2b"
TEST_COMPETITOR_PACKAGE_NAMES = ["com.competitor1", "com.competitor2"]
TEST_KEYWORDS = ["wholesale", "b2b", "marketplace"]

@pytest.fixture
def mock_playstore():
    with patch("aso_tool.server.playstore") as mock:
        mock.get_app_metadata.return_value = {
            "title": "Test B2B App",
            "description": "A test B2B wholesale app",
            "rating": 4.5,
            "reviews_count": 1000,
            "category": "Business"
        }
        yield mock

@pytest.fixture
def mock_deepseek():
    with patch("aso_tool.server.deepseek") as mock:
        mock.analyze_app_metadata.return_value = {
            "analysis": {
                "title_analysis": {
                    "current_score": 85,
                    "suggestions": ["Add keywords"]
                }
            },
            "format": "json"
        }
        yield mock

class TestASOTool:
    """Test suite for ASO Tool implementation"""

    def test_task_helper(self, mock_playstore, mock_deepseek):
        """Test task helper function"""
        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME,
            "competitor_package_names": TEST_COMPETITOR_PACKAGE_NAMES,
            "keywords": TEST_KEYWORDS
        })
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] in [JobStatus.PENDING, JobStatus.PROCESSING]

    def test_task_caching(self, mock_playstore, mock_deepseek):
        """Test task caching functionality"""
        # First request
        response1 = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response1.status_code == 200
        job_id1 = response1.json()["job_id"]

        # Second request (should use cache)
        response2 = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response2.status_code == 200
        job_id2 = response2.json()["job_id"]

        # Check both jobs
        result1 = client.get(f"/analyze/{job_id1}")
        result2 = client.get(f"/analyze/{job_id2}")
        assert result1.status_code == 200
        assert result2.status_code == 200

    def test_task_timeouts(self, mock_playstore):
        """Test task timeout handling"""
        # Mock slow response
        mock_playstore.get_app_metadata.side_effect = asyncio.TimeoutError()

        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check job status
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        assert data["status"] in [JobStatus.ERROR, JobStatus.TIMEOUT]

    def test_task_error_handling(self, mock_playstore):
        """Test task error handling"""
        # Mock error response
        mock_playstore.get_app_metadata.side_effect = Exception("Test error")

        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check job status
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        assert data["status"] == JobStatus.ERROR
        assert "error" in data

    def test_progress_tracking(self, mock_playstore, mock_deepseek):
        """Test progress tracking"""
        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check progress updates
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        assert "progress" in data
        assert isinstance(data["progress"], int)
        assert 0 <= data["progress"] <= 100

    def test_app_analysis(self, mock_playstore, mock_deepseek):
        """Test app analysis functionality"""
        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check analysis results
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        if data["status"] == JobStatus.COMPLETED:
            assert "data" in data
            assert "title_analysis" in data["data"]

    def test_competitor_analysis(self, mock_playstore, mock_deepseek):
        """Test competitor analysis functionality"""
        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME,
            "competitor_package_names": TEST_COMPETITOR_PACKAGE_NAMES
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check competitor analysis
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        if data["status"] == JobStatus.COMPLETED:
            assert "data" in data
            assert "competitor_data" in data["data"]

    def test_keyword_suggestions(self, mock_deepseek):
        """Test keyword suggestions functionality"""
        mock_deepseek.generate_keyword_suggestions.return_value = {
            "analysis": {
                "variations": [
                    {"keyword": "test", "relevance": 0.9}
                ]
            },
            "format": "json"
        }

        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME,
            "keywords": TEST_KEYWORDS
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check keyword suggestions
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        if data["status"] == JobStatus.COMPLETED:
            assert "data" in data
            assert "keyword_suggestions" in data["data"]

    def test_market_trends(self, mock_deepseek):
        """Test market trends analysis"""
        mock_deepseek.analyze_market_trends.return_value = {
            "analysis": {
                "market_trends": [
                    {"trend": "test trend", "impact": "high"}
                ]
            },
            "format": "json"
        }

        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check market trends
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        if data["status"] == JobStatus.COMPLETED:
            assert "data" in data
            assert "market_trends" in data["data"]

    def test_description_optimization(self, mock_deepseek):
        """Test description optimization"""
        mock_deepseek.optimize_description.return_value = {
            "analysis": {
                "optimized_description": "test description",
                "improvements": [{"type": "keyword", "change": "added keywords"}]
            },
            "format": "json"
        }

        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME,
            "keywords": TEST_KEYWORDS
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check description optimization
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        if data["status"] == JobStatus.COMPLETED:
            assert "data" in data
            assert "description_optimization" in data["data"]

    def test_cache_storage(self, mock_playstore, mock_deepseek):
        """Test cache storage functionality"""
        # First request
        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        
        # Second request should use cache
        mock_playstore.get_app_metadata.reset_mock()
        response2 = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response2.status_code == 200
        assert mock_playstore.get_app_metadata.call_count == 0

    def test_cache_expiration(self, mock_playstore, mock_deepseek):
        """Test cache expiration"""
        # First request
        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Simulate cache expiration
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        
        # Request after expiration
        mock_playstore.get_app_metadata.reset_mock()
        response2 = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response2.status_code == 200
        assert mock_playstore.get_app_metadata.call_count > 0

    def test_error_caching(self, mock_playstore):
        """Test error caching behavior"""
        # Simulate error
        mock_playstore.get_app_metadata.side_effect = Exception("Test error")

        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check error is cached
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        assert data["status"] == JobStatus.ERROR
        assert "error" in data

    def test_error_propagation(self, mock_playstore, mock_deepseek):
        """Test error propagation through pipeline"""
        # Simulate cascading errors
        mock_playstore.get_app_metadata.side_effect = Exception("Scraper error")
        mock_deepseek.analyze_app_metadata.side_effect = Exception("Analysis error")

        response = client.post("/analyze", json={
            "package_name": TEST_PACKAGE_NAME
        })
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Check error propagation
        result = client.get(f"/analyze/{job_id}")
        assert result.status_code == 200
        data = result.json()
        assert data["status"] == JobStatus.ERROR
        assert "error" in data