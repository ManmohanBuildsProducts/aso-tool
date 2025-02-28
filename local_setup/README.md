# Local Setup Instructions

1. Make sure you have Docker and Docker Compose installed:
   ```bash
   docker --version
   docker-compose --version
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. Check if services are running:
   ```bash
   docker-compose ps
   ```

4. View logs:
   ```bash
   docker-compose logs -f backend
   ```

5. Stop services:
   ```bash
   docker-compose down
   ```

## Testing the API

1. Check if API is running:
   ```bash
   curl http://localhost:8000/
   ```

2. Add your app:
   ```bash
   curl -X POST "http://localhost:8000/apps/" \
        -H "Content-Type: application/json" \
        -d '{
          "package_name": "com.badhobuyer",
          "name": "BadhoBuyer",
          "is_competitor": false
        }'
   ```

3. Add a competitor:
   ```bash
   curl -X POST "http://localhost:8000/apps/" \
        -H "Content-Type: application/json" \
        -d '{
          "package_name": "club.kirana",
          "name": "Kirana Club",
          "is_competitor": true
        }'
   ```

4. Analyze keywords:
   ```bash
   curl "http://localhost:8000/analyze/keywords?keywords=b2b%20wholesale,kirana%20store"
   ```

5. Get keyword suggestions:
   ```bash
   curl "http://localhost:8000/keywords/suggest/b2b%20wholesale"
   ```

## Troubleshooting

1. If MongoDB connection fails:
   ```bash
   docker-compose restart mongodb
   ```

2. If backend fails to start:
   ```bash
   docker-compose logs backend
   ```

3. To rebuild services:
   ```bash
   docker-compose build --no-cache
   ```

4. To reset everything:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```