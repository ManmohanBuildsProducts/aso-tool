import os
import pytest
import json
from backend.deepseek_analyzer import DeepseekAnalyzer

@pytest.fixture
def analyzer():
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        pytest.skip("DEEPSEEK_API_KEY environment variable not set")
    return DeepseekAnalyzer(api_key)

@pytest.mark.asyncio
async def test_analyze_app_metadata(analyzer):
    """Test app metadata analysis"""
    app_metadata = {
        "title": "B2B Wholesale App",
        "description": "A comprehensive B2B wholesale platform",
        "category": "Business",
        "keywords": ["wholesale", "b2b", "business"]
    }
    competitor_metadata = []
    
    result = await analyzer.analyze_app_metadata(app_metadata, competitor_metadata)
    assert result is not None
    assert "analysis" in result
    assert "format" in result
    
    if result.get("format") == "json":
        analysis = result["analysis"]
        assert "title_analysis" in analysis
        assert "description_analysis" in analysis
        assert "keyword_opportunities" in analysis
        assert "recommendations" in analysis

@pytest.mark.asyncio
async def test_generate_keyword_suggestions(analyzer):
    """Test keyword suggestion generation"""
    result = await analyzer.generate_keyword_suggestions("wholesale b2b")
    assert result is not None
    assert "analysis" in result
    assert "format" in result
    
    if result.get("format") == "json":
        analysis = result["analysis"]
        assert "variations" in analysis
        assert "long_tail" in analysis
        assert "related_terms" in analysis
        assert "recommendations" in analysis

@pytest.mark.asyncio
async def test_analyze_market_trends(analyzer):
    """Test market trend analysis"""
    result = await analyzer.analyze_market_trends()
    assert result is not None
    assert "analysis" in result
    assert "format" in result