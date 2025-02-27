#!/bin/bash
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setting up Node.js..."
# Download and extract Node.js binary
curl -fsSL https://deb.nodesource.com/setup_20.0.0 | bash -
apt-get install -y nodejs
npm install -g npm@latest

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Building frontend..."
npm run build
cd ..

echo "Creating data directories..."
mkdir -p data/historical data/metadata_history

echo "Setting permissions..."
chmod -R 755 data

echo "Build completed successfully!"