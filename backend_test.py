import requests
import pytest
import os
from datetime import datetime
import uuid

class ASOAPITester:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        self.tests_run = 0
        self.tests_passed = 0
        self.test_app_id = None
        self.test_keyword_id = None

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
                if response.text:
                    print(f"Response: {response.json()}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if response.text:
                    print(f"Error: {response.text}")

            return success, response.json() if success and response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "",
            200
        )

    def test_create_app(self, package_name="com.badhobuyer", name="BadhoBuyer"):
        """Test creating a new app"""
        success, response = self.run_test(
            "Create App",
            "POST",
            "apps/",
            200,
            data={
                "package_name": package_name,
                "name": name,
                "is_competitor": False,
                "metadata": {
                    "category": "Business",
                    "rating": 4.5,
                    "installs": "100,000+"
                }
            }
        )
        if success and 'id' in response:
            self.test_app_id = response['id']
        return success

    def test_create_competitor(self):
        """Test creating a competitor app"""
        return self.run_test(
            "Create Competitor",
            "POST",
            "apps/",
            200,
            data={
                "package_name": "club.kirana",
                "name": "Kirana Club",
                "is_competitor": True,
                "metadata": {
                    "category": "Business",
                    "rating": 4.3,
                    "installs": "50,000+"
                }
            }
        )

    def test_get_apps(self):
        """Test getting all apps"""
        return self.run_test(
            "Get Apps",
            "GET",
            "apps/",
            200
        )

    def test_create_keyword(self, keyword="b2b wholesale"):
        """Test creating a new keyword"""
        success, response = self.run_test(
            "Create Keyword",
            "POST",
            "keywords/",
            200,
            data={
                "keyword": keyword,
                "category": "Business",
                "traffic_score": 75.5,
                "difficulty_score": 45.2,
                "last_updated": datetime.utcnow().isoformat()
            }
        )
        if success and 'id' in response:
            self.test_keyword_id = response['id']
        return success

    def test_get_keywords(self):
        """Test getting all keywords"""
        return self.run_test(
            "Get Keywords",
            "GET",
            "keywords/",
            200
        )

    def test_analyze_app(self):
        """Test app analysis"""
        if not self.test_app_id:
            print("❌ No test app ID available")
            return False
        return self.run_test(
            "Analyze App",
            "GET",
            f"analyze/app/{self.test_app_id}",
            200
        )

    def test_analyze_keywords(self):
        """Test keyword analysis"""
        return self.run_test(
            "Analyze Keywords",
            "GET",
            "analyze/keywords?keywords=b2b wholesale,distributor app",
            200
        )

    def test_analyze_competitors(self):
        """Test competitor analysis"""
        if not self.test_app_id:
            print("❌ No test app ID available")
            return False
        return self.run_test(
            "Analyze Competitors",
            "GET",
            f"analyze/competitors/{self.test_app_id}",
            200
        )

    def test_force_ranking_check(self):
        """Test forcing a ranking check"""
        return self.run_test(
            "Force Ranking Check",
            "POST",
            "rankings/check",
            200
        )

    def test_create_ranking(self):
        """Test creating a ranking entry"""
        if not self.test_app_id or not self.test_keyword_id:
            print("❌ No test app ID or keyword ID available")
            return False
        return self.run_test(
            "Create Ranking",
            "POST",
            "rankings/",
            200,
            data={
                "app_id": self.test_app_id,
                "keyword_id": self.test_keyword_id,
                "rank": 15,
                "date": datetime.utcnow().isoformat()
            }
        )

    def test_get_ranking_history(self):
        """Test getting ranking history"""
        if not self.test_app_id:
            print("❌ No test app ID available")
            return False
        return self.run_test(
            "Get Ranking History",
            "GET",
            f"rankings/history/{self.test_app_id}?days=30",
            200
        )

def main():
    # Setup
    tester = ASOAPITester()
    
    # Run tests in sequence
    tester.test_health_check()
    tester.test_create_app()
    tester.test_create_competitor()
    tester.test_get_apps()
    tester.test_create_keyword()
    tester.test_get_keywords()
    tester.test_analyze_app()
    tester.test_analyze_keywords()
    tester.test_analyze_competitors()
    tester.test_force_ranking_check()
    tester.test_create_ranking()
    tester.test_get_ranking_history()

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()