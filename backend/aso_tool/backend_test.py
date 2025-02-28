import pytest
import requests
import time
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from frontend
load_dotenv("/app/frontend/.env")

# Get the backend URL from environment
BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL")
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL not found in environment")

class TestASOTool:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_app = "com.example.testapp"
        
    def test_cors_and_basic_connectivity(self):
        """Test CORS configuration and basic API connectivity"""
        try:
            # Test root endpoint
            response = self.session.get(f"{self.base_url}/")
            assert response.status_code == 200
            assert "message" in response.json()
            logger.info("✅ Basic connectivity test passed")
            
            # Test CORS headers
            headers = {
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
            response = self.session.options(f"{self.base_url}/analyze", headers=headers)
            assert response.headers.get("Access-Control-Allow-Origin") == "*"
            assert "POST" in response.headers.get("Access-Control-Allow-Methods", "")
            logger.info("✅ CORS configuration test passed")
            
            return True
        except Exception as e:
            logger.error(f"❌ Connectivity test failed: {str(e)}")
            return False

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        try:
            # Make rapid requests to trigger rate limit
            endpoint = f"{self.base_url}/analyze"
            data = {
                "package_name": self.test_app,
                "competitor_package_names": [],
                "keywords": []
            }
            
            responses = []
            for _ in range(35):  # Exceeds the 30 requests/minute limit
                response = self.session.post(endpoint, json=data)
                responses.append(response.status_code)
                
            # Check if rate limiting kicked in
            assert 429 in responses, "Rate limiting not triggered"
            logger.info("✅ Rate limiting test passed")
            
            return True
        except Exception as e:
            logger.error(f"❌ Rate limiting test failed: {str(e)}")
            return False

    def test_analyze_endpoint(self):
        """Test the analyze endpoint functionality"""
        try:
            # Test valid request
            data = {
                "package_name": self.test_app,
                "competitor_package_names": ["com.competitor1"],
                "keywords": ["test", "app"]
            }
            
            response = self.session.post(f"{self.base_url}/analyze", json=data)
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert "task_id" in result
            assert "status" in result
            assert result["status"] in ["pending", "processing", "completed"]
            
            # Test status endpoint
            task_id = result["task_id"]
            status_response = self.session.get(f"{self.base_url}/analyze/{task_id}")
            assert status_response.status_code == 200
            
            logger.info("✅ Analyze endpoint test passed")
            return True
        except Exception as e:
            logger.error(f"❌ Analyze endpoint test failed: {str(e)}")
            return False

    def test_error_handling(self):
        """Test error handling"""
        try:
            # Test invalid package name
            data = {
                "package_name": "",
                "competitor_package_names": [],
                "keywords": []
            }
            response = self.session.post(f"{self.base_url}/analyze", json=data)
            assert response.status_code in [400, 422]
            
            # Test invalid task ID
            response = self.session.get(f"{self.base_url}/analyze/invalid-id")
            assert response.status_code == 404
            
            logger.info("✅ Error handling test passed")
            return True
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {str(e)}")
            return False

def main():
    """Run all tests"""
    tester = TestASOTool()
    
    # Run tests
    results = {
        "Connectivity & CORS": tester.test_cors_and_basic_connectivity(),
        "Rate Limiting": tester.test_rate_limiting(),
        "Analyze Endpoint": tester.test_analyze_endpoint(),
        "Error Handling": tester.test_error_handling()
    }
    
    # Print summary
    print("\n📊 Test Results Summary:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    # Calculate success rate
    success_rate = sum(1 for result in results.values() if result) / len(results) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    # Return 0 if all tests passed, 1 otherwise
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit(main())