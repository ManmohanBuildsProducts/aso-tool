import pytest
import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment variable
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable not set")

class TestASOTool:
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = requests.get(f"{BACKEND_URL}/")
        assert response.status_code == 200
        assert response.json() == {"message": "ASO Tool API"}

    def test_analyze_endpoint(self):
        """Test the analyze endpoint"""
        test_data = {
            "package_name": "com.badhobuyer",
            "competitor_package_names": ["club.kirana", "com.udaan.android"],
            "keywords": ["wholesale", "b2b", "business"]
        }

        # Start analysis
        response = requests.post(f"{BACKEND_URL}/api/analyze", json=test_data)
        assert response.status_code == 200
        result = response.json()
        assert "task_id" in result
        assert result["status"] == "processing"

        # Test task status polling
        task_id = result["task_id"]
        max_retries = 10
        retry_count = 0
        final_result = None

        while retry_count < max_retries:
            response = requests.get(f"{BACKEND_URL}/api/analyze/{task_id}")
            assert response.status_code == 200
            result = response.json()
            
            if result.get("status") == "completed":
                final_result = result
                break
            elif result.get("status") == "error":
                pytest.fail(f"Analysis failed with error: {result.get('error')}")
            
            retry_count += 1
            time.sleep(2)

        assert final_result is not None, "Analysis did not complete in time"
        assert "data" in final_result
        assert final_result["progress"] == 100

        # Verify data structure
        data = final_result["data"]
        assert "app_metadata" in data
        assert "analysis" in data
        assert "competitor_analysis" in data
        assert "keyword_suggestions" in data
        assert "market_trends" in data
        assert "description_optimization" in data

    def test_search_endpoint(self):
        """Test the search endpoint"""
        response = requests.get(f"{BACKEND_URL}/api/search", params={
            "keyword": "wholesale",
            "limit": 5
        })
        assert response.status_code == 200
        result = response.json()
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_similar_apps_endpoint(self):
        """Test the similar apps endpoint"""
        response = requests.get(f"{BACKEND_URL}/api/similar", params={
            "package_name": "com.badhobuyer",
            "limit": 3
        })
        assert response.status_code == 200
        result = response.json()
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_error_handling(self):
        """Test error handling"""
        # Test invalid package name
        test_data = {
            "package_name": "invalid.package.name",
            "competitor_package_names": [],
            "keywords": []
        }
        response = requests.post(f"{BACKEND_URL}/api/analyze", json=test_data)
        assert response.status_code == 200  # API returns 200 with error in response
        result = response.json()
        assert "error" in result or result["status"] == "processing"

        # Test invalid task ID
        response = requests.get(f"{BACKEND_URL}/api/analyze/invalid_task_id")
        assert response.status_code == 200
        result = response.json()
        assert "error" in result
        assert result["error"] == "Task not found"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])