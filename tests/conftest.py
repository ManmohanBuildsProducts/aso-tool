import pytest
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def mongo_client():
    """Create a MongoDB client for testing."""
    mongo_url = os.environ.get('MONGO_URL', "").replace(
        "test_database", "test_aso_database"
    )
    client = AsyncIOMotorClient(mongo_url)
    yield client
    client.close()