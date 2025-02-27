# ASO Tool Documentation

## Project Overview
ASO (App Store Optimization) tool focused on Google Play Store that helps analyze apps and their competitors, providing insights for optimization.

### Key Features
1. App Analysis
   - Metadata extraction
   - Performance metrics
   - Rating analysis
   - Install tracking

2. Competitor Analysis
   - Market position comparison
   - Feature comparison
   - Rating distribution
   - Install trends

3. Keyword Analysis
   - Common keywords
   - Unique keywords
   - Keyword density
   - Search volume estimation

4. Review Analysis
   - Sentiment analysis
   - Feature mentions
   - User feedback categorization
   - Rating trends

## Technical Implementation

### Backend (FastAPI)

#### Core Components
1. App Scraper (`app/services/app_scraper.py`)
   - Google Play Store data extraction
   - App metadata parsing
   - Rating and review collection

2. Competitor Analyzer (`app/services/competitor_analyzer.py`)
   - Market position calculation
   - Competitive metrics comparison
   - Feature analysis

3. Keyword Analyzer (`app/services/keyword_analyzer.py`)
   - Keyword extraction
   - Density calculation
   - Relevance scoring

4. Review Analyzer (`app/services/review_analyzer.py`)
   - Sentiment analysis
   - Feature extraction
   - Trend analysis

#### API Endpoints
1. App Analysis
   ```
   GET /api/analyze/app/{app_id}
   Response: App details, metrics, and basic analysis
   ```

2. Competitor Analysis
   ```
   POST /api/analyze/competitors/compare
   Body: {
     "app_id": "main.app.id",
     "competitor_ids": ["comp1.id", "comp2.id"]
   }
   Response: Comparative analysis and market position
   ```

3. Keyword Analysis
   ```
   POST /api/analyze/keywords/discover
   Body: {
     "app_id": "app.id",
     "competitor_ids": ["comp.id"]
   }
   Response: Keyword analysis and recommendations
   ```

4. Review Analysis
   ```
   POST /api/analyze/reviews/analyze
   Body: [Array of reviews]
   Response: Sentiment analysis and insights
   ```

### Frontend (React)

#### Components
1. AppAnalyzer (`frontend/src/components/AppAnalyzer.jsx`)
   - Main container component
   - Handles app and competitor input
   - Manages analysis state

2. ComparisonCharts (`frontend/src/components/ComparisonCharts.jsx`)
   - Data visualization
   - Market position charts
   - Trend analysis graphs

3. KeywordAnalysis (`frontend/src/components/KeywordAnalysis.jsx`)
   - Keyword visualization
   - Density charts
   - Comparison metrics

4. MetadataComparison (`frontend/src/components/MetadataComparison.jsx`)
   - App metadata comparison
   - Feature comparison
   - Rating distribution

### Deployment

#### Current Setup
- Platform: Render.com
- URL: https://aso-tool.onrender.com
- Repository: https://github.com/ManmohanBuildsProducts/aso-tool

#### Environment Variables
```
PORT=8000
PYTHON_VERSION=3.11.0
NODE_VERSION=20.0.0
```

## Current Status

### Working Features
1. Backend API endpoints
   - App data extraction
   - Competitor comparison
   - Keyword analysis
   - Review analysis

2. Frontend Components
   - App input form
   - Competitor management
   - Analysis tabs
   - Data visualization

### Known Issues
1. Frontend Display Issues
   - Data not showing properly in UI
   - Crashes during analysis
   - Missing loading states
   - Incomplete error handling

2. API Integration
   - Response handling needs improvement
   - Better error management needed
   - Rate limiting implementation required

### Test Case
Main App:
```
https://play.google.com/store/apps/details?id=com.badhobuyer
```

Competitors:
```
https://play.google.com/store/apps/details?id=com.udaan.android
https://play.google.com/store/apps/details?id=club.kirana
```

## Next Steps

### Immediate Priorities
1. Fix Frontend Issues
   - Implement proper data handling
   - Add loading states
   - Improve error handling
   - Enhanced visualizations

2. Backend Enhancements
   - Optimize API responses
   - Add caching layer
   - Implement rate limiting
   - Improve error handling

3. New Features
   - Historical data tracking
   - Trend analysis
   - More detailed competitor insights
   - Advanced keyword suggestions

### Future Roadmap
1. Phase 1
   - Review sentiment analysis
   - Screenshot analysis
   - Character/word count tools

2. Phase 2
   - A/B testing support
   - Install tracking
   - Market trend analysis

3. Phase 3
   - User behavior analysis
   - Revenue estimation
   - Advanced performance metrics

## Development Setup

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Testing

### Backend Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_api_endpoints.py
```

### Frontend Tests
```bash
# Run tests
cd frontend
npm test
```

## API Documentation

### App Analysis
```python
GET /api/analyze/app/{app_id}
Response:
{
    "status": "success",
    "data": {
        "title": "App Title",
        "installs": "1,000,000+",
        "score": 4.5,
        "reviews": 10000,
        ...
    }
}
```

### Competitor Analysis
```python
POST /api/analyze/competitors/compare
Request:
{
    "app_id": "com.example.app",
    "competitor_ids": ["com.competitor1", "com.competitor2"]
}
Response:
{
    "status": "success",
    "comparison": {
        "main_app": {...},
        "competitors": [...],
        "metrics_comparison": {...}
    }
}
```

### Keyword Analysis
```python
POST /api/analyze/keywords/discover
Request:
{
    "app_id": "com.example.app",
    "competitor_ids": ["com.competitor1"]
}
Response:
{
    "status": "success",
    "analysis": {
        "common_keywords": [...],
        "unique_keywords": [...],
        "keyword_trends": {...}
    }
}
```

## Contributing

### Branch Strategy
- main: Production branch
- develop: Development branch
- feature/*: Feature branches
- fix/*: Bug fix branches

### Pull Request Process
1. Create feature/fix branch
2. Implement changes
3. Add tests
4. Create pull request
5. Code review
6. Merge to develop

## Support

### Common Issues
1. Frontend not displaying data
   - Check API responses
   - Verify data structure
   - Check console for errors

2. Analysis crashes
   - Implement error boundaries
   - Add loading states
   - Handle API errors

### Troubleshooting
1. Backend Issues
   - Check server logs
   - Verify API endpoints
   - Test database connection

2. Frontend Issues
   - Check browser console
   - Verify API calls
   - Test component rendering