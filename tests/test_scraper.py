import pytest
from backend.scraper import PlayStoreScraper
import aiohttp
from unittest.mock import patch, AsyncMock

@pytest.fixture
def scraper():
    return PlayStoreScraper()

@pytest.mark.asyncio
async def test_search_keyword(scraper):
    """Test Play Store keyword search"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="""
            <html>
                <div class="VfPpkd-EScbFb-JIbuQc">
                    <a href="https://play.google.com/store/apps/details?id=com.test.app">
                        Test App
                    </a>
                </div>
            </html>
        """)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        results = await scraper.search_keyword("test")
        assert len(results) > 0
        assert "package_name" in results[0]
        assert "rank" in results[0]
        
        # Test error handling
        mock_response.status = 404
        results = await scraper.search_keyword("invalid")
        assert len(results) == 0

@pytest.mark.asyncio
async def test_get_app_metadata(scraper):
    """Test app metadata extraction"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="""
            <html>
                <h1 itemprop="name">Test App</h1>
                <div itemprop="description">Test Description</div>
                <a itemprop="genre">Business</a>
            </html>
        """)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        metadata = await scraper.get_app_metadata("com.test.app")
        assert metadata is not None
        assert metadata["name"] == "Test App"
        assert metadata["description"] == "Test Description"
        assert metadata["category"] == "Business"
        
        # Test error handling
        mock_response.status = 404
        metadata = await scraper.get_app_metadata("invalid.app")
        assert metadata is None