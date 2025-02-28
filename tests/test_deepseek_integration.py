import os
import pytest
import asyncio
from pathlib import Path
import sys

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.append(str(backend_dir))

from external_integrations.deepseek_analyzer import DeepseekAnalyzer

@pytest.fixture
def analyzer():
    return DeepseekAnalyzer()

@pytest.mark.asyncio
async def test_analyze_app_metadata(analyzer):
    """Test app metadata analysis"""
    app_metadata = {
        "title": "B2B Wholesale App",
        "description": "A comprehensive B2B wholesale platform",
        "category": "Business",
        "keywords": ["wholesale", "b2b", "business"]
    }
    
    result = await analyzer.analyze_app_metadata(app_metadata)
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
async def test_analyze_competitor_metadata(analyzer):
    """Test competitor metadata analysis"""
    app_metadata = {
        "title": "B2B Wholesale App",
        "description": "A comprehensive B2B wholesale platform",
        "category": "Business",
        "keywords": ["wholesale", "b2b", "business"]
    }
    
    competitor_metadata = [{
        "title": "Competitor App",
        "description": "Another B2B platform",
        "category": "Business",
        "keywords": ["b2b", "marketplace"]
    }]
    
    result = await analyzer.analyze_competitor_metadata(app_metadata, competitor_metadata)
    assert result is not None
    assert "analysis" in result
    assert "format" in result
    
    if result.get("format") == "json":
        analysis = result["analysis"]
        assert "competitive_analysis" in analysis
        assert "keyword_gaps" in analysis
        assert "feature_gaps" in analysis
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
    
    if result.get("format") == "json":
        analysis = result["analysis"]
        assert "market_trends" in analysis
        assert "user_preferences" in analysis
        assert "monetization_insights" in analysis
        assert "recommendations" in analysis

@pytest.mark.asyncio
async def test_optimize_description(analyzer):
    """Test description optimization"""
    description = "A B2B wholesale platform for businesses"
    keywords = ["wholesale", "b2b", "marketplace"]
    
    result = await analyzer.optimize_description(description, keywords)
    assert result is not None
    assert "analysis" in result
    assert "format" in result
    
    if result.get("format") == "json":
        analysis = result["analysis"]
        assert "optimized_description" in analysis
        assert "improvements" in analysis
        assert "keyword_usage" in analysis
        assert "recommendations" in analysis

if __name__ == "__main__":
    pytest.main([__file__, "-v"])