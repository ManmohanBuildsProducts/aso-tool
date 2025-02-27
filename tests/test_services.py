import pytest
from app.services.keyword_analyzer import KeywordAnalyzer
from app.services.review_analyzer import ReviewAnalyzer
from app.services.metadata_analyzer import MetadataAnalyzer
from app.services.text_analyzer import TextAnalyzer
from app.services.metadata_tracker import MetadataTracker
import asyncio

# Test data
TEST_TEXT = """
This is a test description for an app.
It includes multiple sentences and paragraphs.

The app has many features and functionalities.
"""

TEST_REVIEWS = [
    {
        "text": "Great app with amazing features!",
        "score": 5,
        "timestamp": "2024-02-27"
    },
    {
        "text": "App needs improvement, crashes often",
        "score": 2,
        "timestamp": "2024-02-27"
    }
]

@pytest.mark.asyncio
async def test_keyword_analyzer():
    analyzer = KeywordAnalyzer()
    analysis = await analyzer.analyze_app_keywords("com.whatsapp")
    
    assert isinstance(analysis, dict)
    assert "title_keywords" in analysis
    assert "top_keywords" in analysis
    assert "keyword_count" in analysis

@pytest.mark.asyncio
async def test_review_analyzer():
    analyzer = ReviewAnalyzer()
    analysis = await analyzer.analyze_reviews(TEST_REVIEWS)
    
    assert isinstance(analysis, dict)
    assert "overall_sentiment" in analysis
    assert "key_topics" in analysis
    assert "recommendations" in analysis

def test_metadata_analyzer():
    analyzer = MetadataAnalyzer()
    
    # Test title analysis
    title_analysis = analyzer._analyze_title("Test App Title")
    assert isinstance(title_analysis, dict)
    assert "length" in title_analysis
    assert "keywords" in title_analysis
    
    # Test description analysis
    desc_analysis = analyzer._analyze_description(TEST_TEXT)
    assert isinstance(desc_analysis, dict)
    assert "length" in desc_analysis
    assert "paragraph_count" in desc_analysis
    assert "keyword_density" in desc_analysis

def test_text_analyzer():
    analyzer = TextAnalyzer()
    
    # Test full description analysis
    analysis = analyzer.analyze_text(TEST_TEXT, "full_description")
    assert isinstance(analysis, dict)
    assert "basic_metrics" in analysis
    assert "detailed_metrics" in analysis
    assert "recommendations" in analysis
    
    # Test title analysis
    title_analysis = analyzer.analyze_text("Test App Title", "title")
    assert isinstance(title_analysis, dict)
    assert title_analysis["basic_metrics"]["character_count"] == 14  # "Test App Title" has 14 characters
    assert title_analysis["basic_metrics"]["word_count"] == 3

@pytest.mark.asyncio
async def test_metadata_tracker():
    tracker = MetadataTracker()
    
    # Test metadata preparation
    test_data = {
        "title": "Test App",
        "description": TEST_TEXT,
        "version": "1.0",
        "score": 4.5,
        "ratings": 1000,
        "reviews": 500
    }
    
    metadata = tracker._prepare_metadata(test_data)
    assert isinstance(metadata, dict)
    assert "timestamp" in metadata
    assert "title" in metadata
    
    # Test change calculation
    changes = tracker._calculate_changes([
        {
            "timestamp": "2024-02-26T00:00:00",
            "ratings": 1000,
            "reviews": 500
        },
        {
            "timestamp": "2024-02-27T00:00:00",
            "ratings": 1100,
            "reviews": 550
        }
    ])
    
    assert isinstance(changes, dict)
    assert "ratings" in changes
    assert changes["ratings"]["absolute"] == 100