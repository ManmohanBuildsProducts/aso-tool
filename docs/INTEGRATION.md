# ASO Tool Integration Guide

## TLDR
- Authentication: JWT + API Keys
- Webhooks: Real-time updates
- Third-party: Deepseek AI, Play Store
- Custom integrations available

## Authentication

### JWT Authentication
```typescript
interface JWTConfig {
  secret_key: string;
  algorithm: 'HS256' | 'RS256';
  expires_in: string; // e.g., "24h"
  refresh_token_expires_in: string; // e.g., "7d"
}

// Example token
{
  "sub": "user@example.com",
  "role": "admin",
  "exp": 1735689600
}
```

### API Key Authentication
```python
# Generate API key
def generate_api_key():
    return secrets.token_urlsafe(32)

# Validate API key
async def validate_api_key(api_key: str):
    return await db.api_keys.find_one({"key": api_key})
```

## Webhook Integration

### Configuration
```typescript
interface WebhookConfig {
  url: string;
  events: string[];
  secret: string;
  retry_count: number;
  timeout: number;
}
```

### Event Types
```json
{
  "ranking_change": {
    "app_id": "string",
    "keyword": "string",
    "old_rank": "number",
    "new_rank": "number",
    "timestamp": "string"
  },
  "score_update": {
    "app_id": "string",
    "old_score": "number",
    "new_score": "number",
    "components": "object"
  },
  "competitor_update": {
    "app_id": "string",
    "competitor_id": "string",
    "type": "string",
    "changes": "object"
  }
}
```

### Implementation
```python
# Send webhook
async def send_webhook(event_type: str, data: dict):
    webhook = await db.webhooks.find_one({"events": event_type})
    if webhook:
        signature = generate_signature(data, webhook["secret"])
        async with httpx.AsyncClient() as client:
            await client.post(
                webhook["url"],
                json=data,
                headers={"X-Signature": signature}
            )

# Verify webhook
def verify_webhook(signature: str, payload: str, secret: str):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

## Third-Party Services

### 1. Deepseek AI Integration
```python
from .deepseek_analyzer import DeepseekAnalyzer

class DeepseekIntegration:
    def __init__(self, api_key: str):
        self.analyzer = DeepseekAnalyzer(api_key)
        
    async def analyze_keyword(self, keyword: str):
        return await self.analyzer.generate_keyword_suggestions(keyword)
        
    async def optimize_metadata(self, metadata: dict):
        return await self.analyzer.analyze_app_metadata(metadata)
```

### 2. Play Store Integration
```python
class PlayStoreIntegration:
    def __init__(self):
        self.scraper = PlayStoreScraper()
        
    async def get_app_data(self, package_name: str):
        return await self.scraper.get_app_metadata(package_name)
        
    async def search_keyword(self, keyword: str):
        return await self.scraper.search_keyword(keyword)
```

### 3. MongoDB Integration
```python
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDBIntegration:
    def __init__(self, uri: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client.aso_tool
        
    async def store_rankings(self, rankings: list):
        return await self.db.rankings.insert_many(rankings)
        
    async def get_app_history(self, app_id: str):
        return await self.db.rankings.find(
            {"app_id": app_id}
        ).sort("date", -1).to_list(1000)
```

## Custom Integrations

### 1. Data Export
```python
class DataExporter:
    async def export_rankings(self, app_id: str, format: str):
        data = await get_rankings(app_id)
        if format == "csv":
            return convert_to_csv(data)
        elif format == "excel":
            return convert_to_excel(data)
        return data

    async def export_analysis(self, app_id: str, format: str):
        data = await get_analysis(app_id)
        return format_data(data, format)
```

### 2. Custom Notifications
```python
class NotificationSystem:
    async def send_notification(
        self,
        event_type: str,
        data: dict,
        channels: list
    ):
        for channel in channels:
            if channel == "email":
                await send_email_notification(data)
            elif channel == "slack":
                await send_slack_notification(data)
            elif channel == "webhook":
                await send_webhook_notification(data)
```

### 3. Custom Reports
```python
class ReportGenerator:
    async def generate_report(
        self,
        app_id: str,
        report_type: str,
        date_range: dict
    ):
        data = await gather_report_data(app_id, date_range)
        return format_report(data, report_type)
```

## Integration Best Practices

### 1. Error Handling
```python
class IntegrationError(Exception):
    def __init__(self, service: str, error: str):
        self.service = service
        self.error = error
        super().__init__(f"{service}: {error}")

async def safe_integration(func):
    try:
        return await func()
    except Exception as e:
        raise IntegrationError(
            func.__name__,
            str(e)
        )
```

### 2. Rate Limiting
```python
from asyncio import Semaphore

class RateLimiter:
    def __init__(self, limit: int):
        self.semaphore = Semaphore(limit)
        
    async def __aenter__(self):
        await self.semaphore.acquire()
        
    async def __aexit__(self, *args):
        self.semaphore.release()
```

### 3. Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

class Cache:
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self.cache = {}
        
    async def get_or_set(self, key: str, func):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
        value = await func()
        self.cache[key] = (value, datetime.now())
        return value
```

### 4. Monitoring
```python
class IntegrationMonitor:
    async def log_request(
        self,
        service: str,
        method: str,
        duration: float
    ):
        await db.logs.insert_one({
            "service": service,
            "method": method,
            "duration": duration,
            "timestamp": datetime.utcnow()
        })
        
    async def check_health(self, service: str):
        status = await get_service_status(service)
        await update_health_metrics(service, status)
```

## Security Considerations

### 1. Data Encryption
```python
from cryptography.fernet import Fernet

class Encryptor:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)
        
    def encrypt_data(self, data: str):
        return self.fernet.encrypt(data.encode())
        
    def decrypt_data(self, encrypted: bytes):
        return self.fernet.decrypt(encrypted).decode()
```

### 2. Access Control
```python
from functools import wraps

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not has_permission(permission):
                raise PermissionError(
                    f"Missing permission: {permission}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. Data Validation
```python
from pydantic import BaseModel, validator

class IntegrationData(BaseModel):
    service: str
    data: dict
    timestamp: datetime
    
    @validator("data")
    def validate_data(cls, v):
        if not v:
            raise ValueError("Data cannot be empty")
        return v
```