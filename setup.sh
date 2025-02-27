#!/bin/bash

# Create directory structure
mkdir -p app/app frontend tests data app/app/routers app/app/services app/app/core

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn google-play-scraper pydantic python-dotenv requests beautifulsoup4 pandas nltk scikit-learn matplotlib seaborn textblob pytest pytest-asyncio httpx

# Initialize Node.js project in frontend directory
cd frontend
npm init -y
npm install @emotion/react @emotion/styled @mui/icons-material @mui/material react react-dom recharts axios
npm install --save-dev @vitejs/plugin-react vite @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom @babel/preset-react @babel/preset-env

# Create necessary directories for frontend
mkdir -p src/components src/__tests__ public

# Go back to root directory
cd ..

# Download all the source files
# Note: You'll need to replace these with actual file downloads or content creation

echo "Setup complete! Next steps:
1. Add source files
2. Build frontend: cd frontend && npm run build
3. Start server: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"