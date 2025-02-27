#!/usr/bin/env bash
set -o errexit

echo "🔧 Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Installing NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"

echo "✅ Build completed!"