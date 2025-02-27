# ASO Tool Troubleshooting Guide

## TLDR
- Common issues and solutions
- Performance optimization tips
- Debug procedures
- Error resolution steps

## Common Issues

### 1. API Connection Issues
```typescript
Problem: API endpoints returning 500 errors
Solutions:
1. Check MongoDB connection
   ```bash
   docker-compose logs mongodb
   ```
2. Verify API service
   ```bash
   docker-compose logs backend
   ```
3. Check environment variables
   ```bash
   cat .env | grep MONGO_URL
   ```

Problem: Authentication failures
Solutions:
1. Verify token
   ```bash
   curl -H "Authorization: Bearer $TOKEN" http://localhost:55240/
   ```
2. Check token expiration
   ```python
   import jwt
   decoded = jwt.decode(token, verify=False)
   print(decoded['exp'])
   ```
```

### 2. Scraping Issues
```typescript
Problem: No ranking data
Solutions:
1. Check scraper logs
   ```bash
   tail -f /var/log/aso-tool/scraper.log
   ```
2. Verify Play Store access
   ```python
   async def test_scraper():
       scraper = PlayStoreScraper()
       result = await scraper.test_connection()
       print(result)
   ```

Problem: Rate limiting
Solutions:
1. Adjust scraping delay
   ```python
   SCRAPER_DELAY = 5  # seconds
   ```
2. Implement proxy rotation
   ```python
   PROXY_LIST = [
       "http://proxy1:8080",
       "http://proxy2:8080"
   ]
   ```
```

### 3. Performance Issues
```typescript
Problem: Slow API responses
Solutions:
1. Check database indexes
   ```javascript
   db.rankings.getIndexes()
   ```
2. Optimize queries
   ```python
   # Before
   rankings = await db.rankings.find({}).to_list(1000)
   
   # After
   rankings = await db.rankings.find({
       "date": {"$gte": start_date}
   }).limit(100)
   ```

Problem: High memory usage
Solutions:
1. Monitor memory
   ```bash
   docker stats
   ```
2. Implement pagination
   ```python
   @app.get("/rankings/")
   async def get_rankings(
       skip: int = 0,
       limit: int = 100
   ):
       return await db.rankings.find().skip(skip).limit(limit)
   ```
```

## Debug Procedures

### 1. Backend Debugging
```python
# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add debug points
async def analyze_app(app_id: str):
    logger.debug(f"Starting analysis for {app_id}")
    try:
        result = await perform_analysis(app_id)
        logger.debug(f"Analysis result: {result}")
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise
```

### 2. Frontend Debugging
```javascript
// Enable React DevTools
import { debugContextDevtool } from "react-context-devtool";

// Add performance monitoring
import { Profiler } from 'react';

function onRenderCallback(
    id, phase, actualDuration, baseDuration, startTime, commitTime
) {
    console.log({
        id,
        phase,
        actualDuration,
        baseDuration,
        startTime,
        commitTime
    });
}

<Profiler id="HealthScore" onRender={onRenderCallback}>
    <HealthScore />
</Profiler>
```

### 3. Database Debugging
```javascript
// Monitor slow queries
db.setProfilingLevel(2, { slowms: 100 });

// Check query execution plan
db.rankings.find({
    "app_id": "com.example"
}).explain("executionStats");

// Monitor connections
db.currentOp(true);
```

## Error Resolution

### 1. API Errors
```typescript
interface APIError {
    status: number;
    code: string;
    message: string;
    details?: any;
}

// Error handling middleware
app.use((err, req, res, next) => {
    logger.error('API Error:', err);
    res.status(err.status || 500).json({
        code: err.code || 'INTERNAL_ERROR',
        message: err.message,
        details: err.details
    });
});
```

### 2. Integration Errors
```python
class IntegrationError(Exception):
    def __init__(self, service: str, error: str, details: dict = None):
        self.service = service
        self.error = error
        self.details = details
        super().__init__(f"{service}: {error}")

async def handle_integration_error(error: IntegrationError):
    await notify_admin(error)
    await log_error(error)
    if error.service == "deepseek":
        return await use_fallback_analysis()
    raise error
```

