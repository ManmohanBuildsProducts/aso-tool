import pytest
from app.services.keyword_analyzer import KeywordAnalyzer
from app.services.review_analyzer import ReviewAnalyzer
from app.services.metadata_analyzer import MetadataAnalyzer
from app.services.text_analyzer import TextAnalyzer
from datetime import datetime, timedelta
import json

# Test data
SAMPLE_REVIEWS = [
    {
        "text": "Great app! Love the new features and interface.",
        "score": 5,
        "timestamp": "2024-02-27"
    },
    {
        "text": "App keeps crashing after the latest update.",
        "score": 2,
        "timestamp": "2024-02-27"
    },
    {
        "text": "Good app but needs better performance.",
        "score": 3,
        "timestamp": "2024-02-27"
    }
]

SAMPLE_METADATA = {
    "title": "Test App - Best Tool for Testing",
    "description": """
    This is a test app that helps you with testing.
    Features:
    - Easy to use interface
    - Fast performance
    - Reliable results
    
    Download now and start testing!
    """,
    "category": "Tools",
    "version": "1.0.0"
}

@pytest.mark.asyncio
class TestKeywordFeatures:
    async def test_keyword_density(self):
        """Test keyword density calculation"""
        analyzer = KeywordAnalyzer()
        analysis = await analyzer.analyze_app_keywords("com.whatsapp")
        
        # Check keyword density calculation
        assert "keyword_density" in analysis
        assert isinstance(analysis["keyword_density"], dict)
        
        # Verify density values are between 0 and 1
        for density in analysis["keyword_density"].values():
            assert 0 <= density <= 1

    async def test_keyword_relevance(self):
        """Test keyword relevance scoring"""
        analyzer = KeywordAnalyzer()
        analysis = await analyzer.analyze_app_keywords("com.whatsapp")
        
        # Check relevance scores
        assert "relevance_scores" in analysis
        for score in analysis["relevance_scores"].values():
            assert 0 <= score <= 100

    async def test_keyword_trends(self):
        """Test keyword trend analysis"""
        analyzer = KeywordAnalyzer()
        trends = await analyzer.compare_keywords("com.whatsapp", ["org.telegram.messenger"])
        
        assert "timestamp" in trends
        assert "keyword_trends" in trends
        for keyword, data in trends["keyword_trends"].items():
            assert "difficulty_score" in data
            assert "search_volume" in data
            assert "ranking_potential" in data

class TestReviewAnalysis:
    def test_sentiment_accuracy(self):
        """Test sentiment analysis accuracy"""
        analyzer = ReviewAnalyzer()
        
        # Test positive sentiment
        positive_result = analyzer._analyze_sentiment(
            "This is an amazing app, absolutely love it!", 5
        )
        assert positive_result["compound"] > 0.5
        
        # Test negative sentiment
        negative_result = analyzer._analyze_sentiment(
            "Terrible app, constantly crashes and loses data", 1
        )
        assert negative_result["compound"] < -0.5
        
        # Test neutral sentiment
        neutral_result = analyzer._analyze_sentiment(
            "The app works as expected", 3
        )
        assert -0.2 <= neutral_result["compound"] <= 0.2

    def test_feature_extraction(self):
        """Test feature extraction from reviews"""
        analyzer = ReviewAnalyzer()
        
        # Test feature categorization
        features = analyzer._analyze_feature_mentions(
            "The UI is great but performance is slow",
            {}
        )
        assert "ui" in str(features).lower()
        assert "performance" in str(features).lower()

    @pytest.mark.asyncio
    async def test_review_aggregation(self):
        """Test review aggregation and statistics"""
        analyzer = ReviewAnalyzer()
        analysis = await analyzer.analyze_reviews(SAMPLE_REVIEWS)
        
        assert "overall_sentiment" in analysis
        assert "sentiment_distribution" in analysis
        assert abs(analysis["overall_sentiment"]["positive_ratio"] - 0.33) < 0.1
        assert abs(analysis["overall_sentiment"]["negative_ratio"] - 0.33) < 0.1

class TestMetadataAnalysis:
    def test_title_optimization(self):
        """Test title optimization analysis"""
        analyzer = MetadataAnalyzer()
        title_analysis = analyzer._analyze_title(SAMPLE_METADATA["title"])
        
        assert "length_score" in title_analysis
        assert "keyword_density" in title_analysis
        assert "overall_score" in title_analysis
        assert 0 <= title_analysis["overall_score"] <= 1

    def test_description_structure(self):
        """Test description structure analysis"""
        analyzer = MetadataAnalyzer()
        desc_analysis = analyzer._analyze_description(SAMPLE_METADATA["description"])
        
        assert desc_analysis["has_feature_list"]
        assert desc_analysis["has_calls_to_action"]
        assert desc_analysis["paragraph_count"] > 1

    def test_keyword_consistency(self):
        """Test keyword consistency between title and description"""
        analyzer = MetadataAnalyzer()
        keywords = analyzer._analyze_keywords(
            SAMPLE_METADATA["title"],
            SAMPLE_METADATA["description"]
        )
        
        assert len(keywords["common_keywords"]) > 0
        assert "test" in keywords["common_keywords"]

class TestTextAnalysis:
    def test_readability_metrics(self):
        """Test readability metrics calculation"""
        analyzer = TextAnalyzer()
        analysis = analyzer.analyze_text(SAMPLE_METADATA["description"], "full_description")
        
        metrics = analysis["detailed_metrics"]
        assert "avg_word_length" in metrics
        assert "avg_sentence_length" in metrics
        assert metrics["avg_word_length"] > 0
        assert metrics["avg_sentence_length"] > 0

    def test_text_optimization(self):
        """Test text optimization recommendations"""
        analyzer = TextAnalyzer()
        analysis = analyzer.analyze_text("Short text", "full_description")
        
        assert "recommendations" in analysis
        assert len(analysis["recommendations"]) > 0
        assert any("add more content" in rec.lower() for rec in analysis["recommendations"])

    def test_character_limits(self):
        """Test character limit validation"""
        analyzer = TextAnalyzer()
        
        # Test title limits
        title_analysis = analyzer.analyze_text("Very Long Title That Exceeds The Recommended Length", "title")
        assert any("reduce" in rec.lower() for rec in title_analysis["recommendations"])
        
        # Test description limits
        short_desc = analyzer.analyze_text("Too short", "full_description")
        assert any("add more" in rec.lower() for rec in short_desc["recommendations"])