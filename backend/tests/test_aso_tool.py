import pytest
import aiohttp
import asyncio
from datetime import datetime
import os
import json

# Use localhost since we're testing internally
BACKEND_URL = "http://localhost:8001"

class TestASOTool:
    @pytest.fixture
    async def session(self):
        async with aiohttp.ClientSession() as session:
            yield session

    @pytest.mark.asyncio
    async def test_root_endpoint(self, session):
        """Test the root endpoint"""
        async with session.get(f"{BACKEND_URL}/api/") as response:
            assert response.status == 200
            data = await response.json()
            assert "message" in data
            assert data["message"] == "ASO Tool API"

    @pytest.mark.asyncio
    async def test_analyze_endpoint(self, session):
        """Test the analyze endpoint"""
        test_data = {
            "package_name": "com.badhobuyer",
            "competitor_package_names": ["club.kirana"],
            "keywords": ["wholesale", "b2b"]
        }

        # Create analysis job
        async with session.post(
            f"{BACKEND_URL}/api/analyze",
            json=test_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "task_id" in data
            assert "status" in data
            assert data["status"] == "processing"
            task_id = data["task_id"]

        # Wait and check job status
        max_retries = 10
        retry_count = 0
        job_completed = False

        while retry_count < max_retries and not job_completed:
            await asyncio.sleep(2)  # Wait 2 seconds between checks
            async with session.get(
                f"{BACKEND_URL}/api/analyze/{task_id}"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "status" in data
                
                if data["status"] == "completed":
                    job_completed = True
                    # Verify job result structure
                    assert "app_data" in data
                    assert "analysis" in data
                    break
                elif data["status"] == "error":
                    pytest.fail(f"Job failed with error: {data.get('error')}")
                
                retry_count += 1

        assert job_completed, "Job did not complete within expected time"

    @pytest.mark.asyncio
    async def test_search_endpoint(self, session):
        """Test the search endpoint"""
        test_keyword = "wholesale"
        async with session.get(
            f"{BACKEND_URL}/api/search?keyword={test_keyword}"
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "results" in data
            assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_similar_apps_endpoint(self, session):
        """Test the similar apps endpoint"""
        test_package = "com.badhobuyer"
        async with session.get(
            f"{BACKEND_URL}/api/similar?package_name={test_package}"
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "results" in data
            assert isinstance(data["results"], list)

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
            task_id = data["task_id"]

        # Check if job fails appropriately
        await asyncio.sleep(2)
        async with session.get(
            f"{BACKEND_URL}/api/analyze/{task_id}"
        ) as response:
            data = await response.json()
            assert "status" in data
            assert data["status"] in ["error", "processing"]

    @pytest.mark.asyncio
    async def test_caching_mechanism(self, session):
        """Test the caching mechanism"""
        # Make two consecutive requests for the same package
        test_package = "com.badhobuyer"
        
        # First request
        start_time1 = datetime.now()
        async with session.get(
            f"{BACKEND_URL}/api/similar?package_name={test_package}"
        ) as response1:
            assert response1.status == 200
            data1 = await response1.json()
            time1 = (datetime.now() - start_time1).total_seconds()

        await asyncio.sleep(1)

        # Second request (should be cached)
        start_time2 = datetime.now()
        async with session.get(
            f"{BACKEND_URL}/api/similar?package_name={test_package}"
        ) as response2:
            assert response2.status == 200
            data2 = await response2.json()
            time2 = (datetime.now() - start_time2).total_seconds()

        # Second request should be faster due to caching
        assert time2 <= time1, "Cached request should be faster"
        assert data1 == data2, "Cached data should match original data"