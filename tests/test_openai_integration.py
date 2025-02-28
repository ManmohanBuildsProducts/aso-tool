import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.append(str(backend_dir))

from external_integrations.openai_client import query_openai_model

# Load environment variables
load_dotenv(backend_dir / '.env')

def test_openai_api_key():
    """Test if OpenAI API key is configured"""
    assert os.getenv("OPENAI_API_KEY") is not None, "OPENAI_API_KEY not found in environment"

def test_aso_keyword_analysis():
    """Test keyword analysis for ASO"""
    prompt = """Analyze the following fitness app metadata and suggest keywords:
    App Name: FitTrack Pro
    Description: Track workouts, nutrition, and progress. AI-powered personal trainer.
    Category: Health & Fitness
    
    Format response as JSON with:
    - top_keywords: List of 5 best keywords
    - competitor_apps: List of 3 similar apps
    - market_trends: Key market trends
    """
    
    response = query_openai_model(
        model="o3-mini-2025-01-31",
        user_prompt=prompt,
        reasoning_effort="high"
    )
    
    assert "reply" in response
    assert "reasoning" in response
    assert response["model"] == "o3-mini-2025-01-31"

def test_app_description_optimization():
    """Test app description optimization"""
    prompt = """Optimize this app description for better ASO:
    'FitTrack Pro helps you track workouts and diet.'
    
    Format response as JSON with:
    - optimized_description: Enhanced description
    - keywords_used: List of keywords incorporated
    - improvement_reasons: List of improvements made
    """
    
    response = query_openai_model(
        model="o3-mini-2025-01-31",
        user_prompt=prompt,
        reasoning_effort="high"
    )
    
    assert "reply" in response
    assert "reasoning" in response
    assert response["model"] == "o3-mini-2025-01-31"

def test_market_trend_analysis():
    """Test market trend analysis"""
    prompt = """Analyze current trends in fitness apps market:
    
    Format response as JSON with:
    - key_trends: List of top 3 trends
    - user_preferences: Key user preferences
    - monetization_insights: Popular monetization strategies
    """
    
    response = query_openai_model(
        model="o3-mini-2025-01-31",
        user_prompt=prompt,
        reasoning_effort="high"
    )
    
    assert "reply" in response
    assert "reasoning" in response
    assert response["model"] == "o3-mini-2025-01-31"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])