import pytest
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')

class TestASOTool:
    @pytest.fixture
    async def session(self):
        async with aiohttp.ClientSession() as session:
            yield session

    @pytest.mark.asyncio
    async def test_root_endpoint(self, session):
        """Test root endpoint"""
        async with session.get(f"{BACKEND_URL}/api/") as response:
            assert response.status == 200
            data = await response.json()
            assert data["message"] == "ASO Tool API"

    @pytest.mark.asyncio
    async def test_analyze_app(self, session):
        """Test app analysis workflow"""
        # Test data
        test_data = {
            "package_name": "com.badhobuyer",
            "competitor_package_names": ["club.kirana", "com.udaan.android"],
            "keywords": ["wholesale", "b2b", "business"]
        }

        # Start analysis
        print("Starting app analysis...")
        async with session.post(
            f"{BACKEND_URL}/api/analyze",
            json=test_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "task_id" in data
            assert data["status"] == "processing"
            task_id = data["task_id"]

        # Poll for results
        print("Polling for results...")
        max_retries = 30
        retry_count = 0
        result_data = None

        while retry_count < max_retries:
            async with session.get(
                f"{BACKEND_URL}/api/analyze/{task_id}"
            ) as response:
                assert response.status == 200
                result = await response.json()
                
                if result.get("status") == "completed":
                    result_data = result.get("data")
                    break
                elif result.get("status") == "error":
                    pytest.fail(f"Analysis failed: {result.get('error')}")
                    break
                
                print(f"Progress: {result.get('progress')}%")
                await asyncio.sleep(2)
                retry_count += 1

        assert result_data is not None, "Analysis did not complete in time"
        
        # Validate result structure
        assert "app_metadata" in result_data
        assert "analysis" in result_data
        assert "competitor_analysis" in result_data
        assert "keyword_suggestions" in result_data
        assert "market_trends" in result_data

        # Validate app metadata
        app_metadata = result_data["app_metadata"]
        assert "title" in app_metadata
        assert "description" in app_metadata
        assert "rating" in app_metadata
        assert "category" in app_metadata

    @pytest.mark.asyncio
    async def test_search_keyword(self, session):
        """Test keyword search"""
        keyword = "wholesale"
        async with session.get(
            f"{BACKEND_URL}/api/search?keyword={keyword}&limit=5"
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "results" in data
            assert len(data["results"]) <= 5
            
            if data["results"]:
                app = data["results"][0]
                assert "name" in app
                assert "package_name" in app
                assert "rating" in app

    @pytest.mark.asyncio
    async def test_similar_apps(self, session):
        """Test similar apps endpoint"""
        package_name = "com.badhobuyer"
        async with session.get(
            f"{BACKEND_URL}/api/similar?package_name={package_name}&limit=5"
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "results" in data
            assert len(data["results"]) <= 5
            
            if data["results"]:
                app = data["results"][0]
                assert "name" in app
                assert "package_name" in app
                assert "rating" in app

    @pytest.mark.asyncio
    async def test_error_handling(self, session):
        """Test error handling"""
        # Test with invalid package name
        test_data = {
            "package_name": "invalid.package.name",
            "competitor_package_names": [],
            "keywords": []
        }

        async with session.post(
            f"{BACKEND_URL}/api/analyze",
            json=test_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "task_id" in data

            # Check task status
            task_id = data["task_id"]
            async with session.get(
                f"{BACKEND_URL}/api/analyze/{task_id}"
            ) as status_response:
                status_data = await status_response.json()
                # Either the task should be in processing state or error state
                assert status_data["status"] in ["processing", "error"]

        # Test with invalid task ID
        async with session.get(
            f"{BACKEND_URL}/api/analyze/invalid_task_id"
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "error" in data
