#!/bin/bash
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setting up Node.js..."
# Download and extract Node.js binary
curl -o nodejs.tar.xz https://nodejs.org/dist/v20.11.1/node-v20.11.1-linux-x64.tar.xz
mkdir -p nodejs
tar -xf nodejs.tar.xz -C nodejs --strip-components=1
export PATH=$PATH:$(pwd)/nodejs/bin

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