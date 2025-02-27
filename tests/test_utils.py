import pytest
from app.services.app_scraper import AppScraper
from datetime import datetime

@pytest.mark.asyncio
async def test_app_scraper():
    scraper = AppScraper()
    
    # Test valid app ID
    app_details = await scraper.get_app_details("com.whatsapp")
    assert isinstance(app_details, dict)
    assert "title" in app_details
    assert "description" in app_details
    
    # Test invalid app ID
    with pytest.raises(Exception):
        await scraper.get_app_details("invalid.app.id")

def test_timestamp_parsing():
    from app.services.metadata_tracker import MetadataTracker
    
    tracker = MetadataTracker()
    
    # Test valid timestamp
    valid_timestamp = "2024-02-27T00:00:00"
    parsed = tracker.parse_timestamp(valid_timestamp)
    assert isinstance(parsed, str)
    assert parsed == "2024-02-27"
    
    # Test invalid timestamp
    invalid_timestamp = "invalid"
    parsed = tracker.parse_timestamp(invalid_timestamp)
    assert parsed == ""

def test_keyword_extraction():
    from app.services.keyword_analyzer import KeywordAnalyzer
    
    analyzer = KeywordAnalyzer()
    
    # Test keyword extraction
    text = "This is a test app with some keywords"
    keywords = analyzer._extract_keywords(text)
    assert isinstance(keywords, list)
    assert "test" in keywords
    assert "app" in keywords
    assert "keywords" in keywords
    
    # Test stop words removal
    assert "is" not in keywords
    assert "with" not in keywords

def test_sentiment_calculation():
    from app.services.review_analyzer import ReviewAnalyzer
    
    analyzer = ReviewAnalyzer()
    
    # Test positive sentiment
    positive_text = "Great app with amazing features!"
    positive_sentiment = analyzer._analyze_sentiment(positive_text, 5)
    assert positive_sentiment["compound"] > 0
    
    # Test negative sentiment
    negative_text = "Terrible app, keeps crashing"
    negative_sentiment = analyzer._analyze_sentiment(negative_text, 1)
    assert negative_sentiment["compound"] < 0

def test_text_metrics():
    from app.services.text_analyzer import TextAnalyzer
    
    analyzer = TextAnalyzer()
    
    text = """This is a test description.
It has multiple sentences.

And multiple paragraphs too."""
    
    analysis = analyzer._detailed_analysis(text)
    assert analysis["sentence_count"] == 3
    assert analysis["paragraph_count"] == 2
    assert isinstance(analysis["avg_word_length"], float)
    assert isinstance(analysis["keyword_density"], dict)