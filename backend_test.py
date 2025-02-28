import requests
import pytest
import os
from datetime import datetime

class ASOAPITester:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
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

    def test_analyze_app(self):
        """Test app analysis"""
        return self.run_test(
            "Analyze App",
            "POST",
            "api/analyze",
            200,
            data={
                "package_name": "com.badhobuyer",
                "competitor_package_names": ["club.kirana", "com.udaan.android"],
                "keywords": ["wholesale", "b2b", "business"]
            }
        )

    def test_search_keyword(self):
        """Test keyword search"""
        return self.run_test(
            "Search Keyword",
            "GET",
            "api/search",
            200,
            params={"keyword": "wholesale", "limit": 5}
        )

    def test_similar_apps(self):
        """Test similar apps"""
        return self.run_test(
            "Similar Apps",
            "GET",
            "api/similar",
            200,
            params={"package_name": "com.badhobuyer", "limit": 5}
        )

    def test_error_handling(self):
        """Test error handling"""
        return self.run_test(
            "Error Handling",
            "POST",
            "api/analyze",
            200,  # API returns 200 with error message
            data={
                "package_name": "invalid.package.name",
                "competitor_package_names": [],
                "keywords": []
            }
        )

def main():
    # Setup
    tester = ASOAPITester()
    
    # Run tests in sequence
    tester.test_health_check()
    tester.test_analyze_app()
    tester.test_search_keyword()
    tester.test_similar_apps()
    tester.test_error_handling()

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()