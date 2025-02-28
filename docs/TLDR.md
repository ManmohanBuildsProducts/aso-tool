# ASO Tool Technical Documentation

## TLDR
- Frontend: React + TailwindCSS dashboard for ASO optimization
- Backend: FastAPI + MongoDB + Deepseek AI
- Key Features: Health score, action items, competitor analysis
- Main APIs: Keyword analysis, metadata optimization, ranking tracking

## Quick Start
- `/api/ai/analyze/{app_id}` - Get app analysis
- `/api/ai/keywords/{keyword}` - Analyze keywords
- `/api/ai/metadata/title/{app_id}` - Optimize title
- `/api/rankings/check` - Force ranking check

## Architecture

### Frontend Components
```mermaid
graph TD
    A[App.js] --> B[Dashboard]
    B --> C[HealthScore]
    B --> D[ActionItems]
    B --> E[CompetitorAnalysis]
    B --> F[KeywordOpportunities]
    B --> G[MetadataHealth]
    
    C --> C1[CircularProgress]
    C --> C2[MetricsGrid]
    
    D --> D1[PriorityList]
    D --> D2[ActionCard]
    
    E --> E1[ComparisonChart]
    E --> E2[InsightsList]
    
    F --> F1[KeywordGrid]
    F --> F2[OpportunityScore]
    
    G --> G1[MetadataForm]
    G --> G2[HealthIndicators]
</code>
```

### Backend Architecture
```mermaid
graph LR
    A[FastAPI] --> B[MongoDB]
    A --> C[Deepseek AI]
    A --> D[Play Store Scraper]
    
    B --> B1[Rankings]
    B --> B2[Apps]
    B --> B3[Keywords]
    
    C --> C1[Keyword Analysis]
    C --> C2[Metadata Optimization]
    
    D --> D1[Ranking Data]
    D --> D2[App Data]
</code>
```

### Data Flow
```mermaid
graph TD
    A[Frontend] --> |API Requests| B[Backend]
    B --> |Store Data| C[MongoDB]
    B --> |AI Analysis| D[Deepseek]
    B --> |Scrape Data| E[Play Store]
    
    C --> |Query Data| B
    D --> |Insights| B
    E --> |Rankings| B
    
    B --> |Response| A
</code>
```

### API Flow
```mermaid
graph LR
    A[API Request] --> B[FastAPI Router]
    B --> C[Controller]
    C --> D[Service Layer]
    
    D --> E[MongoDB Service]
    D --> F[AI Service]
    D --> G[Scraper Service]
    
    E & F & G --> H[Response Handler]
    H --> I[API Response]
</code>
```

## Key Endpoints

### Analysis APIs
- GET `/ai/analyze/{app_id}`
  ```json
  {
    "health_score": 85,
    "metrics": {...},
    "recommendations": [...]
  }
  ```

### Keyword APIs
- GET `/ai/keywords/{keyword}`
  ```json
  {
    "suggestions": [...],
    "metrics": {...},
    "opportunities": [...]
  }
  ```

### Ranking APIs
- GET `/rankings/history/{app_id}`
  ```json
  {
    "rankings": [...],
    "trends": {...},
    "predictions": [...]
  }
  ```

## Data Models

### App Model
```python
{
    "package_name": str,
    "name": str,
    "metadata": {
        "title": str,
        "description": str,
        "screenshots": List[str]
    },
    "rankings": {
        "keyword": str,
        "rank": int,
        "date": datetime
    }
}
```

### Keyword Model
```python
{
    "keyword": str,
    "metrics": {
        "volume": float,
        "difficulty": float,
        "relevance": float
    },
    "trends": {
        "direction": str,
        "velocity": float
    }
}
```

## Implementation Notes

### Frontend
- React 19.0.0
- TailwindCSS for styling
- Chart.js for visualizations
- React Query for API calls

### Backend
- FastAPI 0.110.1
- MongoDB with Motor 3.3.1
- Deepseek AI integration
- Async scraping with aiohttp

### AI Features
- Keyword analysis
- Metadata optimization
- Ranking predictions
- Competitor insights

## Error Handling
- Frontend: React Error Boundary
- Backend: Global exception handler
- AI: Fallback to rule-based analysis
- Scraping: Retry mechanism

## Monitoring
- API health checks
- AI response quality
- Scraping success rate
- Response times

## Security
- API authentication
- Rate limiting
- Data validation
- Error logging