### 3. Data Errors
```python
class DataValidationError(Exception):
    pass

async def validate_rankings(rankings: list):
    errors = []
    for ranking in rankings:
        try:
            validate_ranking(ranking)
        except Exception as e:
            errors.append({
                "ranking": ranking,
                "error": str(e)
            })
    if errors:
        raise DataValidationError(errors)
```

## Performance Optimization

### 1. Database Optimization
```javascript
// Create indexes
db.rankings.createIndex({ "app_id": 1, "date": -1 });
db.keywords.createIndex({ "keyword": 1 });

// Compound indexes
db.rankings.createIndex(
    { "app_id": 1, "keyword": 1, "date": -1 },
    { unique: true }
);
```

### 2. API Optimization
```python
# Caching
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_cached_analysis(app_id: str):
    return await perform_analysis(app_id)

# Batch processing
async def batch_update_rankings(rankings: list):
    chunks = [rankings[i:i+100] for i in range(0, len(rankings), 100)]
    for chunk in chunks:
        await db.rankings.insert_many(chunk)
```

### 3. Frontend Optimization
```javascript
// Code splitting
const HealthScore = React.lazy(() => import('./HealthScore'));

// Memoization
const MemoizedChart = React.memo(({ data }) => (
    <LineChart data={data} />
));

// Virtual scrolling
import { VirtualList } from 'react-virtual';

function RankingList({ rankings }) {
    return (
        <VirtualList
            height={400}
            itemCount={rankings.length}
            itemSize={50}
            renderItem={({ index, style }) => (
                <RankingItem
                    ranking={rankings[index]}
                    style={style}
                />
            )}
        />
    );
}
```

## Monitoring and Alerts

### 1. System Monitoring
```python
async def monitor_system_health():
    metrics = {
        "api_latency": await measure_api_latency(),
        "db_connections": await get_db_connections(),
        "memory_usage": await get_memory_usage(),
        "error_rate": await calculate_error_rate()
    }
    await store_metrics(metrics)
    if should_alert(metrics):
        await send_alert(metrics)
```

### 2. Error Tracking
```python
async def track_errors():
    error_counts = await db.errors.aggregate([
        {
            "$group": {
                "_id": "$type",
                "count": {"$sum": 1}
            }
        }
    ])
    return error_counts
```

### 3. Performance Tracking
```python
async def track_performance():
    metrics = await db.metrics.aggregate([
        {
            "$group": {
                "_id": "$endpoint",
                "avg_latency": {"$avg": "$duration"},
                "p95_latency": {"$percentile": ["$duration", 95]}
            }
        }
    ])
    return metrics
```

## Recovery Procedures

### 1. Data Recovery
```python
async def recover_data(date_range: dict):
    # Backup current data
    await backup_data()
    
    # Fetch missing data
    missing_data = await find_missing_data(date_range)
    
    # Recover data
    for data in missing_data:
        await refetch_data(data)
        
    # Validate recovered data
    await validate_recovered_data()
```

### 2. Service Recovery
```python
async def recover_service(service_name: str):
    # Stop service
    await stop_service(service_name)
    
    # Clean up
    await cleanup_service(service_name)
    
    # Restart service
    await start_service(service_name)
    
    # Verify service
    await verify_service(service_name)
```

### 3. Error Recovery
```python
async def handle_recovery(error: Exception):
    try:
        # Log error
        await log_error(error)
        
        # Attempt recovery
        if isinstance(error, DatabaseError):
            await recover_database()
        elif isinstance(error, APIError):
            await recover_api()
        elif isinstance(error, ScraperError):
            await recover_scraper()
            
        # Verify recovery
        await verify_system_health()
        
    except Exception as e:
        # Escalate if recovery fails
        await escalate_error(e)
```