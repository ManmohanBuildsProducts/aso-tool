import pytest
from datetime import datetime
from backend.aso_analyzer import ASOAnalyzer
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def aso_analyzer(mock_db):
    return ASOAnalyzer(mock_db)

@pytest.mark.asyncio
async def test_analyze_keyword_opportunity():
    """Test keyword opportunity analysis"""
    analyzer = ASOAnalyzer(None)
    
    # Test high opportunity keyword
    high_opp_data = {
        "search_volume_score": 90,
        "difficulty_score": 30,
        "current_rank": None
    }
    result = await analyzer.analyze_keyword_opportunity(high_opp_data)
    assert result["priority"] == "high"
    assert "opportunity_score" in result
    assert "recommendation" in result
    
    # Test low opportunity keyword
    low_opp_data = {
        "search_volume_score": 20,
        "difficulty_score": 80,
        "current_rank": 50
    }
    result = await analyzer.analyze_keyword_opportunity(low_opp_data)
    assert result["priority"] == "low"
    
    # Test error handling
    result = await analyzer.analyze_keyword_opportunity({})
    assert result["priority"] == "low"
    assert result["opportunity_score"] == 0

@pytest.mark.asyncio
async def test_analyze_competitor_metadata():
    """Test competitor metadata analysis"""
    analyzer = ASOAnalyzer(None)
    
    app_metadata = {
        "title": "B2B Wholesale App",
        "full_description": "A great wholesale app for business"
    }
    
    competitor_metadata = {
        "title": "B2B Wholesale Distributor App",
        "full_description": "The best wholesale distributor app for business and enterprises"
    }
    
    result = await analyzer.analyze_competitor_metadata(app_metadata, competitor_metadata)
    
    assert "title" in result
    assert "description" in result
    assert "distributor" in result["title"]["missing_keywords"]
    
    # Test error handling
    result = await analyzer.analyze_competitor_metadata({}, {})
    assert isinstance(result, dict)

@pytest.mark.asyncio
async def test_generate_aso_recommendations(mock_db):
    """Test ASO recommendations generation"""
    analyzer = ASOAnalyzer(mock_db)
    
    # Mock app data
    mock_app = {
        "metadata": {
            "title": "Short Title",  # Under 50 chars
            "full_description": "Short description",  # Under 3000 chars
            "screenshots": ["1.jpg", "2.jpg"]  # Under 8 screenshots
        }
    }
    
    # Setup mock
    mock_db.apps.find_one = AsyncMock(return_value=mock_app)
    
    recommendations = await analyzer.generate_aso_recommendations("test_id")
    
    assert len(recommendations) == 3  # Should have title, description, and screenshot recommendations
    assert any(r["category"] == "title" for r in recommendations)
    assert any(r["category"] == "description" for r in recommendations)
    assert any(r["category"] == "screenshots" for r in recommendations)
    
    # Test error handling
    mock_db.apps.find_one = AsyncMock(return_value=None)
    recommendations = await analyzer.generate_aso_recommendations("invalid_id")
    assert len(recommendations) == 0

@pytest.mark.asyncio
async def test_analyze_b2b_specific_metrics(mock_db):
    """Test B2B-specific metrics analysis"""
    analyzer = ASOAnalyzer(mock_db)
    
    # Mock app data
    mock_app = {
        "metadata": {
            "title": "B2B Wholesale App",
            "full_description": "A wholesale distributor app for business"
        }
    }
    
    # Mock rankings data
    mock_rankings = [
        {"keyword": "wholesale", "rank": 5},
        {"keyword": "b2b", "rank": 10},
        {"keyword": "distributor", "rank": 15}
    ]
    
    # Setup mocks
    mock_db.apps.find_one = AsyncMock(return_value=mock_app)
    mock_db.rankings.find = AsyncMock(return_value=AsyncMock(
        to_list=AsyncMock(return_value=mock_rankings)
    ))
    
    result = await analyzer.analyze_b2b_specific_metrics("test_id")
    
    assert "keyword_coverage" in result
    assert "competitor_comparison" in result
    assert "wholesale" in result["keyword_coverage"]
    assert "b2b" in result["keyword_coverage"]
    
    # Test error handling
    mock_db.apps.find_one = AsyncMock(return_value=None)
    result = await analyzer.analyze_b2b_specific_metrics("invalid_id")
    assert "keyword_coverage" in result
    assert len(result["keyword_coverage"]) == 0