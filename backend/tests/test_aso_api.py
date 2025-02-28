import pytest
import requests
import json
from datetime import datetime

class ASOAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_app = "com.badhobuyer"
        self.test_competitors = ["club.kirana", "com.udaan.android"]

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Error: {response.text}")

            return success, response.json() if success else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_analyze_app(self):
        """Test app analysis endpoint"""
        return self.run_test(
            "App Analysis",
            "GET",
            f"analyze/app/{self.test_app}",
            200
        )

    def test_analyze_keywords(self):
        """Test keyword analysis endpoint"""
        return self.run_test(
            "Keyword Analysis",
            "POST",
            "analyze/keywords",
            200,
            data={
                "base_keyword": "wholesale",
                "industry": "B2B wholesale"
            }
        )

    def test_analyze_competitors(self):
        """Test competitor analysis endpoint"""
        return self.run_test(
            "Competitor Analysis",
            "POST",
            "analyze/competitors",
            200,
            data={
                "app_metadata": {"name": "BadhoBuyer", "category": "Business"},
                "competitor_metadata": [
                    {"name": "Kirana Club", "category": "Business"},
                    {"name": "Udaan", "category": "Business"}
                ]
            }
        )

    def test_analyze_trends(self):
        """Test market trends analysis endpoint"""
        return self.run_test(
            "Market Trends Analysis",
            "POST",
            "analyze/trends",
            200,
            data={
                "category": "B2B wholesale"
            }
        )

    def test_optimize_description(self):
        """Test description optimization endpoint"""
        return self.run_test(
            "Description Optimization",
            "POST",
            "optimize/description",
            200,
            data={
                "current_description": "B2B wholesale app for businesses",
                "keywords": ["wholesale", "b2b", "business"]
            }
        )

def main():
    # Use localhost with backend port
    backend_url = "http://localhost:55925"
    
    if not backend_url:
        print("❌ Could not find backend URL in frontend/.env")
        return 1

    print(f"🔗 Using backend URL: {backend_url}")
    
    # Initialize tester
    tester = ASOAPITester(backend_url)

    # Run tests
    tester.test_analyze_app()
    tester.test_analyze_keywords()
    tester.test_analyze_competitors()
    tester.test_analyze_trends()
    tester.test_optimize_description()

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()