#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Installing NLTK data..."
python3 -m nltk.downloader punkt vader_lexicon

echo "🔧 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

echo "📦 Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "📂 Setting up static files..."
mkdir -p app/static
cp -r frontend/dist/* app/static/

echo "✅ Build completed successfully!"