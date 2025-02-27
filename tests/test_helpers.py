from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime, timedelta

def generate_test_reviews(count: int) -> List[Dict[str, Any]]:
    """Generate test review data"""
    positive_texts = [
        "Great app, really love it!",
        "Amazing features and performance",
        "Best app in its category",
        "Very user friendly and reliable",
        "Excellent support and updates"
    ]
    
    negative_texts = [
        "App keeps crashing",
        "Poor performance and slow",
        "Needs a lot of improvement",
        "Not worth the storage space",
        "Terrible user experience"
    ]
    
    neutral_texts = [
        "Average app, does the job",
        "Some good features, some bad",
        "Works as expected",
        "Regular updates but minor improvements",
        "Basic functionality works fine"
    ]
    
    reviews = []
    for i in range(count):
        sentiment = i % 3  # 0: positive, 1: negative, 2: neutral
        if sentiment == 0:
            text = positive_texts[i % len(positive_texts)]
            score = 5
        elif sentiment == 1:
            text = negative_texts[i % len(negative_texts)]
            score = 1
        else:
            text = neutral_texts[i % len(neutral_texts)]
            score = 3
        
        reviews.append({
            "text": text,
            "score": score,
            "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
        })
    
    return reviews

def generate_test_metadata_history(days: int) -> List[Dict[str, Any]]:
    """Generate test metadata history"""
    base_metrics = {
        "ratings": 1000,
        "reviews": 500,
        "installs": "10,000+",
        "score": 4.5
    }
    
    history = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        metrics = {
            "timestamp": date.isoformat(),
            "record_date": date.strftime("%Y-%m-%d"),
            **base_metrics
        }
        
        # Add some variation
        metrics["ratings"] += i * 10
        metrics["reviews"] += i * 5
        metrics["score"] += (i % 3 - 1) * 0.1
        
        history.append(metrics)
    
    return history

def calculate_performance_metrics(response_times: List[float]) -> Dict[str, float]:
    """Calculate performance metrics from response times"""
    if not response_times:
        return {}
    
    sorted_times = sorted(response_times)
    total_requests = len(response_times)
    
    return {
        "min": min(response_times),
        "max": max(response_times),
        "avg": sum(response_times) / total_requests,
        "median": sorted_times[total_requests // 2],
        "p95": sorted_times[int(total_requests * 0.95)],
        "p99": sorted_times[int(total_requests * 0.99)]
    }

def verify_data_consistency(data1: Dict[str, Any], data2: Dict[str, Any],
                          fields: List[str]) -> bool:
    """Verify consistency between two data sets"""
    for field in fields:
        if field not in data1 or field not in data2:
            return False
        if data1[field] != data2[field]:
            return False
    return True

async def measure_response_time(client, endpoint: str, method: str = "GET",
                              data: Dict[str, Any] = None) -> float:
    """Measure response time for an endpoint"""
    start_time = datetime.now()
    
    if method == "GET":
        response = await client.get(endpoint)
    else:
        response = await client.post(endpoint, json=data)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    return duration

def load_test_data(file_path: str) -> Dict[str, Any]:
    """Load test data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading test data: {str(e)}")
        return {}