# ASO Tool API Documentation

## TLDR
- Base URL: `http://localhost:55240`
- Authentication: Bearer token
- Response format: JSON
- Rate limits: 100 requests/minute

## Endpoints Overview

### App Management
```typescript
// Add an app
POST /apps/
{
  "package_name": string,
  "name": string,
  "is_competitor": boolean,
  "metadata": {
    "title": string,
    "full_description": string,
    "category": string,
    "rating": number,
    "installs": string,
    "screenshots": string[]
  }
}

// Get app details
GET /apps/{package_name}

// Update app metadata
PUT /apps/{package_name}/metadata
{
  "title": string,
  "full_description": string,
  // ... other metadata
}
```

### AI Analysis
```typescript
// Get app analysis
GET /ai/analyze/{app_id}
Response: {
  "health_score": number,
  "metrics": {
    "keyword_score": number,
    "metadata_score": number,
    "competitive_score": number,
    "engagement_score": number
  },
  "recommendations": string[]
}

// Analyze keywords
GET /ai/keywords/{keyword}
Response: {
  "suggestions": [{
    "keyword": string,
    "relevance_score": number,
    "competition": number,
    "trend": "up" | "down" | "stable"
  }],
  "analysis": {
    "difficulty": number,
    "opportunity": number,
    "recommendations": string[]
  }
}

// Optimize metadata
POST /ai/metadata/title/{app_id}
Request: {
  "keywords": string[]
}
Response: {
  "suggestions": string[],
  "analysis": {
    "current_score": number,
    "potential_score": number,
    "recommendations": string[]
  }
}
```

### Rankings
```typescript
// Get ranking history
GET /rankings/history/{app_id}
Query params: {
  days: number  // default: 30
}
Response: {
  "rankings": [{
    "date": string,
    "keyword": string,
    "rank": number
  }],
  "trends": {
    "direction": string,
    "velocity": number
  }
}

// Force ranking check
POST /rankings/check
Response: {
  "status": "success" | "error",
  "message": string
}
```

### Competitor Analysis
```typescript
// Get competitor impact
GET /ai/competitors/impact/{app_id}
Query params: {
  competitor_ids: string[]
}
Response: {
  "analysis": {
    "shared_keywords": string[],
    "opportunities": string[],
    "threats": string[]
  },
  "recommendations": string[]
}

// Compare metadata
GET /ai/competitors/metadata/{app_id}
Response: {
  "differences": {
    "title": object,
    "description": object,
    "screenshots": object
  },
  "recommendations": string[]
}
```

## Error Responses
```json
{
  "detail": string,
  "code": number,
  "path": string,
  "timestamp": string
}
```

## Common Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 429: Too Many Requests
- 500: Server Error

## Rate Limiting
```typescript
Headers: {
  "X-RateLimit-Limit": "100",
  "X-RateLimit-Remaining": string,
  "X-RateLimit-Reset": string
}
```

## Authentication
```typescript
Headers: {
  "Authorization": "Bearer <token>"
}
```

## Webhook Events
```typescript
// Ranking changes
POST /webhook/rankings
{
  "app_id": string,
  "keyword": string,
  "old_rank": number,
  "new_rank": number,
  "timestamp": string
}

// Competitor updates
POST /webhook/competitors
{
  "app_id": string,
  "competitor_id": string,
  "type": "metadata" | "ranking",
  "changes": object
}
```

## Best Practices
1. Use pagination for large datasets
2. Cache frequently accessed data
3. Handle rate limits gracefully
4. Implement retry logic
5. Log API errors

## Example Usage

### cURL
```bash
# Get app analysis
curl -X GET "http://localhost:55240/ai/analyze/com.badhobuyer" \
     -H "Authorization: Bearer <token>"

# Add new app
curl -X POST "http://localhost:55240/apps/" \
     -H "Content-Type: application/json" \
     -d '{
       "package_name": "com.example.app",
       "name": "Example App",
       "is_competitor": false
     }'

# Force ranking check
curl -X POST "http://localhost:55240/rankings/check"
```

### JavaScript
```javascript
// Get keyword analysis
async function analyzeKeyword(keyword) {
  const response = await fetch(
    `http://localhost:55240/ai/keywords/${keyword}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
}

// Update metadata
async function updateMetadata(appId, metadata) {
  const response = await fetch(
    `http://localhost:55240/apps/${appId}/metadata`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(metadata)
    }
  );
  return await response.json();
}
```

### Python
```python
import requests

# Get competitor analysis
def get_competitor_analysis(app_id, competitor_ids):
    response = requests.get(
        f"http://localhost:55240/ai/competitors/impact/{app_id}",
        params={"competitor_ids": competitor_ids},
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

# Get ranking history
def get_ranking_history(app_id, days=30):
    response = requests.get(
        f"http://localhost:55240/rankings/history/{app_id}",
        params={"days": days},
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```