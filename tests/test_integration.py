import pytest
from fastapi.testclient import TestClient
from app.main import app
import asyncio
from datetime import datetime, timedelta

client = TestClient(app)

class TestIntegrationFlows:
    def test_complete_analysis_flow(self):
        """Test complete app analysis flow"""
        # 1. Analyze main app
        app_response = client.get("/analyze/app/com.whatsapp")
        assert app_response.status_code == 200
        app_data = app_response.json()
        
        # 2. Analyze competitors
        competitor_response = client.post(
            "/analyze/competitors/compare",
            json={
                "app_id": "com.whatsapp",
                "competitor_ids": ["org.telegram.messenger"]
            }
        )
        assert competitor_response.status_code == 200
        competitor_data = competitor_response.json()
        
        # 3. Analyze keywords
        keyword_response = client.post(
            "/analyze/keywords/discover",
            json={
                "app_id": "com.whatsapp",
                "competitor_ids": ["org.telegram.messenger"]
            }
        )
        assert keyword_response.status_code == 200
        keyword_data = keyword_response.json()
        
        # 4. Verify data consistency
        assert app_data["data"]["title"] == competitor_data["comparison"]["main_app"]["details"]["title"]
        assert "main_app" in keyword_data["analysis"]

    def test_metadata_tracking_flow(self):
        """Test metadata tracking and history flow"""
        # 1. Get initial metadata
        initial_response = client.get("/track/track/com.whatsapp")
        assert initial_response.status_code == 200
        initial_data = initial_response.json()
        
        # 2. Wait and get updated metadata
        asyncio.sleep(1)
        updated_response = client.get("/track/track/com.whatsapp")
        assert updated_response.status_code == 200
        updated_data = updated_response.json()
        
        # 3. Verify tracking
        assert initial_data["tracking_data"]["current_metadata"]["record_date"] != \
               updated_data["tracking_data"]["current_metadata"]["record_date"]
        assert "changes" in updated_data["tracking_data"]

    def test_review_analysis_flow(self):
        """Test review analysis and sentiment tracking flow"""
        reviews = [
            {
                "text": "Great app with amazing features!",
                "score": 5,
                "timestamp": datetime.now().isoformat()
            },
            {
                "text": "Needs improvement in performance",
                "score": 3,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # 1. Analyze reviews
        review_response = client.post("/analyze/reviews/analyze", json=reviews)
        assert review_response.status_code == 200
        review_data = review_response.json()
        
        # 2. Verify sentiment analysis
        assert "overall_sentiment" in review_data["analysis"]
        assert "sentiment_trends" in review_data["analysis"]
        
        # 3. Check feature extraction
        assert "feature_analysis" in review_data["analysis"]

    def test_error_handling_flow(self):
        """Test error handling and recovery flow"""
        # 1. Test invalid app ID
        invalid_response = client.get("/analyze/app/invalid.app.id")
        assert invalid_response.status_code == 400
        
        # 2. Test valid request after error
        valid_response = client.get("/analyze/app/com.whatsapp")
        assert valid_response.status_code == 200
        
        # 3. Test invalid competitor analysis
        invalid_comp_response = client.post(
            "/analyze/competitors/compare",
            json={
                "app_id": "com.whatsapp",
                "competitor_ids": ["invalid.id1", "invalid.id2"]
            }
        )
        assert invalid_comp_response.status_code == 400
        
        # 4. Verify error message
        assert "detail" in invalid_comp_response.json()

class TestDataConsistency:
    def test_metadata_consistency(self):
        """Test consistency of metadata across endpoints"""
        # Get metadata from different endpoints
        app_response = client.get("/analyze/app/com.whatsapp")
        metadata_response = client.get("/analyze/metadata/analyze/com.whatsapp")
        tracking_response = client.get("/track/track/com.whatsapp")
        
        app_data = app_response.json()["data"]
        metadata_data = metadata_response.json()["analysis"]
        tracking_data = tracking_response.json()["tracking_data"]["current_metadata"]
        
        # Verify consistency
        assert app_data["title"] == metadata_data["current_metadata"]["title"]
        assert app_data["description"] == metadata_data["current_metadata"]["description"]
        assert tracking_data["title"] == metadata_data["current_metadata"]["title"]

    def test_keyword_consistency(self):
        """Test consistency of keyword analysis across endpoints"""
        # Get keyword data from different endpoints
        keyword_response = client.post(
            "/analyze/keywords/discover",
            json={"app_id": "com.whatsapp"}
        )
        metadata_response = client.get("/analyze/metadata/analyze/com.whatsapp")
        
        keyword_data = keyword_response.json()["analysis"]["main_app"]["analysis"]
        metadata_data = metadata_response.json()["analysis"]
        
        # Verify keyword consistency
        assert any(k in str(metadata_data["current_metadata"]["keywords"]) 
                  for k in keyword_data["top_keywords"])