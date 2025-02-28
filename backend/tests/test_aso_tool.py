import pytest
import aiohttp
import asyncio
import os
from datetime import datetime
import json

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', '')

class TestASOTool:
    @pytest.fixture
    def test_data(self):
        return {
            "package_name": "com.badhobuyer",
            "competitor_package_names": ["club.kirana", "com.udaan.android"],
            "keywords": ["wholesale", "b2b", "business"]
        }

    async def test_analyze_endpoint(self, test_data):
        """Test the /analyze endpoint"""
        async with aiohttp.ClientSession() as session:
            # Create analysis task
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
                max_retries = 10
                retry_count = 0
                while retry_count < max_retries:
                    async with session.get(
                        f"{BACKEND_URL}/api/analyze/{task_id}"
                    ) as status_response:
                        assert status_response.status == 200
                        status_data = await status_response.json()
                        
                        if status_data["status"] == "completed":
                            assert "data" in status_data
                            assert status_data["progress"] == 100
                            return
                        elif status_data["status"] == "error":
                            pytest.fail(f"Task failed: {status_data['error']}")
                        
                        await asyncio.sleep(2)
                        retry_count += 1

                pytest.fail("Task did not complete in time")

    async def test_search_endpoint(self):
        """Test the /search endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BACKEND_URL}/api/search",
                params={"keyword": "wholesale", "limit": 5}
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "results" in data
                assert isinstance(data["results"], list)

    async def test_similar_apps_endpoint(self):
        """Test the /similar endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BACKEND_URL}/api/similar",
                params={"package_name": "com.badhobuyer", "limit": 5}
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "results" in data
                assert isinstance(data["results"], list)

    async def test_error_handling(self):
        """Test error handling"""
        async with aiohttp.ClientSession() as session:
            # Test invalid package name
            async with session.post(
                f"{BACKEND_URL}/api/analyze",
                json={
                    "package_name": "invalid.package.name",
                    "competitor_package_names": [],
                    "keywords": []
                }
            ) as response:
                assert response.status == 200  # API returns 200 with error in response
                data = await response.json()
                assert "error" in data or "task_id" in data

            # Test invalid task ID
            async with session.get(
                f"{BACKEND_URL}/api/analyze/invalid_task_id"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "error" in data

@pytest.mark.asyncio
async def test_aso_tool():
    """Run all ASO tool tests"""
    test_instance = TestASOTool()
    test_data = test_instance.test_data()
    
    print("\n🔍 Starting ASO Tool API Tests...")
    
    try:
        print("\n✨ Testing analyze endpoint...")
        await test_instance.test_analyze_endpoint(test_data)
        print("✅ Analyze endpoint test passed")
        
        print("\n✨ Testing search endpoint...")
        await test_instance.test_search_endpoint()
        print("✅ Search endpoint test passed")
        
        print("\n✨ Testing similar apps endpoint...")
        await test_instance.test_similar_apps_endpoint()
        print("✅ Similar apps endpoint test passed")
        
        print("\n✨ Testing error handling...")
        await test_instance.test_error_handling()
        print("✅ Error handling test passed")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_aso_tool())