# ASO Tool - App Store Optimization Analyzer

A tool for analyzing and optimizing app store rankings, with a focus on B2B and wholesale applications.

## Features

- Keyword ranking analysis
- Competitor tracking
- ASO recommendations
- B2B-specific insights
- Real-time keyword suggestions

## Local Setup

1. Prerequisites:
   - Docker
   - Docker Compose

2. Installation:
   ```bash
   # Clone the repository
   git clone https://github.com/ManmohanBuildsProducts/aso-tool.git
   cd aso-tool

   # Start the services
   docker-compose up -d
   ```

3. Access:
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

### Keyword Analysis
- `GET /analyze/keywords?keywords=keyword1,keyword2`
  - Analyze multiple keywords

### Keyword Suggestions
- `GET /keywords/suggest/{base_keyword}`
  - Get keyword suggestions based on a base keyword

### Keyword Categories
- `GET /keywords/categories`
  - Get all keyword categories and their keywords

### App Analysis
- `GET /analyze/app/{app_id}`
  - Get comprehensive ASO analysis for an app

### Competitor Analysis
- `GET /analyze/competitors/{app_id}`
  - Get competitor analysis for an app

### Rankings
- `GET /rankings/history/{app_id}`
  - Get ranking history for an app
- `POST /rankings/check`
  - Force an immediate ranking check

## Example Usage

1. Add an app:
```bash
curl -X POST "http://localhost:8000/apps/" \
     -H "Content-Type: application/json" \
     -d '{
       "package_name": "com.example.app",
       "name": "Example App",
       "is_competitor": false
     }'
```

2. Analyze keywords:
```bash
curl "http://localhost:8000/analyze/keywords?keywords=b2b,wholesale,distributor"
```

3. Get keyword suggestions:
```bash
curl "http://localhost:8000/keywords/suggest/b2b%20wholesale"
```

## Development

1. Run tests:
```bash
docker-compose exec backend poetry run pytest
```

2. Check logs:
```bash
docker-compose logs -f backend
```

3. Access MongoDB:
```bash
docker-compose exec mongodb mongosh
```