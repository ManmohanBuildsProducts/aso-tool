# Local Installation Instructions

1. Prerequisites:
   - Python 3.11 or higher
   - Node.js 20 or higher
   - Git

2. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd aso-tool
   ```

3. Set up Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Set up Frontend:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. Access the application:
   - Open your browser and go to http://localhost:8000

## Development

1. Start frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Start backend development server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## File Structure

```
aso-tool/
├── app/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   └── core/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── __tests__/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Configuration

1. Environment Variables:
   Create a `.env` file in the root directory:
   ```
   DEBUG=True
   API_KEY=your_api_key
   ```

2. Frontend Configuration:
   The frontend is configured to proxy API requests to the backend server.
   See `frontend/vite.config.js` for details.

## Testing

1. Run backend tests:
   ```bash
   python -m pytest tests/
   ```

2. Run frontend tests:
   ```bash
   cd frontend
   npm test
   ```

## Common Issues

1. Port already in use:
   ```bash
   lsof -i :8000  # Find process using port 8000
   kill -9 <PID>  # Kill the process
   ```

2. Frontend build issues:
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   npm run build
   ```

3. Python dependency issues:
   ```bash
   pip install --upgrade -r requirements.txt
   ```