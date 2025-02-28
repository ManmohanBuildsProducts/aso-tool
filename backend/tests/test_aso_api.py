import pytest
import requests
import json
import os
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
            "POST",
            "analyze",
            200,
            data={
                "package_name": self.test_app,
                "competitor_package_names": self.test_competitors,
                "keywords": ["wholesale", "b2b", "business"]
            }
        )

    def test_search_keyword(self):
        """Test keyword search endpoint"""
        return self.run_test(
            "Keyword Search",
            "GET",
            "search?keyword=wholesale%20b2b&limit=10",
            200
        )

    def test_similar_apps(self):
        """Test similar apps endpoint"""
        return self.run_test(
            "Similar Apps",
            "GET",
            f"similar?package_name={self.test_app}&limit=5",
            200
        )

def main():
    # Use environment variable for backend URL
    backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    if not backend_url:
        print("❌ REACT_APP_BACKEND_URL environment variable not set")
        return 1
    
    print(f"🔗 Using backend URL: {backend_url}")
    
    # Initialize tester
    tester = ASOAPITester(backend_url)

    print("\n🚀 Starting ASO Tool API Tests\n")

    # Test 1: Analyze BadhoBuyer app
    success, response = tester.test_analyze_app()
    if not success:
        print("❌ BadhoBuyer analysis failed")
    else:
        print("✅ App analysis successful")
        print("- App metadata retrieved")
        print("- Competitor analysis performed")
        print("- Keywords analyzed")

    # Test 2: Search for wholesale b2b keyword
    success, response = tester.test_search_keyword()
    if not success:
        print("❌ Keyword search failed")
    else:
        print("✅ Keyword search successful")
        print(f"- Found {len(response.get('results', []))} results")

    # Test 3: Get similar apps for BadhoBuyer
    success, response = tester.test_similar_apps()
    if not success:
        print("❌ Similar apps search failed")
    else:
        print("✅ Similar apps search successful")
        print(f"- Found {len(response.get('results', []))} similar apps")

    # Print results
    print(f"\n📊 Tests Summary:")
    print(f"Total tests: {tester.tests_run}")
    print(f"Passed: {tester.tests_passed}")
    print(f"Failed: {tester.tests_run - tester.tests_passed}")

    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()