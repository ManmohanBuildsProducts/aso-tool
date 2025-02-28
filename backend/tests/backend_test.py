import requests
import pytest
import time
from datetime import datetime
import os

class ASOToolTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
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
                return success, response.json()
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                return success, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_analyze_endpoint(self, package_name):
        """Test analyze endpoint"""
        data = {
            "package_name": package_name,
            "competitor_package_names": ["com.competitor1", "com.competitor2"],
            "keywords": ["wholesale", "b2b", "marketplace"]
        }
        success, response = self.run_test(
            "Create Analysis Job",
            "POST",
            "analyze",
            200,
            data=data
        )
        if success and response:
            print(f"Response: {response}")
            return response.get('job_id') or response.get('task_id')
        return None

    def test_job_status(self, job_id):
        """Test job status endpoint"""
        success, response = self.run_test(
            "Get Job Status",
            "GET",
            f"analyze/{job_id}",
            200
        )
        return response if success else None

    def test_job_completion(self, job_id, timeout=60):
        """Test job completion with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.test_job_status(job_id)
            if not response:
                return False
            
            if response['status'] == 'completed':
                print("✅ Job completed successfully")
                return True
            elif response['status'] in ['error', 'timeout']:
                print(f"❌ Job failed with status: {response['status']}")
                return False
            
            time.sleep(2)
        
        print("❌ Job timed out")
        return False

def main():
    # Setup
    tester = ASOToolTester()
    test_package = "com.badhobuyer"

    # Test 1: Create Analysis Job
    print("\n🔬 Testing Analysis Job Creation")
    job_id = tester.test_analyze_endpoint(test_package)
    if not job_id:
        print("❌ Failed to create analysis job")
        return 1

    # Test 2: Monitor Job Progress
    print("\n🔬 Testing Job Progress Monitoring")
    if not tester.test_job_completion(job_id):
        print("❌ Job monitoring failed")
        return 1

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    exit(main())