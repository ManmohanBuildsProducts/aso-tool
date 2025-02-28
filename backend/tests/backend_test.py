import pytest
import aiohttp
import asyncio
from typing import Dict
import os
import json

# Get the backend URL from environment variable
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')

@pytest.mark.asyncio
async def test_root_endpoint():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/api/") as response:
            assert response.status == 200
            data = await response.json()
            assert data["message"] == "ASO Tool API"

@pytest.mark.asyncio
async def test_analyze_endpoint():
    test_data = {
        "package_name": "com.badhobuyer",
        "competitor_package_names": ["club.kirana", "com.udaan.android"],
        "keywords": ["wholesale", "b2b", "business"]
    }
    
    async with aiohttp.ClientSession() as session:
        # Test analyze endpoint
        async with session.post(
            f"{BACKEND_URL}/api/analyze",
            json=test_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "task_id" in data
            assert data["status"] == "processing"
            
            task_id = data["task_id"]
            
            # Test task status endpoint
            max_retries = 10
            retry_count = 0
            while retry_count < max_retries:
                async with session.get(
                    f"{BACKEND_URL}/api/analyze/{task_id}"
                ) as status_response:
                    assert status_response.status == 200
                    status_data = await status_response.json()
                    
                    if status_data.get("status") == "completed":
                        assert "data" in status_data
                        assert isinstance(status_data["data"], dict)
                        assert "app_metadata" in status_data["data"]
                        assert "analysis" in status_data["data"]
                        break
                    elif status_data.get("status") == "error":
                        pytest.fail(f"Task failed with error: {status_data.get('error')}")
                        break
                        
                retry_count += 1
                await asyncio.sleep(2)
            
            if retry_count >= max_retries:
                pytest.fail("Task did not complete within expected time")

@pytest.mark.asyncio
async def test_search_endpoint():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BACKEND_URL}/api/search",
            params={"keyword": "wholesale", "limit": 5}
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "results" in data
            assert isinstance(data["results"], list)

@pytest.mark.asyncio
async def test_similar_apps_endpoint():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BACKEND_URL}/api/similar",
            params={"package_name": "com.badhobuyer", "limit": 5}
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "results" in data
            assert isinstance(data["results"], list)

@pytest.mark.asyncio
async def test_error_handling():
    async with aiohttp.ClientSession() as session:
        # Test invalid package name
        test_data = {
            "package_name": "invalid.package.name",
            "competitor_package_names": [],
            "keywords": []
        }
        
        async with session.post(
            f"{BACKEND_URL}/api/analyze",
            json=test_data
        ) as response:
            data = await response.json()
            assert "task_id" in data
            
            # Check if task fails with appropriate error
            async with session.get(
                f"{BACKEND_URL}/api/analyze/{data['task_id']}"
            ) as status_response:
                status_data = await status_response.json()
                assert status_data.get("status") in ["error", "processing"]

@pytest.mark.asyncio
async def test_concurrent_tasks():
    test_packages = [
        "com.badhobuyer",
        "club.kirana",
        "com.udaan.android"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for package in test_packages:
            test_data = {
                "package_name": package,
                "competitor_package_names": [],
                "keywords": ["wholesale", "b2b"]
            }
            tasks.append(
                session.post(
                    f"{BACKEND_URL}/api/analyze",
                    json=test_data
                )
            )
        
        responses = await asyncio.gather(*tasks)
        task_ids = []
        
        for response in responses:
            data = await response.json()
            assert "task_id" in data
            task_ids.append(data["task_id"])
        
        # Monitor all tasks
        max_retries = 15
        retry_count = 0
        completed_tasks = set()
        
        while retry_count < max_retries and len(completed_tasks) < len(task_ids):
            status_tasks = []
            for task_id in task_ids:
                if task_id not in completed_tasks:
                    status_tasks.append(
                        session.get(f"{BACKEND_URL}/api/analyze/{task_id}")
                    )
            
            status_responses = await asyncio.gather(*status_tasks)
            for response in status_responses:
                status_data = await response.json()
                if status_data.get("status") == "completed":
                    completed_tasks.add(status_data["task_id"])
                elif status_data.get("status") == "error":
                    pytest.fail(f"Task failed with error: {status_data.get('error')}")
            
            retry_count += 1
            await asyncio.sleep(2)
        
        assert len(completed_tasks) == len(task_ids), "Not all tasks completed successfully"