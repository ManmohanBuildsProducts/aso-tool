import pytest
from backend.scheduler import RankingScheduler
from unittest.mock import Mock, AsyncMock
import asyncio

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def scheduler(mock_db):
    return RankingScheduler(mock_db)

@pytest.mark.asyncio
async def test_run_ranking_check(scheduler):
    """Test ranking check execution"""
    # Mock database data
    mock_apps = [
        {"_id": "1", "package_name": "com.test.app1"},
        {"_id": "2", "package_name": "com.test.app2"}
    ]
    mock_keywords = [
        {"keyword": "test1"},
        {"keyword": "test2"}
    ]
    
    # Setup mocks
    scheduler.db.apps.find = AsyncMock(return_value=AsyncMock(
        to_list=AsyncMock(return_value=mock_apps)
    ))
    scheduler.db.keywords.find = AsyncMock(return_value=AsyncMock(
        to_list=AsyncMock(return_value=mock_keywords)
    ))
    scheduler.scraper.search_keyword = AsyncMock(return_value=[
        {"package_name": "com.test.app1", "rank": 1},
        {"package_name": "com.test.app2", "rank": 2}
    ])
    scheduler.scraper.get_app_metadata = AsyncMock(return_value={
        "name": "Test App",
        "description": "Test Description"
    })
    scheduler.db.rankings.insert_one = AsyncMock()
    scheduler.db.apps.update_one = AsyncMock()
    
    # Run check
    await scheduler._run_ranking_check()
    
    # Verify rankings were stored
    assert scheduler.db.rankings.insert_one.call_count > 0
    
    # Verify metadata was updated
    assert scheduler.db.apps.update_one.call_count > 0

@pytest.mark.asyncio
async def test_scheduler_start_stop(scheduler):
    """Test scheduler start/stop functionality"""
    # Mock _run_ranking_check to avoid actual execution
    scheduler._run_ranking_check = AsyncMock()
    
    # Start scheduler
    start_task = asyncio.create_task(scheduler.start())
    
    # Wait a bit
    await asyncio.sleep(0.1)
    
    # Stop scheduler
    await scheduler.stop()
    
    # Wait for start task to complete
    await start_task
    
    # Verify ranking check was called
    assert scheduler._run_ranking_check.called

@pytest.mark.asyncio
async def test_force_check(scheduler):
    """Test force check functionality"""
    scheduler._run_ranking_check = AsyncMock()
    
    await scheduler.force_check()
    
    assert scheduler._run_ranking_check.called