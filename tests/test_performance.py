import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from concurrent.futures import ThreadPoolExecutor
import statistics

client = TestClient(app)

class TestAPIPerformance:
    def test_endpoint_response_times(self):
        """Test response times for key endpoints"""
        endpoints = [
            ("/analyze/app/com.whatsapp", "GET"),
            ("/analyze/metadata/analyze/com.whatsapp", "GET"),
            ("/track/track/com.whatsapp", "GET")
        ]
        
        response_times = {}
        for endpoint, method in endpoints:
            times = []
            for _ in range(5):  # Test each endpoint 5 times
                start_time = time.time()
                if method == "GET":
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint)
                end_time = time.time()
                
                assert response.status_code == 200
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            response_times[endpoint] = avg_time
            
            # Assert reasonable response time (adjust thresholds as needed)
            assert avg_time < 2.0, f"Slow response time for {endpoint}: {avg_time}s"

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        num_concurrent = 5
        endpoint = "/analyze/app/com.whatsapp"
        
        async def make_request():
            response = client.get(endpoint)
            return response.status_code
        
        async def run_concurrent_requests():
            tasks = [make_request() for _ in range(num_concurrent)]
            results = await asyncio.gather(*tasks)
            return results
        
        results = asyncio.run(run_concurrent_requests())
        
        # Verify all requests succeeded
        assert all(status == 200 for status in results)

    def test_large_data_handling(self):
        """Test handling of large data sets"""
        # Generate large review dataset
        large_reviews = [
            {
                "text": f"Review text {i} with some detailed feedback about various features",
                "score": i % 5 + 1,
                "timestamp": "2024-02-27"
            }
            for i in range(100)  # Test with 100 reviews
        ]
        
        start_time = time.time()
        response = client.post("/analyze/reviews/analyze", json=large_reviews)
        end_time = time.time()
        
        assert response.status_code == 200
        processing_time = end_time - start_time
        assert processing_time < 5.0, f"Slow processing for large dataset: {processing_time}s"

    def test_memory_usage(self):
        """Test memory usage during operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        # Perform memory-intensive operation
        large_text = "Sample text " * 1000
        response = client.post(
            "/analyze/text/analyze",
            params={"text": large_text, "text_type": "full_description"}
        )
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        assert response.status_code == 200
        assert memory_increase < 100, f"High memory usage: {memory_increase}MB increase"

class TestCaching:
    def test_cache_effectiveness(self):
        """Test effectiveness of caching mechanism"""
        endpoint = "/analyze/app/com.whatsapp"
        
        # First request (no cache)
        start_time = time.time()
        first_response = client.get(endpoint)
        first_request_time = time.time() - start_time
        
        # Second request (should use cache)
        start_time = time.time()
        second_response = client.get(endpoint)
        second_request_time = time.time() - start_time
        
        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert second_request_time <= first_request_time * 1.5, "Caching not effective"

    def test_cache_invalidation(self):
        """Test cache invalidation"""
        endpoint = "/analyze/app/com.whatsapp"
        
        # Get initial data
        first_response = client.get(endpoint)
        first_data = first_response.json()
        
        # Force cache invalidation
        invalidate_response = client.post(f"{endpoint}/invalidate-cache")
        
        # Get new data
        second_response = client.get(endpoint)
        second_data = second_response.json()
        
        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert first_data != second_data

class TestResourceUtilization:
    def test_cpu_usage(self):
        """Test CPU usage during intensive operations"""
        import psutil
        
        def get_cpu_percent():
            return psutil.cpu_percent(interval=1)
        
        initial_cpu = get_cpu_percent()
        
        # Perform CPU-intensive operation
        response = client.post(
            "/analyze/competitors/compare",
            json={
                "app_id": "com.whatsapp",
                "competitor_ids": [
                    "org.telegram.messenger",
                    "org.thoughtcrime.securesms"
                ]
            }
        )
        
        peak_cpu = get_cpu_percent()
        
        assert response.status_code == 200
        assert peak_cpu - initial_cpu < 50, f"High CPU usage: {peak_cpu}% peak"

    def test_database_connections(self):
        """Test database connection handling"""
        results = []
        for _ in range(10):
            response = client.get("/track/track/com.whatsapp")
            results.append(response)
        assert all(r.status_code == 200 for r in results)

class TestScalability:
    def test_batch_processing(self):
        """Test batch processing capabilities"""
        # Generate batch of apps to analyze
        apps = ["com.whatsapp", "org.telegram.messenger", "org.thoughtcrime.securesms"]
        
        start_time = time.time()
        results = []
        for app_id in apps:
            response = client.get(f"/analyze/app/{app_id}")
            results.append(response.json())
        total_time = time.time() - start_time
        
        assert len(results) == len(apps)
        assert total_time < 6.0, f"Slow batch processing: {total_time}s"

    def test_load_handling(self):
        """Test handling of increased load"""
        endpoint = "/analyze/app/com.whatsapp"
        
        def make_request(_):
            return client.get(endpoint)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            responses = list(executor.map(make_request, range(20)))
            total_time = time.time() - start_time
        
        success_rate = sum(1 for r in responses if r.status_code == 200) / len(responses)
        assert success_rate > 0.95, f"Low success rate under load: {success_rate}"
        assert total_time < 10.0, f"Poor load handling: {total_time}s for 20 requests"